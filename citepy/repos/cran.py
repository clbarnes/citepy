import datetime as dt
import logging
from typing import DefaultDict, Dict, Tuple, List
from collections import defaultdict

import httpx
from bs4 import BeautifulSoup

from ..classes import CslItem, CslType, CslName
from .common import KNOWN_SITES as common_known, get_publisher, DataFetcher

KNOWN_SITES = common_known.copy()
KNOWN_SITES.update({"cran": "The Comprehensive R Archive Network"})

logger = logging.getLogger(__name__)


def remove_brackets(s):
    letters = []
    levels = {"[": 0, "(": 0, "<": 0}
    partners = {"]": "[", ")": "(", ">": "<"}
    skip = False

    for c in s:
        if c in levels:
            levels[c] += 1
            skip = True
        elif c in partners:
            partner = partners[c]
            levels[partner] -= 1
            if sum(levels.values()) == 0:
                skip = False
        elif not skip:
            letters.append(c)

    return "".join(letters)


class CranDataFetcher(DataFetcher):
    base_url = "https://CRAN.R-project.org"

    def __init__(self, client: httpx.AsyncClient) -> None:
        super().__init__(client)

    def get_authors(self, info) -> List[CslName]:
        authors: DefaultDict[CslName, int] = defaultdict(lambda: 0)
        for k in ("Author", "Maintainer"):
            val = info.get(k)
            if not val:
                continue
            for s in remove_brackets(val).split(","):
                authors[CslName(literal=s.strip())] += 1
        return list(authors.keys())

    def parse_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        out = dict()

        for table in soup.find_all("table"):
            if not table.get("summary", "").endswith("summary"):
                continue
            for row in table.find_all("tr"):
                key, value = list(row.find_all("td"))
                out[key.string.strip().rstrip(":")] = value.get_text(" ", strip=True)

        return out

    def parse_title_abstract(self, soup: BeautifulSoup) -> Tuple[str, str]:
        title = soup.find("h2").get_text(" ", strip=True)
        abstract = soup.find("p").get_text(" ", strip=True)
        return title.strip(), " ".join(abstract.strip().split())

    async def get(self, package, version=None, date_accessed=None) -> CslItem:
        url = self.base_url + "/package=" + package

        logger.debug("Fetching information from %s", url)

        response = await self.client.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        title, abstract = self.parse_title_abstract(soup)
        info = self.parse_metadata(soup)

        info_version = info["Version"]
        if version and version != info["Version"]:
            logger.warning(
                "Using metadata for version '%s' not requested '%s'",
                info_version,
                version
            )

        info_url = info.get("URL", url)

        return CslItem(
            type=CslType.WEBPAGE,
            id=package,
            author=self.get_authors(info),
            URL=info_url,
            abstract=abstract or None,
            version=version or info_version,
            issued=dt.datetime.strptime(info["Published"], "%Y-%m-%d").date(),
            accessed=date_accessed,
            categories=["software", "R", "libraries"],
            publisher=get_publisher(info_url),
            title=title,
        )
