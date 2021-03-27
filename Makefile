SRC = $(shell find -name '*\.py')

.PHONY: all
all: docs

README.md: README.md.in Makefile $(SRC)
	codebraid pandoc \
		-f markdown -t markdown --no-cache --overwrite --standalone \
		--self-contained -t gfm -o $@ $<

README-RU.md: README-RU.md.in Makefile $(SRC)
	codebraid pandoc \
		-f markdown -t markdown --no-cache --overwrite --standalone \
		--self-contained -t gfm -o $@ $<

.PHONY: docs
docs: README.md README-RU.md

