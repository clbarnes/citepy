readme:
	citepy --help | pipe2codeblock --tgt help README.md && \
	citepy citepy | pipe2codeblock --tgt json README.md
