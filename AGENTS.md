# AGENTS.md

Guidance for coding agents (and new contributors) working in WebDavClient.

Laid out per ANTfrastructure's
[`shared/templates/AGENTS.md.template`](third_party/ANTfrastructure/shared/templates/README.md).
The rule that shapes it: *would this still be true in a different project?* If
yes, ANTfrastructure owns it and § 2 links to it. If no, it is written out in § 3.

## 1. What this project is

A Python package for talking to a WebDAV host. Python ≥ 3.10, managed with `uv`. It builds
a **binary** wheel: the hub packaging driver exports `CYTHONIZE=True`, and `setup.py` then
compiles every module with Cython and strips the sources from the wheel. OrchestrANT builds
its wheel the same way (same driver, same `CYTHONIZE` switch in its own `setup.py`), so
this does not set the lane apart.

| Path | What lives there |
| --- | --- |
| `kataglyphis_webdavclient/` | The package — `webdavclient.py` is the substance |
| `tests/` | `test_webdav_client.py` and the `mock_webdav_server.py` it starts, plus `unit/`, `integration/`, `fuzzy/` and `remote/` (the mock server's document root) |
| `bench/`, `demo/` | Benchmarks and a runnable example |
| `scripts/linux/` | Six thin wrappers over ANTfrastructure drivers: the four Python CI lanes, plus `setup-dependencies.sh` and `run-lint-gates.sh` |
| `scripts/windows/` | `python-ci.psd1` (the hub's Windows build driver reads it, § 2), the `Resolve-BuildModule.ps1` bootstrap, and `setup-dependencies.ps1`, a winget/scoop host-toolchain installer no lane calls |
| `third_party/ANTfrastructure` | The submodule owning every reusable script, module and doc |

Distribution name and module name agree here (`kataglyphis_webdavclient`), so
upstream's `PACKAGE_NAME` derivation from `pyproject.toml` is correct and no
wrapper overrides it.

## 2. What ANTfrastructure owns — links only

**Do not restate these procedures here.** Start at
[`third_party/ANTfrastructure/docs/INDEX.md`](third_party/ANTfrastructure/docs/INDEX.md),
which maps topic → owning document, so these links survive upstream
reorganisation.

| Topic | Where |
| --- | --- |
| Wiring this repo to ANTfrastructure — resolver, actions, libraries | `docs/adopting-in-a-new-project.md` |
| Linux container builds | `docs/linux-build-basics.md` |
| Running Linux containers on a Windows host | `docs/rancher-desktop-linux-containers.md` |
| The Windows image, its entrypoint and known traps | `docs/windows-builds.md` |
| Bind mount vs tar-pipe, Dev Drive filter setup, container reuse | `docs/windows-container-build-performance.md` |
| Python CI lanes and the uv traps | [`docs/python-ci.md`](third_party/ANTfrastructure/docs/python-ci.md) |
| The five shell-safety bug classes | [`third_party/ANTfrastructure/AGENTS.md`](third_party/ANTfrastructure/AGENTS.md) § *Shell safety conventions* |
| Code comments: one line, only the why; API docs short; gated | [`third_party/ANTfrastructure/AGENTS.md`](third_party/ANTfrastructure/AGENTS.md#comments-one-line-only-the-why) § *Comments: one line, only the why* |
| Searching the tree: `rg`, not `grep -r` | [`third_party/ANTfrastructure/AGENTS.md`](third_party/ANTfrastructure/AGENTS.md) § *Searching the tree: ripgrep (`rg`)* |

**Every `scripts/linux/*.sh` here is a wrapper, not an implementation.** Each sources
`scripts/linux/lib/antfrastructure.sh` and calls `antfrastructure_exec` (or
`antfrastructure_source`, or runs the path `antfrastructure_path` resolves) into the submodule. Change behaviour **upstream**: a fix
made in the wrapper is a fix the other Python consumers never get.

| Wrapper | Upstream driver | Local addition |
| --- | --- | --- |
| `ci_tests.sh` | `python/ci_tests.sh` | none |
| `ci_static_analysis.sh` | `python/ci_static_analysis.sh` | points `UV_PROJECT_ENVIRONMENT` at the venv the driver creates but never activates |
| `ci_build_docs.sh` | `python/ci_build_docs.sh` | none |
| `ci_packaging.sh` | `python/ci_packaging.sh` | installs `patchelf` — see § 3; then runs the hub's `python/test-free-threaded-wheel.sh` |

**`run-lint-gates.sh` runs the hub lint aggregator with `--ratchets`**, the same call
`.github/workflows/lint-gates.yml` makes with `ratchets: true`. What each of its eight gates
checks and how a freeze file works:
[`code-quality-tooling.md`](third_party/ANTfrastructure/docs/code-quality-tooling.md#the-scan-root-contract).
This repo freezes rows in `comment-size.allow`, `function-size.allow` and
`code-complexity.allow`, and budgets the passages it shares with a hub page in
`doc-dupes-hub.allow`; a gate with no file here has nothing frozen.

**The two bootstrap copies**, `scripts/windows/Resolve-BuildModule.ps1` and its bash twin
`scripts/linux/lib/antfrastructure.sh`, cannot live upstream, because they are what *find*
the submodule. `.antfrastructure-shared.manifest` declares them (`antfrastructure-sh`,
`resolve-build-module`), and the shared-config gate compares them with the hub's templates
on every lint run: re-copy them from the templates, never edit them here
([the hub's `shared/config/README.md`](third_party/ANTfrastructure/shared/config/README.md#the-template-trees-are-owners-too)).

**The Windows x64 build is the hub's** (2026-10-19): `python-ci-windows.yml` runs
`windows/scripts/python/Invoke-PythonCiBuild.ps1`, which takes this repo's values from
`scripts/windows/python-ci.psd1`: the pinned X.Y and X.Yt (`pinned pinnedt`; X.Yt with only the
`tests` extra), and packaging on the pinned X.Y
([`python-ci.md` § *The Windows build driver*](third_party/ANTfrastructure/docs/python-ci.md#the-windows-build-driver)).
Its static analysis is the hub's `Invoke-CiStaticAnalysis.ps1` on the pinned Python, and it gates.

Two upstream facts repeated here only because they bite before you reach a doc:

- Every ANTfrastructure PowerShell module and the hub's build driver declare
  `#requires -Version 7.0`, and so does `scripts/windows/Resolve-BuildModule.ps1` —
  launch with `pwsh`, never `powershell`.
- Composite actions and the reusable workflows resolve at `@develop`, so an
  ANTfrastructure change a workflow depends on must be pushed **before** the
  consumer change.

For local work on the newest code, run
`bash third_party/ANTfrastructure/linux/scripts/git-sync-branches.sh` (`--dry-run`
first): [`adopting-in-a-new-project.md` § *Putting every checkout on its branch*](third_party/ANTfrastructure/docs/adopting-in-a-new-project.md#putting-every-checkout-on-its-branch).

## 3. Pitfalls specific to this project

Everything here is false or meaningless in another repo — that is why it is
written out rather than linked.

- **`ci_packaging.sh` installs `patchelf` before delegating, a duplicate step.** The binary
  wheel needs it (`auditwheel repair` rewrites the wheel's RPATHs), but upstream's driver
  has installed it itself since the file's first commit (hub `fc4df858`, 2026-06-12), two
  months before this wrapper delegated to it, and OrchestrANT's wrapper carries no such
  step. The wrapper's header keeps it local "because no second consumer needs it"; at the
  current pin upstream installs it anyway.
- **`ci_packaging.sh` exports `WORKSPACE_ROOT` itself; do not remove it.** It runs the
  hub driver with `bash`, not through `antfrastructure_exec`, so that the free-threaded wheel
  suite can follow it, and so misses the export `antfrastructure_exec` makes. Without it
  every tool runs against the submodule tree
  ([the hub's templates README](third_party/ANTfrastructure/shared/linux/templates/README.md#the-three-entry-points)).
- **Do not re-add a `PACKAGE_NAME` default.** The pre-wrapper `ci_tests.sh` defaulted it to
  `orchestr_ant_ion`, the *sibling* project's name, copy-pasted. It only ever worked
  because CI passed the name explicitly. Upstream derives it from `pyproject.toml`, which
  is why that class of bug cannot recur; hardcoding it again reintroduces the failure mode.
- **`tests/remote/` is not a remote host.** It is the document root
  `tests/mock_webdav_server.py` serves (wsgidav on `127.0.0.1:8081`);
  `tests/test_webdav_client.py` starts that server from a module-scoped fixture and asserts
  on the files under `tests/remote/data`, so edit those and the tests change. The paths are
  relative, so run `pytest` from the repo root. Every CI lane runs the whole configured
  suite, `testpaths = tests`, all 10 tests, since 2026-10-01.
  - Linux: the hub's `ci_tests.sh` passes pytest no path of its own.
  - Windows: the hub's driver runs a bare `pytest`, since `python-ci.psd1` sets no `TestPaths`.
  - Until then every lane had run `tests/unit` only. That narrowing came with the arm64
    and Windows lanes (2025-10-20), so `test_webdav_client.py` and `tests/integration/`
    ran on no lane, and coverage came from the dummy tests alone.
- **The 3.14t test leg tests the sources, not the Cython build.** The hub's `ci_tests.sh`
  syncs the project uncompiled, and the hub's packaging proof only *creates* each compiled
  module (`free-threaded-wheel.py prove`), never runs it. So `ci_packaging.sh` runs the hub
  driver as a child, then the hub's `test-free-threaded-wheel.sh` (a local script until
  2026-10-12): the locked `tests` extra and the `cp314t` wheel from `dist/` go into a fresh
  3.14t venv, and the whole suite runs from a copy of `tests/` and `pytest.ini` that has no
  package directory beside it. `KATAGLYPHIS_EXPECT_COMPILED=1` makes
  `tests/unit/test_free_threading.py` fail when a module is not the compiled one, and on
  any free-threaded leg it fails when importing the package turns the GIL back on. Both
  Linux rows run it; the Windows lanes do not yet.
- **Module state is shared between threads, so it is locked.** The modules hold one piece
  of mutable state, the set of loguru file sinks in `webdavclient.py`. Before 2026-10-11
  every `WebDavClient()` added another sink on the same file, so each line was written
  once per client and the file rotated once per client. Downloads write a private `.part`
  file and rename it into place, so threads that share a destination never interleave.
  `freethreading_compatible=True` in `setup.py` rests on that audit. A new module-level
  cache, global or lazily built object needs a lock as well, and a test in `tests/` that
  drives it from threads.
- **`packages.find` must keep its `include`.** Setuptools' default namespace discovery took
  `third_party/`, `scripts/` and `images/` as top-level packages, 218 in all, and every
  wheel shipped the hub's scripts into `site-packages/third_party/` until 2026-10-11.
- **There is no Flutter step here.** The pre-wrapper `ci_build_docs.sh` put
  `$WORKSPACE_ROOT/flutter/bin` on `PATH`, copied from a Flutter sibling. It was dropped
  rather than ported; if it reappears, it is copy-paste.

## 4. Build, run, test

```bash
uv sync

# Every lane runs the pinned X.Y and X.Yt; Linux follows :latest's X.Y (3.14 and 3.14t on
# 2026-10-19). X.Yt syncs only the tests extra (free-threaded-extras) and gates like X.Y. Two changes
# made that leg possible: atheris is gone (no cp314t wheel, nothing used it), and bcrypt is
# overridden to >=5 (wsgidav caps it below 5, and 4.x has no cp314t wheel).
FREE_THREADED_SYNC_EXTRAS=tests bash scripts/linux/ci_tests.sh kataglyphis_webdavclient  # X.Y and X.Yt: whole suite + coverage
bash scripts/linux/ci_static_analysis.sh x64       # codespell, bandit, vulture, ruff, ty (X.Y)
bash scripts/linux/ci_build_docs.sh                # Sphinx, with X.Y's coverage
bash scripts/linux/ci_packaging.sh                 # sdist + cpXY and proved cpXYt wheels, then the suite on the cpXYt one

bash scripts/linux/run-lint-gates.sh     # the eight lint gates, ratchets included
```

Windows:

```powershell
# Inside :winamd64, from the repo root: the hub's driver, as windows-x64.yml runs it.
pwsh -NoProfile -File .\third_party\ANTfrastructure\windows\scripts\python\Invoke-PythonCiBuild.ps1
```

| CI lane | What it runs |
| --- | --- |
| `.github/workflows/linux-x64.yml`, `linux-arm64.yml` | the two rows of one hub reusable lane, `arches` picking the row; keep their Python versions equal |
| `.github/workflows/windows-x64.yml` | Windows x64 · build + test |
| `.github/workflows/windows-arm64.yml` | the hub's runner-native `windows-11-arm` pytest job: no container, wheels only, so a dependency without a `win_arm64` wheel needs `platform_machine != 'ARM64'` |
| `.github/workflows/lint-gates.yml` | the lint gates; `scripts/linux/run-lint-gates.sh` is the same lint lane for a local run |

Every one of them is configuration for an ANTfrastructure reusable workflow; do not
re-inline the steps. Names follow the fleet convention
([`adopting-in-a-new-project.md` § *Workflow file names and display names*](third_party/ANTfrastructure/docs/adopting-in-a-new-project.md#workflow-file-names-and-display-names));
the two Linux files split `ubuntu-26.04-amd64-arm64.yml` on 2026-09-25.

**CI rounds and releases follow the family rule**, ANTfrastructure's
[`branch-and-release-strategy.md`](third_party/ANTfrastructure/docs/branch-and-release-strategy.md)
(here since 2026-10-16). A push or PR runs Linux x64 and the lint gates; Linux arm64,
Windows x64 and Windows arm64 run on request (`[ci arm64]`, `[ci windows]`, `[ci all]`). A
push to `main` releases the `VERSION.txt` version with a cp314 and a cp314t binary wheel from
each lane (Linux x86_64 and aarch64, Windows amd64 and arm64), Linux x64's pure wheel and
sdist, and the hub publisher's `SHA256SUMS`: `release.yml` calls the hub's `release-publish.yml`,
which collects them with its `collect` options (since 2026-10-19). A dry run collects and lists
them and tags nothing: `gh workflow run release.yml --ref develop -f dry-run=true`.

## 5. Docs owned by this repo

**Write docs like a developer: short and precise** (owner, 2026-10-19). Say what a thing does,
how to run it and what breaks; no filler, no marketing, no repetition.

- Sphinx sources in `docs/`. `docs/source/README.md` and
  `docs/source/CHANGELOG.md` are copies: the docs driver copies the root
  `README.md` and `CHANGELOG.md` over them before every build, so edit the root
  files. They stay tracked because `docs/Makefile` and `make.bat` build without
  that copy; re-sync them in the commit that changes the root file. A new page
  goes into `docs/source/index.rst`'s toctree.
- `conf.py` calls the family theme's `setup_theme()`, which `docs/Makefile` and `make.bat`
  install editable from the hub's vendored DocumANTation before every build. It is not a uv
  path source: a checkout without that submodule would then fail every `uv sync --locked`.
  The brand CSS comes with the theme; do not add a copy under `docs/source/_static/`.
- `README.md` is the short overview the family's README rule asks for
  ([`repository-family.md`](https://github.com/Kataglyphis/ANTfrastructure/blob/develop/docs/repository-family.md#the-readme-rule));
  installation, usage, tests and static analysis are
  [`docs/source/getting-started.md`](docs/source/getting-started.md). `pyproject.toml`'s
  `readme` makes the README the package's long description, so it links with absolute
  GitHub URLs.
- `CHANGELOG.md` and `VERSION.txt` — the version is read from `VERSION.txt`, so
  bump it there, and turn `## [Unreleased]` into its `## [<version>]` section before a merge into
  `main`: the release takes its notes from it and refuses a version without one.
- Update docs in the same PR as user-facing behaviour changes.
