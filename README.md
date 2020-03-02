# citepy

Python 3.7+

Easily cite software libraries using information from automatically gathered from their package repository.

## Installation

For installing python-based system tools, I recommend [pipx](https://pipxproject.github.io/pipx/).
With pipx installed:

```sh
pipx install citepy
```

If you only have pip available:

```bash
pip install --user citepy
```

## Usage

```help
usage: citepy [-h] [--all] [--repo {pypi,crates}] [--output OUTPUT]
              [--format FORMAT] [--threads THREADS] [--verbose]
              [--version VERSION]
              [package [package ...]]

positional arguments:
  package               names of python packages you want to cite, optionally
                        with (full) version string. e.g. numpy==1.16.3
                        beautifulsoup4==4.7.1

optional arguments:
  -h, --help            show this help message and exit
  --all, -a             if set, will get information for all python packages
                        accessible to `pip freeze`
  --repo {pypi,crates}, -r {pypi,crates}
                        which package repository to use (default pypi)
  --output OUTPUT, -o OUTPUT
                        path to write output to (default write to stdout)
  --format FORMAT, -f FORMAT
                        format to write out (default json)
  --threads THREADS, -t THREADS
                        how many threads to use to fetch data
  --verbose, -v         Increase verbosity of logging (can be repeated). One
                        for DEBUG, two for NOTSET, three includes all library
                        logging.
  --version VERSION     print version information and exit
```

### Supported package repos

- PyPI
- crates.io

### Supported output formats

- CSL-data JSON

CSL-data can be converted into bibtex, HTML, or a plaintext bibliography using another tool, e.g. [citation-js](https://github.com/larsgw/citation.js/).

## Example

To get a CSL-data JSON representation of the citation information of this package:

```sh
citepy citepy
```

```json
[
  {
    "URL": "https://www.github.com/clbarnes/citepy",
    "abstract": "Automatically create citations for packages",
    "accessed": {
      "date-parts": [
        [
          2020,
          3,
          2
        ]
      ]
    },
    "author": [
      {
        "literal": "Chris L. Barnes"
      }
    ],
    "categories": [
      "software",
      "python",
      "libraries",
      "pypi"
    ],
    "id": "citepy",
    "issued": {
      "date-parts": [
        [
          2019,
          5,
          28
        ]
      ]
    },
    "original-date": {
      "date-parts": [
        [
          2019,
          5,
          25
        ]
      ]
    },
    "publisher": "GitHub",
    "title": "citepy",
    "type": "webpage",
    "version": "0.2.3"
  }
]
```

## Limitations

- Author names are not parsed, and are therefore taken as literals
- If the package has its own citation information (as numpy, scipy, astropy etc do), citepy will not pick it up - it just uses the package publication metadata
- Software libraries do not fit into the CSL or bibtex categories very well, and so are cited as the web pages which host them
