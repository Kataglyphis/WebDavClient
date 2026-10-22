# Copyright (c) 2024 Jonas Heinle

"""Build configuration for packaging and optional Cython compilation."""

import logging
import os
import runpy
import sys
from pathlib import Path

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext


rewrite_wheel = runpy.run_path(
    str(Path(__file__).parent / "build_support/kataglyphis_wheel.py")
)["rewrite_wheel"]

LOGGER = logging.getLogger(__name__)


try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
except Exception:
    _bdist_wheel = None

# Accept several truthy values for CYTHONIZE (so "True", True, "1", "true" all work)
CYTHONIZE_RAW = os.getenv("CYTHONIZE", "0")
CYTHONIZE = str(CYTHONIZE_RAW).strip().lower() in ("1", "true", "yes", "on")

if CYTHONIZE:
    from Cython.Build import cythonize

if sys.platform == "win32":
    os.environ["CC"] = "clang-cl"
    os.environ["CXX"] = "clang-cl"
    os.environ["DISTUTILS_USE_SDK"] = "1"
else:
    os.environ.pop("DISTUTILS_USE_SDK", None)
    os.environ.setdefault("CC", "clang")
    os.environ.setdefault("CXX", "clang")


class StripWheel(_bdist_wheel if _bdist_wheel is not None else object):
    """Build the wheel, then drop its source files and rewrite a valid .dist-info/RECORD."""

    exclude_suffixes = (".py", ".pyc", ".pyo", ".c", ".h", ".pxd", ".pyi")

    def run(self) -> None:
        """Build wheel artifacts and strip source files from resulting wheels."""
        if _bdist_wheel is not None:
            super().run()
        else:
            error_message = "wheel bdist_wheel not available; install 'wheel' package"
            raise RuntimeError(error_message)

        dist_dir = Path(getattr(self, "dist_dir", "dist"))
        for wheel_path in dist_dir.iterdir():
            if wheel_path.suffix != ".whl":
                continue
            self._strip_wheel(wheel_path)

    def _strip_wheel(self, wheel_path: Path) -> None:
        """Delegate the archive rewrite to the shared, sdist-bundled helper."""
        rewrite_wheel(wheel_path, self.exclude_suffixes)


class ClangBuildExt(build_ext):
    """Build extensions with clang-cl and lld-link in place of MSVC's cl and link."""

    def build_extension(self, ext: Extension) -> None:
        """Build one extension and map MSVC toolchain calls to LLVM binaries."""
        if self.compiler.compiler_type == "msvc":
            # The first compile() would initialize() and reset cc to cl.exe, so the first extension built with MSVC cl.
            if not getattr(self.compiler, "initialized", True):
                self.compiler.initialize(self.plat_name)

            if hasattr(self.compiler, "cc"):
                self.compiler.cc = "clang-cl"
            if hasattr(self.compiler, "linker_so"):
                self.compiler.linker_so = "lld-link"
            if hasattr(self.compiler, "linker"):
                self.compiler.linker = "lld-link"

        super().build_extension(ext)


package_dir = "kataglyphis_webdavclient"
version = Path("VERSION.txt").read_text().strip()


def list_py_files(package_dir: str) -> list[str]:
    """Return all Python module file paths under the package directory."""
    return [str(path) for path in Path(package_dir).rglob("*.py")]


py_files = list_py_files(package_dir)

extensions = []
if CYTHONIZE:
    if sys.platform == "win32":
        extra_compile_args = ["/O2", "/MD"]
        extra_link_args = ["/OPT:REF", "/OPT:ICF", "/LTCG:OFF"]
    else:
        extra_compile_args = ["-O3", "-flto", "-fvisibility=hidden"]
        extra_link_args = ["-flto"]

    extensions = [
        Extension(
            py_file.replace(os.path.sep, ".")[:-3],
            [py_file],
            extra_compile_args=extra_compile_args,
            extra_link_args=extra_link_args,
        )
        for py_file in py_files
    ]

setup_kwargs = {"name": package_dir, "version": version, "zip_safe": False}

if CYTHONIZE:
    cmds = {"build_ext": ClangBuildExt}
    if _bdist_wheel is not None:
        cmds["bdist_wheel"] = StripWheel
    setup_kwargs.update(
        {
            "ext_modules": cythonize(
                extensions,
                # A stale in-tree .c from an earlier build hid a changed directive; three modules regenerate in seconds.
                force=True,
                compiler_directives={
                    "language_level": "3",
                    "emit_code_comments": False,
                    "linetrace": False,
                    "embedsignature": False,
                    "binding": False,
                    "profile": False,
                    "annotation_typing": False,
                    "initializedcheck": False,
                    "warn.undeclared": False,
                    "infer_types": False,
                    # Else each module re-enables the GIL on 3.14t; the 3.14t legs test this code free-threaded.
                    "freethreading_compatible": True,
                },
            ),
            "cmdclass": cmds,
            "package_data": {"": ["*.c", "*.so", "*.pyd"]},
        }
    )
else:
    setup_kwargs.update({"packages": [package_dir], "include_package_data": True})

setup(**setup_kwargs)
