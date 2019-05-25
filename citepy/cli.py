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

from citepy.classes import CslItem

logger = logging.getLogger(__name__)


def get_all_versions():
    return dict(line.strip().split('==') for line in freeze.freeze())


def get_versions(*packages, version=None):
    versions = get_all_versions()
    return {p: version if version else versions.get(p) for p in packages}


def setup_logging(level=logging.DEBUG):
    logging.getLogger('pip').setLevel(logging.INFO)
    logging.getLogger('urllib3').setLevel(logging.INFO)
    logging.getLogger('websockets').setLevel(logging.INFO)
    logging.getLogger('pyppeteer').setLevel(logging.INFO)
    logging.basicConfig(level=level)


def get_threaded(fn, package_versions, max_threads):
    threads = min(len(package_versions), max_threads)
    futs: List[Tuple[str, Future]] = []
    with ThreadPoolExecutor(max_workers=threads) as exe:
        for package, version in package_versions:
            fut = exe.submit(fn, package, version)
            futs.append((package, fut))

        out: List[CslItem] = []
        fut: Future
        for package, fut in futs:
            try:
                out.append(fut.result())
            except Exception as e:
                logger.exception(
                    "Could not get citation for package {%s}\n" + textwrap.indent(str(e), ' ' * 4),package
                )
    return out


def get_serial(fn, package_versions):
    out = []
    for package, version in package_versions:
        try:
            out.append(fn(package, version))
        except Exception as e:
            logger.exception(
                "Could not get citation for package {%s}\n" + textwrap.indent(str(e), ' ' * 4), package
            )
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("package", nargs='*', help="names of python packages you want to cite")
    parser.add_argument(
        "--all", "-a", action="store_true",
        help="if set, will get information for all python packages accessible to `pip freeze`"
    )
    parser.add_argument("--repo", default="pypi", help="which package repository to use (default pypi)")
    parser.add_argument(
        "--with_version", "-w", help="fetch data for a specific version, not what is currently installed"
    )
    parser.add_argument("--output", "-o", help="path to write output to (default write to stdout)")
    parser.add_argument("--format", "-f", default="json", help="format to write out (default json)")
    parser.add_argument("--threads", "-t", default=5, help="how many threads to use to fetch data")

    parsed = parser.parse_args()

    setup_logging()

    mod = importlib.import_module("citepy.repos." + parsed.repo)

    versions = get_all_versions()
    packages = list(versions) if parsed.all else parsed.package

    package_versions = [(p, parsed.with_version or versions.get(p)) for p in packages]

    if parsed.repo.lower() == "pypi":
        csl_items = get_threaded(mod.get, package_versions, parsed.threads)
    else:
        csl_items = get_serial(mod.get, package_versions)

    if parsed.format.lower() == "json":
        s = json.dumps([item.to_jso() for item in csl_items], indent=2, sort_keys=True)
    else:
        raise ValueError(f"Unrecognised output format '{parsed.format}'")

    if parsed.output:
        with open(parsed.output, 'w') as f:
            f.write(s)
    else:
        print(s)

    sys.exit(0)


if __name__ == '__main__':
    main()
