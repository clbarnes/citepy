readme: install-dev
	citepy --help | pipe2codeblock --tgt help README.md && \
	citepy --date-accessed 2063-04-05 citepy | pipe2codeblock --tgt json README.md

install-dev:
	pip install -e .

fmt:
	black .

lint:
	flake8 .
	black --check .
	# mypy --ignore-missing-imports .
