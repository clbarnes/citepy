import httpx
from datetime import datetime
import logging

from citepy.repos.common import DataFetcher, KNOWN_SITES as common_known, get_publisher
from citepy.classes import CslItem, CslType, CslName


KNOWN_SITES = common_known.copy()
KNOWN_SITES.update({"crates.io": "Crates.io", "docs.rs": "Docs.rs"})


logger = logging.getLogger(__name__)


class CratesDataFetcher(DataFetcher):
    base_url = "https://www.crates.io"

    async def get_date_author(self, version_dict):
        issued = datetime.fromisoformat(version_dict["created_at"])

        authors_url = self.base_url + version_dict["links"]["authors"]
        author_response = await self.client.get(authors_url)
        author_response.raise_for_status()
        names = author_response.json()["meta"]["names"]
        return issued, [CslName(literal=name) for name in names]

    async def get(self, package, version=None) -> CslItem:
        api_url = self.base_url + "/api/v1/crates/" + package

        logger.debug("Fetching information from %s", api_url)

        response = await self.client.get(api_url)
        response.raise_for_status()
        data = response.json()
        crate_data = data["crate"]

        categories = ["software", "rust", "libraries", "crates"]
        categories.extend(crate_data.get("keywords", []))
        categories.extend(crate_data.get("categories", []))

        item_url = crate_data.get("homepage")

        if item_url is None:
            item_url = "/".join([self.base_url, "crates", package])
            if version:
                item_url += "/" + version

        if not version:
            version = crate_data["max_version"]

        original_authors = None
        issued = None
        authors = None

        for idx, v_dict in enumerate(data["versions"]):
            if idx == len(data["versions"]) - 1:
                _, original_authors = await self.get_date_author(v_dict)

            if v_dict["num"] == version:
                issued, authors = await self.get_date_author(v_dict)

        return CslItem(
            type=CslType.WEBPAGE,
            id=package,
            abstract=data.get("description", ""),
            author=authors,
            URL=item_url,
            version=version,
            issued=issued,
            original_author=original_authors,
            original_date=datetime.fromisoformat(crate_data["created_at"]),
            accessed=datetime.utcnow(),
            categories=categories,
            publisher=get_publisher(item_url, KNOWN_SITES),
            title=crate_data.get("name", package),
        )
