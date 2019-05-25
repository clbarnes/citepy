import requests_html
from datetime import date, datetime
import logging

from citepy.classes import CslItem, CslType, CslName


logger = logging.getLogger(__name__)


base_url = 'https://www.crates.io/crates/'


months = dict(enumerate([
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
], 1))


def get_version_dates(page, version):
    this = None
    dt = None
    for row in page.find('#crate-all-versions > div.row'):
        this_version = row.find('a', first=True).text
        date_str = row.find('span', first=True).text

        month_str, day_str, year_str = date_str.split()
        month = months[month_str]
        day = int(date_str.rstrip(','))
        year = int(year_str)
        dt = date(year, month, day)

        if version == this_version:
            this = dt

    return dt or this, this


def get(package, version=None) -> CslItem:
    raise NotImplementedError("crates.io not fully implemented yet")
    pkg_url = base_url + '/' + package
    url = pkg_url + '/' + version if version else pkg_url

    logger.debug("Fetching information from %s", url)

    session = requests_html.HTMLSession()
    page = session.get(url)
    page.render()

    heading = page.find('#crates-heading', first=True)
    if not version:
        version = heading.find('h2', first=True).text

    authors = []
    for author_elem in page.find('div.authors > ul > li'):
        authors.append(CslName(literal=author_elem.text))

    original_date, issued = get_version_dates(session.get(pkg_url + '/versions').html, version)

    info_url = None
    for anchor in heading.find('.quick-links > ul > li > a'):
        if anchor.text.lower() == "homepage":
            info_url = anchor.attrs["href"]
            break

    categories = []
    for kw in page.find('ul.keywords > li > a'):
        categories.append(kw.text)
    for cat in page.find('ul.categories > ul > li'):
        categories.append(cat.text)

    return CslItem(
        type=CslType.WEBPAGE,
        id=package,
        author=authors,
        URL=info_url or pkg_url,
        version=version,
        issued=issued,
        original_date=original_date,
        accessed=datetime.utcnow(),
        categories=["software", "rust", "libraries", "crates"] + categories,
        publisher="The Python Package Index",
        title=package
    )
