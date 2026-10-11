# Copyright (c) 2026 Jonas Heinle

"""On a free-threaded interpreter the package must leave the GIL off; with KATAGLYPHIS_EXPECT_COMPILED=1, as compiled modules."""

import importlib
import importlib.machinery
import os
import sys
import sysconfig

import pytest


MODULES = (
    "kataglyphis_webdavclient",
    "kataglyphis_webdavclient.webdavclient",
    "kataglyphis_webdavclient.dummy",
)


@pytest.mark.skipif(
    not sysconfig.get_config_var("Py_GIL_DISABLED"),
    reason="needs a free-threaded interpreter",
)
def test_importing_the_package_keeps_the_gil_disabled() -> None:
    """A module without freethreading_compatible, or a dependency without free-threading support, turns the GIL back on."""
    for name in MODULES:
        importlib.import_module(name)
    assert sys._is_gil_enabled() is False  # noqa: SLF001 -- the documented free-threading probe


@pytest.mark.skipif(
    os.environ.get("KATAGLYPHIS_EXPECT_COMPILED") != "1",
    reason="only the run against the installed binary wheel expects compiled modules",
)
def test_every_module_is_the_compiled_one() -> None:
    """A wheel test that silently imported the source tree would prove nothing about the Cython build."""
    suffixes = tuple(importlib.machinery.EXTENSION_SUFFIXES)
    for name in MODULES:
        path = importlib.import_module(name).__file__ or ""
        assert path.endswith(suffixes), (
            f"{name} came from {path}, not a compiled module"
        )
