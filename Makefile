SRC = $(shell find -name '*\.py')

.PHONY: all
all: typecheck wheel docs

README.md: README.md.in Makefile $(SRC)
	codebraid pandoc \
		-f markdown -t markdown --no-cache --overwrite --standalone \
		--self-contained -t gfm -o $@ $<

README-RU.md: README-RU.md.in Makefile $(SRC)
	codebraid pandoc \
		-f markdown -t markdown --no-cache --overwrite --standalone \
		--self-contained -t gfm -o $@ $<

.PHONY: tc typecheck
tc: typecheck
typecheck:
	pytest --mypy -m mypy

.PHONY: docs
docs: README.md README-RU.md

.PHONY: wheel
wheel: Makefile $(SRC)
	python3 setup.py sdist bdist_wheel --universal

