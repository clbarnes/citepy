from urllib.parse import urlparse

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
