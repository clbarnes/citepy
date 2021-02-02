#!/usr/bin/env python3
from pathlib import Path

from setuptools import setup

here = Path(__file__).absolute().parent

with open(here / "README.md") as f:
    long_description = f.read()

setup(
    name="citepy",
    packages=["citepy", "citepy.repos"],
    url="https://www.github.com/clbarnes/citepy",
    license="MIT",
    author="Chris L. Barnes",
    author_email="cbarnes@mrc-lmb.cam.ac.uk",
    description="Automatically create citations for packages",
    install_requires=["jsonschema", "httpx"],
    package_data={"citepy": ["csl-data.json"]},
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.7,<4",
    entry_points={
        "console_scripts": ["citepy = citepy.cli:main", "cite = citepy.cli:main"]
    },
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
)
