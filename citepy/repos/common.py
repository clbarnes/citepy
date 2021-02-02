from abc import ABC, abstractmethod
from urllib.parse import urlparse

import httpx

from ..classes import CslItem

KNOWN_SITES = {
    "github": "GitHub",
    "gitlab": "GitLab",
    "readthedocs": "ReadTheDocs",
    "bitbucket": "BitBucket",
    "joss": "The Journal of Open Source Software",
    "zenodo": "Zenodo",
}


def get_publisher(url, known_sites=None):
    if known_sites is None:
        known_sites = KNOWN_SITES.copy()

    netloc = urlparse(url)[1]
    for key, val in known_sites.items():
        if key in netloc.lower():
            return val

    netloc = netloc.split(":")[0]
    if netloc.startswith("www"):
        netloc = ".".join(netloc.split(".")[1:])
    return netloc


class DataFetcher(ABC):
    base_url: str

    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client

    @abstractmethod
    async def get(self, package, version=None) -> CslItem:
        pass
