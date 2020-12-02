from .common import DataFetcher
from .pypi import PypiDataFetcher
from .crates import CratesDataFetcher


KNOWN_FETCHERS = {
    "pypi": PypiDataFetcher,
    "crates": CratesDataFetcher,
}

__all__ = ["PypiDataFetcher", "CratesDataFetcher", "KNOWN_FETCHERS", "DataFetcher"]
