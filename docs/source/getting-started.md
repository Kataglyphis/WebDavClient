# Getting started

The package talks to a remote host over the WebDAV protocol, for example to automate
downloads from your cloud. The API is [webdavclient.rst](webdavclient.rst); how to
contribute to any of the family's repositories is ANTfrastructure's
[`repository-family.md`](https://github.com/Kataglyphis/ANTfrastructure/blob/develop/docs/repository-family.md).

## Installation

**From a release** (since v0.10.0): every [release](https://github.com/Kataglyphis/WebDavClient/releases/latest)
carries wheels for Linux x64/arm64 and Windows x64/arm64 (the pinned CPython, with and without the
GIL: cp314 and cp314t in v0.10.1; Windows arm64 since v0.10.1), a
pure-Python wheel that installs anywhere, the sdist and a `SHA256SUMS`. Download the wheel for your
platform and `SHA256SUMS`, then:

```sh
sha256sum --check --ignore-missing SHA256SUMS
pip install ./kataglyphis_webdavclient-*.whl
```

**From source:**

```sh
git clone --recurse-submodules https://github.com/Kataglyphis/WebDavClient.git
cd WebDavClient
uv sync --all-extras --python 3.15   # the pinned CPython; 3.15t for the free-threaded build
```

## Dependencies

Python ≥ 3.10 (`requires-python` in `pyproject.toml`), managed with
[uv](https://docs.astral.sh/uv/). Develop on the pinned CPython, `PYTHON_VERSION` in
`third_party/ANTfrastructure/linux/scripts/01-core/versions.env`: nothing in the repo picks it,
so `uv sync` takes `--python`. The dependencies are declared in `pyproject.toml` (the
runtime set plus the `tests` and `docs` extras) and locked in `uv.lock`.

## Usage

The usage example is the README's [Quick start](README.md#quick-start).
`download_all_files_iterative` downloads everything below the remote path into the local one,
keeping the folder structure, and returns the number of downloaded files. Pass
`extension=".md"` to download only that suffix, case-insensitively. `download_files` accepts
the same option for one directory. Both use the same atomic file writer: an interrupted
transfer removes its partial file and preserves an existing destination.

HTTP and listing failures raise errors; unsafe decoded paths raise `ValueError`. The client
rejects remote paths outside the requested tree, parent segments, Windows drives, UNC/alternate
stream syntax, reserved names and existing symlinks that resolve outside the local root. Remote
URLs must use the configured server's origin. PROPFIND and GET responses close on success and
failure. Callers should handle errors explicitly and retry the operation when appropriate.

Creating a `WebDavClient` also creates `logs/` in the current
working directory and logs to `logs/downloadMd_s.log` there. `demo/download_markdown_files.py`
is the same example as a command-line script:

```sh
uv run python demo/download_markdown_files.py <hostname> <username> <password> <remote_base_path> <local_base_path>
```

## Tests

Run pytest in the root directory (`uv run pytest` after the sync above).
The WebDAV tests start a local mock server over `tests/remote/`, so no remote
host is needed. Every CI lane runs the whole suite on the pinned CPython (ANTfrastructure's
`PYTHON_VERSION`), once with the GIL and once free-threaded, and packages that X.Y's wheels:

| Lane | Python | Set by |
| --- | --- | --- |
| Linux x64, arm64 | the image's X.Y and X.Yt: 3.14 and 3.14t in `:latest` (2026-10-19), 3.15 after its rebuild | the hub's default, no version named |
| Windows x64 | 3.15 and 3.15t, the `:winamd64` image's | `PythonVersions = 'pinned pinnedt'` in `scripts/windows/python-ci.psd1` |
| Windows arm64 | 3.15 and 3.15t, installed by uv on the runner | `arm64-python-versions: 'pinned pinnedt'` in `.github/workflows/windows-arm64.yml` |

## Building wheels

`CYTHONIZE=1` enables the compiled wheel. `setup.py` delegates its archive rewrite to
`build_support/kataglyphis_wheel.py`, copied from ANTfrastructure's shared Python helper and
checked by `.antfrastructure-shared.manifest`. Update the upstream helper and copy it back;
project metadata and compiler options remain in `setup.py`.

`MANIFEST.in` includes the helper in the source distribution, so rebuilding an sdist needs no
submodule or hub import. The rewrite removes sources and invalidated signatures, compresses
retained entries and rebuilds their `RECORD` hashes before replacing the wheel atomically.

The installed-wheel suite copies `setup.py` and the rewriter alongside its tests so the
archive regression exercises the build class there too. It copies no package sources;
the compiled-module assertions still check imports from the installed wheel.

## Static analysis

```bash
./scripts/linux/ci_static_analysis.sh x64 > "ci_analysis_$(date +%Y%m%d_%H%M%S).log" 2>&1
```

The argument is the architecture; it runs on the pinned X.Y. It is the CI gate and exits
non-zero on a finding, which the redirect hides
([ANTfrastructure `python-ci.md`](https://github.com/Kataglyphis/ANTfrastructure/blob/develop/docs/python-ci.md#working-on-a-python-consumer-locally): the hook, the gate, binary-only wheels, the tools). The
other CI scripts are in [`AGENTS.md` § 4](https://github.com/Kataglyphis/WebDavClient/blob/develop/AGENTS.md#4-build-run-test).

## Literature

* <https://de.wikipedia.org/wiki/WebDAV>
