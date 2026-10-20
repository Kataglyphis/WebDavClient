# Minimal makefile for Sphinx documentation

# Overridable from the command line; the first two also from the environment.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build
# Not a uv path source: that would fail every --locked sync of a checkout without this submodule.
THEME         = ../third_party/ANTfrastructure/third_party/DocumANTation/sphinx-kataglyphis-theme

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# The family theme, editable into the active venv; its dependencies are the docs extra's.
theme:
	uv pip install --quiet --no-deps -e "$(THEME)"

# The root README.md and CHANGELOG.md are the one source; the pages are untracked copies.
sources:
	cp ../README.md ../CHANGELOG.md "$(SOURCEDIR)/"

.PHONY: help theme sources Makefile

# Route every unknown target to Sphinx's "make mode"; $(O) is a shortcut for $(SPHINXOPTS).
%: Makefile theme sources
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
