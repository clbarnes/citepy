import requests
from datetime import datetime
import logging

from citepy.classes import CslItem, CslType, CslName
from citepy.repos.common import KNOWN_SITES as common_known, get_publisher

KNOWN_SITES = common_known.copy()
KNOWN_SITES.update({"pypi": "The Python Package Index"})

logger = logging.getLogger(__name__)


base_url = "https://www.pypi.org/pypi"


def get_authors(info):
    author_str = info.get("author")
    maintainer_str = info.get("maintainer")

    authors = []

    if author_str:
        authors.append(CslName(literal=author_str))
    elif maintainer_str:
        authors.append(CslName(literal=maintainer_str))

    return authors


def get(package, version=None) -> CslItem:
    url = base_url + "/" + package
    if version:
        url += "/" + version
    url += "/" + "json"

    logger.debug("Fetching information from %s", url)

    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    logger.debug("Successfully parsed data")
    info = data["info"]

    release = data["releases"][info["version"]][0]
    dt = datetime.fromisoformat(release["upload_time"])

    first_upload = dt
    for release in data["releases"].values():
        for upload in release:
            first_upload = min(
                first_upload, datetime.fromisoformat(upload["upload_time"])
            )

    item_url = info.get("home_page") or info["project_url"]
    publisher = get_publisher(item_url, KNOWN_SITES)

    return CslItem(
        type=CslType.WEBPAGE,
        id=package,
        author=get_authors(info),
        URL=item_url,
        abstract=info["summary"] or None,
        version=info["version"],
        issued=dt,
        # event_date=dt,
        # container=dt,
        # submitted=dt,
        original_date=first_upload,
        accessed=datetime.utcnow(),
        categories=["software", "python", "libraries", "pypi"] + info["classifiers"],
        publisher=publisher,
        title=package,
    )
