readme: install-dev
	citepy --help | pipe2codeblock --tgt help README.md && \
	citepy citepy | pipe2codeblock --tgt json README.md

install-dev:
	pip install -e .

fmt:
	black .

lint:
	flake8 .
	black --check .
	# mypy --ignore-missing-imports .
