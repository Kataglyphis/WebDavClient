<div align="center">
  <a href="https://jonasheinle.de">
    <img src="https://raw.githubusercontent.com/Kataglyphis/WebDavClient/develop/images/logo.svg" alt="WebDavClient logo: an ant carrying a file down from a cloud" width="200" />
  </a>

# WebDavClient

  <h4>Download files and folders from WebDAV storage.</h4>
</div>

[![Linux x64 · build + test](https://github.com/Kataglyphis/WebDavClient/actions/workflows/linux-x64.yml/badge.svg)](https://github.com/Kataglyphis/WebDavClient/actions/workflows/linux-x64.yml)
[![Linux arm64 · build + test](https://github.com/Kataglyphis/WebDavClient/actions/workflows/linux-arm64.yml/badge.svg)](https://github.com/Kataglyphis/WebDavClient/actions/workflows/linux-arm64.yml)
[![Windows x64 · build + test](https://github.com/Kataglyphis/WebDavClient/actions/workflows/windows-x64.yml/badge.svg)](https://github.com/Kataglyphis/WebDavClient/actions/workflows/windows-x64.yml)
[![Windows arm64 · test + wheels](https://github.com/Kataglyphis/WebDavClient/actions/workflows/windows-arm64.yml/badge.svg)](https://github.com/Kataglyphis/WebDavClient/actions/workflows/windows-arm64.yml)
[![Lint gates](https://github.com/Kataglyphis/WebDavClient/actions/workflows/lint-gates.yml/badge.svg)](https://github.com/Kataglyphis/WebDavClient/actions/workflows/lint-gates.yml)
[![CodeQL](https://github.com/Kataglyphis/WebDavClient/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/Kataglyphis/WebDavClient/actions/workflows/github-code-scanning/codeql)
[![TopLang](https://img.shields.io/github/languages/top/Kataglyphis/WebDavClient)](https://github.com/Kataglyphis/WebDavClient)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/paypalme/JonasHeinle)
[![Twitter](https://img.shields.io/twitter/follow/Cataglyphis_?style=social)](https://twitter.com/Cataglyphis_)
[![YouTube](https://img.shields.io/youtube/channel/subscribers/UC3LZiH4sZzzaVBCUV8knYeg?style=social)](https://www.youtube.com/channel/UC3LZiH4sZzzaVBCUV8knYeg)

[**Docs site**](https://webdavclient.jonasheinle.de/)

WebDavClient is a Python package that downloads files and folders from a WebDAV host. Use it to
communicate to a cloud storage provider (e.g. Nextcloud, ownCloud, Magenta, Synology NAS, QNAP
NAS) and automate your personal storage tasks, in CI for example. Other solutions on PyPI did
not fit my needs and/or were not actively maintained.

## Highlights

- **Downloads a whole remote folder**, subfolders included, keeping its structure (`download_all_files_iterative`).
- **Binary wheels** for Linux x64/arm64 and Windows x64/arm64, the pinned CPython with and without the GIL (cp314 and cp314t in v0.10.1).
- **A pure-Python wheel** that installs anywhere, and a `SHA256SUMS` with every release.
- **Every module compiled with Cython**, the sources stripped from the binary wheels.
- **Safe across threads**: each download writes a private `.part` file and renames it into place.
- **Tested against a local mock WebDAV server**, so no remote host is needed.

## Quick start

```bash
git clone --recurse-submodules --branch develop https://github.com/Kataglyphis/WebDavClient.git
cd WebDavClient
uv sync --all-extras --python 3.15   # the pinned CPython; 3.15t for the free-threaded build
```

```python
from kataglyphis_webdavclient.webdavclient import WebDavClient

hostname = "https://yourhost.de/webdav"
username = "Schlawiner23"
password = "YOUR_PERSONAL_TOKEN"
remote_base_path = "MyProjectFolder"
local_base_path = "assets"
webdevclient = WebDavClient(hostname, username, password)
webdevclient.download_all_files_iterative(remote_base_path, local_base_path)
```

Filter with `extension=".md"`; downloads raise on HTTP, listing or unsafe-path errors.
Release wheels, logging, the demo script and the tests:
[docs/source/getting-started.md](https://github.com/Kataglyphis/WebDavClient/blob/develop/docs/source/getting-started.md).

## Documentation

| Topic | Read |
| --- | --- |
| Getting started: installation, usage, tests, static analysis | [docs/source/getting-started.md](https://github.com/Kataglyphis/WebDavClient/blob/develop/docs/source/getting-started.md) |
| The API | [docs/source/webdavclient.rst](https://github.com/Kataglyphis/WebDavClient/blob/develop/docs/source/webdavclient.rst), rendered on the [docs site](https://webdavclient.jonasheinle.de/) |
| Rules for agents and contributors | [AGENTS.md](https://github.com/Kataglyphis/WebDavClient/blob/develop/AGENTS.md) |
| Changes | [CHANGELOG.md](https://github.com/Kataglyphis/WebDavClient/blob/develop/CHANGELOG.md) |

## Contributing and contact

WebDavClient is one of the [Kataglyphis repositories](https://github.com/Kataglyphis/ANTfrastructure/blob/develop/docs/repository-family.md),
which share one way to contribute and one contact. Licence: MIT, see [LICENSE](https://github.com/Kataglyphis/WebDavClient/blob/develop/LICENSE).
