import argparse
import importlib
import json
import sys
import logging
from concurrent.futures import Future
from concurrent.futures.thread import ThreadPoolExecutor
from typing import List, Tuple

from pip._internal.operations import freeze
import textwrap

from citepy import __version__
from citepy.classes import CslItem

logger = logging.getLogger(__name__)


SUPPORTED_REPOS = ["pypi", "crates"]


def get_pypi_versions():
    d = dict()
    for line in freeze.freeze():
        try:
            k, v = line.strip().split("==")
        except ValueError:
            continue
        d[k] = v
    return d


def get_versions(*packages, version=None):
    versions = get_pypi_versions()
    return {p: version if version else versions.get(p) for p in packages}


def setup_logging(verbosity):
    verbosity = verbosity or 0
    levels = [logging.INFO, logging.DEBUG, logging.NOTSET, logging.NOTSET]
    v_idx = min(verbosity, len(levels) - 1)

    logging.basicConfig(level=levels[v_idx])

    if v_idx > 2:
        logging.getLogger("pip").setLevel(logging.INFO)
        logging.getLogger("urllib3").setLevel(logging.INFO)
        logging.getLogger("websockets").setLevel(logging.INFO)
        logging.getLogger("pyppeteer").setLevel(logging.INFO)


def msg_template(e):
    return "Could not get citation for package '%s'\n" + textwrap.indent(
        str(e), " " * 4
    )


def get_threaded(fn, package_versions, max_threads):
    threads = min(len(package_versions), max_threads)
    futs: List[Tuple[str, Future]] = []
    with ThreadPoolExecutor(max_workers=threads) as exe:
        for package, version in package_versions.items():
            fut = exe.submit(fn, package, version)
            futs.append((package, fut))

        out: List[CslItem] = []
        fut: Future
        for package, fut in futs:
            try:
                out.append(fut.result())
            except Exception as e:
                logger.exception(msg_template(e), package)
    return out


def get_serial(fn, package_versions):
    out = []
    for package, version in package_versions:
        try:
            out.append(fn(package, version))
        except Exception as e:
            logger.exception(msg_template(e), package)
    return out


def split_package_versions(packages):
    for s in packages:
        pair = s.split("==")
        if len(pair) == 1:
            p = pair[0]
            v = None
        elif len(pair) == 2:
            p, v = pair
        else:
            raise ValueError(f"Could not parse '{s}'")
        yield p, v


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "package",
        nargs="*",
        help="names of python packages you want to cite, optionally with (full) version string. "
        "e.g. numpy==1.16.3 beautifulsoup4==4.7.1",
    )
    parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="if set, will get information for all python packages accessible to `pip freeze`",
    )
    parser.add_argument(
        "--repo",
        "-r",
        default="pypi",
        choices=SUPPORTED_REPOS,
        help="which package repository to use (default pypi)",
    )
    parser.add_argument(
        "--output", "-o", help="path to write output to (default write to stdout)"
    )
    parser.add_argument(
        "--format", "-f", default="json", help="format to write out (default json)"
    )
    parser.add_argument(
        "--threads", "-t", default=5, help="how many threads to use to fetch data"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        help="Increase verbosity of logging (can be repeated). "
        "One for DEBUG, two for NOTSET, three includes all library logging.",
    )
    parser.add_argument("--version", help="print version information and exit")

    parsed = parser.parse_args()

    setup_logging(parsed.verbose)

    if parsed.version:
        print(__version__)
        sys.exit(0)

    mod = importlib.import_module("citepy.repos." + parsed.repo)

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

    csl_items = get_threaded(mod.get, package_versions, parsed.threads)

    if parsed.format.lower() == "json":
        s = json.dumps([item.to_jso() for item in csl_items], indent=2, sort_keys=True)
    else:
        raise ValueError(f"Unrecognised output format '{parsed.format}'")

    if parsed.output:
        with open(parsed.output, "w") as f:
            f.write(s)
    else:
        print(s)

    sys.exit(0)


if __name__ == "__main__":
    main()
