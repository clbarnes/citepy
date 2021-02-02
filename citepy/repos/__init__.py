from typing import Dict, Type

from .common import DataFetcher
from .pypi import PypiDataFetcher
from .crates import CratesDataFetcher
from .cran import CranDataFetcher


KNOWN_FETCHERS: Dict[str, Type[DataFetcher]] = {
    "pypi": PypiDataFetcher,
    "crates": CratesDataFetcher,
    "cran": CranDataFetcher,
}

__all__ = [
    "PypiDataFetcher",
    "CratesDataFetcher",
    "CranDataFetcher",
    "KNOWN_FETCHERS",
    "DataFetcher",
]
