# citepy

Python 3.7+

Easily cite software packages using their package repository URL.

## Installation

```bash
pip install citepy
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

### Supported output formats

- CSL-data JSON

CSL-data can be converted into bibtex, HTML, or a plaintext bibliography using another tool, e.g. [citation-js](https://github.com/larsgw/citation.js/).
packages you want to cite

optional arguments:
  -h, --help            show this help message and exit
  --all, -a             if set, will get information for all python packages
                        accessible to `pip freeze`
  --repo REPO           which package repository to use (default pypi)
  --with_version WITH_VERSION, -w WITH_VERSION
                        fetch data for a specific version, not what is
                        currently installed
  --output OUTPUT, -o OUTPUT
                        path to write output to (default write to stdout)
  --format FORMAT, -f FORMAT
                        format to write out (default json)
  --threads THREADS, -t THREADS
                        how many threads to use to fetch data
```

### Supported package repos

- PyPI

### Supported output formats

- CSL-data JSON

CSL-data can be converted into bibtex, HTML, or a plaintext bibliography using another tool, e.g. [citation-js](https://github.com/larsgw/citation.js/).
