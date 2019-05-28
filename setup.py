from setuptools import setup
from pathlib import Path

here = Path(__file__).absolute().parent
package = here / "fran"

with open(here / "README.md") as f:
    long_description = f.read()

setup(
    name="citepy",
    version="0.2.2",
    packages=["citepy", "citepy.repos"],
    url="https://www.github.com/clbarnes/citepy",
    license="MIT",
    author="Chris L. Barnes",
    author_email="barnesc@janelia.hhmi.org",
    description="Automatically create citations for packages",
    install_requires=["jsonschema", "requests"],
    package_data={"citepy": ["csl-data.json"]},
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    entry_points={
        "console_scripts": ["citepy = citepy.cli:main", "cite = citepy.cli:main"]
    },
)
