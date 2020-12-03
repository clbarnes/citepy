from typing import Dict, Type

from .common import DataFetcher
from .pypi import PypiDataFetcher
from .crates import CratesDataFetcher


KNOWN_FETCHERS: Dict[str, Type[DataFetcher]] = {
    "pypi": PypiDataFetcher,
    "crates": CratesDataFetcher,
}

__all__ = ["PypiDataFetcher", "CratesDataFetcher", "KNOWN_FETCHERS", "DataFetcher"]
