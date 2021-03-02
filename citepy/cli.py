#!/usr/bin/env python
"""
Fetch citation data from software package repositories.
"""
import argparse
import json
import sys
import logging
from typing import Dict, Optional, Iterable
import re
from contextlib import contextmanager
from pip._internal.operations.freeze import freeze as pip_freeze
import asyncio
import datetime as dt
import os

import httpx

from . import __version__
from .repos import KNOWN_FETCHERS
from .classes import CslItem

logger = logging.getLogger(__name__)

DATE_ACCESSED_VAR = "CITEPY_DATE_ACCESSED"
DEFAULT_DATE_STR = os.environ.get(DATE_ACCESSED_VAR, dt.date.today().isoformat())
DEFAULT_DUMPER = "csl-json/pretty"


def get_pypi_versions() -> Dict[str, Optional[str]]:
    """Get versions from ``pip freeze``"""
    d = dict()
    for line in pip_freeze():
        try:
            k, v = line.strip().split("==")
        except ValueError:
            continue
        d[k] = v
    return d


def setup_logging(verbosity):
    verbosity = verbosity or 0
    levels = [
        logging.CRITICAL,
        logging.WARNING,
        logging.INFO,
        logging.DEBUG,
        logging.NOTSET,
    ]
    logging.basicConfig(level=levels[min(verbosity + 1, len(levels) - 1)])

    loud_level = levels[min(verbosity, len(levels) - 1)]
    for name in ["pip", "urllib3", "websockets"]:
        logging.getLogger(name).setLevel(loud_level)


name_re = re.compile(
    r"^(?P<name>(\w[\w\d\._-]*))\s*((?P<rel>[=><!~^]{1,2})\s*(?P<ver>[\d\.\*\w-]+))?$"
)


def split_package_versions(packages):
    for s in packages:
        s = s.strip()
        if s == "-":
            yield from split_package_versions(sys.stdin.readlines())
            continue

        m = name_re.match(s)
        if m is None:
            logger.warning("Could not parse '%s'; skipping", s)
            continue

        g = m.groupdict()
        name = g["name"]
        rel = g["rel"]
        ver = g["ver"]

        if rel:
            if set(rel) == {"="} and len(rel) <= 2:
                yield name, ver
                continue
            else:
                logger.warning(
                    f"Unsupported package-version relationship '{rel}'; "
                    "ignoring version"
                )
        yield name, None


async def get_info(
    package_versions: Dict[str, Optional[str]], repo: str, date: dt.date = None
):
    fetcher_cls = KNOWN_FETCHERS[repo]
    # sem = asyncio.Semaphore(jobs)
    futs = []
    async with httpx.AsyncClient() as c:
        fetcher = fetcher_cls(c)
        for k, v in package_versions.items():
            # async with sem:
            futs.append(fetcher.get(k, v, date))
        results = await asyncio.gather(*futs)
    return results


@contextmanager
def outfile(obj):
    if not obj or obj == "-":
        yield sys.stdout
    else:
        with open(obj, "w") as f:
            yield f


@contextmanager
def infile(obj):
    if not obj or obj == "-":
        yield sys.stdin
    else:
        with open(obj) as f:
            yield f


def parse_date(s: str) -> dt.date:
    datetime = dt.datetime.strptime(s, "%Y-%m-%d")
    return datetime.date()


def read_packages(args):
    if not args:
        return
    has_stdin = False
    for arg in args:
        if arg == "-":
            if has_stdin:
                continue
            else:
                has_stdin = True
        with infile(arg) as f:
            for line in f:
                stripped = line.strip()
                if not stripped or line.startswith("#"):
                    continue
                yield stripped


def dump_csl_json_lines(items: Iterable[CslItem], f):
    for item in items:
        print(json.dumps(item.to_jso(), sort_keys=True), file=f)


def dump_csl_json_pretty(items: Iterable[CslItem], f):
    json.dump([item.to_jso() for item in items], f, sort_keys=True, indent=2)
    f.write("\n")


def dump_csl_json_min(items: Iterable[CslItem], f):
    json.dump(
        [item.to_jso() for item in items], f, sort_keys=True, separators=(",", ":")
    )
    f.write("\n")


dumpers = {
    "csl-json/lines": dump_csl_json_lines,
    "csl-json/pretty": dump_csl_json_pretty,
    "csl-json/min": dump_csl_json_min,
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "package",
        nargs="*",
        help=(
            "names of packages you want to cite, "
            "optionally with (full) version string. "
            "e.g. 'numpy==1.16.3' 'beautifulsoup4==4.7.1' . "
            "Note that version strings are handled differently "
            "by different repositories, and may be ignored. "
            "In particular, any non-exact version constraint is ignored. "
            "'-' will read a newline-separated list from stdin."
        ),
    )
    parser.add_argument(
        "--all-python",
        "-a",
        action="store_true",
        help=(
            "if set, will get information for all python packages "
            "accessible to `pip freeze`"
        ),
    )
    parser.add_argument(
        "--repo",
        "-r",
        default="pypi",
        choices=sorted(KNOWN_FETCHERS),
        help="which package repository to use (default pypi)",
    )
    parser.add_argument(
        "--infile",
        "-i",
        action="append",
        help=(
            "path to read input packages from as newline-separated items "
            "(can be given multiple times; - reads from stdin)"
        ),
    )
    parser.add_argument(
        "--outfile",
        "-o",
        help="path to write output to (default or - writes to stdout)",
    )
    parser.add_argument(
        "--format",
        "-f",
        default=DEFAULT_DUMPER,
        choices=sorted(dumpers),
        help=f"format to write out (default '{DEFAULT_DUMPER}')",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        help="Increase verbosity of logging (can be repeated).",
    )
    parser.add_argument(
        "--date-accessed",
        "-d",
        type=parse_date,
        default=parse_date(DEFAULT_DATE_STR),
        help=(
            "Manually set access date, in format 'YYYY-MM-DD'. "
            f"Falls back to {DATE_ACCESSED_VAR} environment variable, "
            "then today's date."
        ),
    )
    parser.add_argument(
        "--version", action="store_true", help="print version information and exit"
    )

    parsed = parser.parse_args()

    setup_logging(parsed.verbose)

    if parsed.version:
        print(__version__)
        sys.exit(0)

    parsed.package.extend(read_packages(parsed.infile))

    if parsed.repo == "pypi":
        versions = get_pypi_versions()
        if parsed.package:
            package_versions = {
                p: v or versions.get(p)
                for p, v in split_package_versions(parsed.package)
            }
        else:
            package_versions = versions
    else:
        package_versions = dict(split_package_versions(parsed.package))

    csl_items = asyncio.run(
        get_info(package_versions, parsed.repo, parsed.date_accessed)
    )
    with outfile(parsed.outfile) as f:
        dumpers[parsed.format](csl_items, f)

    parser.exit(0)


if __name__ == "__main__":
    main()
