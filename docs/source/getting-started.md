# Getting started

This module provides an easy interface for communication via the WebDAV protocol
to a remote host: you can, for example, automate downloads from your cloud. The
API itself is [webdavclient.rst](webdavclient.rst); how to contribute to any of the
family's repositories is ANTfrastructure's
[`repository-family.md`](https://github.com/Kataglyphis/ANTfrastructure/blob/develop/docs/repository-family.md).

## Installation

**From a release** (since v0.10.0): every [release](https://github.com/Kataglyphis/WebDavClient/releases/latest)
carries wheels for Linux x64/arm64 and Windows x64/arm64 (CPython 3.14, with and without the GIL; Windows
arm64 since v0.10.1), a
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
uv sync --all-extras --python 3.14
```

## Dependencies

Python ≥ 3.10 (`requires-python` in `pyproject.toml`), managed with
[uv](https://docs.astral.sh/uv/).

* Python dependencies are declared in `pyproject.toml` (the runtime set plus
  the `tests` and `docs` extras) and locked in `uv.lock`

## Usage

The usage example is the README's [Quick start](README.md#quick-start).
`download_all_files_iterative` downloads everything below the remote path into the local one,
keeping the folder structure. Creating a `WebDavClient` also creates `logs/` in the current
working directory and logs to `logs/downloadMd_s.log` there. `demo/download_markdown_files.py`
is the same example as a command-line script:

```sh
uv run python demo/download_markdown_files.py <hostname> <username> <password> <remote_base_path> <local_base_path>
```

## Tests

Run pytest in the root directory (`uv run pytest` after the sync above).
The WebDAV tests start a local mock server over `tests/remote/`, so no remote
host is needed. Every CI lane runs the whole suite, on 3.14 and the free-threaded 3.14t.

## Static analysis

```bash
./scripts/linux/ci_static_analysis.sh x64 3.14 > "ci_analysis_$(date +%Y%m%d_%H%M%S).log" 2>&1
```

The arguments are the architecture and the Python version. It is the CI gate and exits
non-zero on a finding, which the redirect hides
([ANTfrastructure `python-ci.md`](https://github.com/Kataglyphis/ANTfrastructure/blob/develop/docs/python-ci.md#working-on-a-python-consumer-locally): the hook, the gate, binary-only wheels, the tools). The
other CI scripts are in [`AGENTS.md` § 4](https://github.com/Kataglyphis/WebDavClient/blob/develop/AGENTS.md#4-build-run-test).

## Literature

Some very helpful literature, tutorials, etc.

* <https://de.wikipedia.org/wiki/WebDAV>
