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
usage: citepy [-h] [--all-python] [--repo {cran,crates,pypi}]
              [--infile INFILE] [--outfile OUTFILE]
              [--format {csl-json/lines,csl-json/min,csl-json/pretty}]
              [--verbose] [--date-accessed DATE_ACCESSED] [--version]
              [package ...]

Fetch citation data from software package repositories.

positional arguments:
  package               names of packages you want to cite, optionally with
                        (full) version string. e.g. 'numpy==1.16.3'
                        'beautifulsoup4==4.7.1' . Note that version strings
                        are handled differently by different repositories, and
                        may be ignored. In particular, any non-exact version
                        constraint is ignored. '-' will read a newline-
                        separated list from stdin.

optional arguments:
  -h, --help            show this help message and exit
  --all-python, -a      if set, will get information for all python packages
                        accessible to `pip freeze`
  --repo {cran,crates,pypi}, -r {cran,crates,pypi}
                        which package repository to use (default pypi)
  --infile INFILE, -i INFILE
                        path to read input packages from as newline-separated
                        items (can be given multiple times; - reads from
                        stdin)
  --outfile OUTFILE, -o OUTFILE
                        path to write output to (default or - writes to
                        stdout)
  --format {csl-json/lines,csl-json/min,csl-json/pretty}, -f {csl-json/lines,csl-json/min,csl-json/pretty}
                        format to write out (default 'csl-json/pretty')
  --verbose, -v         Increase verbosity of logging (can be repeated).
  --date-accessed DATE_ACCESSED, -d DATE_ACCESSED
                        Manually set access date, in format 'YYYY-MM-DD'.
                        Falls back to CITEPY_DATE_ACCESSED environment
                        variable, then today's date.
  --version             print version information and exit
```

### Supported package repos

- PyPI (`pypi`)
- crates.io (`crates`)

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
          2063,
          4,
          5
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
          2021,
          2,
          2
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
    "version": "0.4.0"
  }
]
```

## Limitations

- Author names are not parsed, and are therefore taken as literals
    - This is a "wontfix". Author names *should* be literals. A huge amount of complexity is added to tools which attempt, and fail, to encode the complexity of different cultural conventions around handling names.
- If the package has its own citation information (as numpy, scipy, astropy etc do), citepy will not pick it up - it just uses the package publication metadata
- Software libraries do not fit into the CSL or bibtex categories very well, and so are cited as the web pages which host them

