# Copyright (c) 2024 Jonas Heinle

"""Sphinx configuration: the family theme's setup_theme(), as the hub's docs/conf.py calls it."""

from pathlib import Path

# docs/Makefile and make.bat install it from the theme package the hub vendors, before every build.
from sphinx_kataglyphis import setup_theme


PROJECT = "WebDavClient"
VERSION_FILE = Path(__file__).resolve().parents[2] / "VERSION.txt"

setup_theme(
    globals(),
    repository_url=f"https://github.com/Kataglyphis/{PROJECT}",
    project_name=PROJECT,
    copyright_="2024, Jonas Heinle",
    release=VERSION_FILE.read_text(encoding="utf-8").strip(),
    extensions_extra=[
        "sphinx.ext.autodoc",
        "sphinx.ext.napoleon",
        "sphinx.ext.viewcode",
    ],
    myst_enable_extensions=["dollarmath", "amsmath", "colon_fence", "deflist"],
)

# The repository's own logo, in place of setup_theme()'s shared default.
html_logo = "../../images/logo.svg"
html_favicon = html_logo
