SRC = $(shell find -name '*\.py')

README.md: README.md.in Makefile $(SRC)
	codebraid pandoc \
		-f markdown -t markdown --no-cache --overwrite --standalone \
		--self-contained -t gfm -o $@ $<
