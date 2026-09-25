# AGENTS.md

Guidance for coding agents (and new contributors) working in WebDavClient.

Laid out per ANTfrastructure's
[`shared/templates/AGENTS.md.template`](third_party/ANTfrastructure/shared/templates/README.md).
The rule that shapes it: *would this still be true in a different project?* If
yes, ANTfrastructure owns it and § 2 links to it. If no, it is written out in § 3.

## 1. What this project is

A Python package for talking to a WebDAV host. Python ≥ 3.10, managed with `uv`.
It builds a **binary** wheel: the hub packaging driver exports `CYTHONIZE=True`,
and `setup.py` then compiles every module with Cython and strips the sources
from the wheel. OrchestrANT's wheel is built the same way — same driver, same
`CYTHONIZE` switch in its own `setup.py` — so this does not set the lane apart.

| Path | What lives there |
| --- | --- |
| `kataglyphis_webdavclient/` | The package — `webdavclient.py` is the substance |
| `tests/` | `test_webdav_client.py` and the `mock_webdav_server.py` it starts, plus `unit/`, `integration/`, `fuzzy/` and `remote/` (the mock server's document root) |
| `bench/`, `demo/` | Benchmarks and a runnable example |
| `scripts/linux/` | Six thin wrappers over ANTfrastructure drivers: the four Python CI lanes, plus `setup-dependencies.sh` and `run-lint-gates.sh` |
| `scripts/windows/` | `Build-Windows.ps1` + the `Resolve-BuildModule.ps1` bootstrap |
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

**Every `scripts/linux/*.sh` here is a wrapper, not an implementation.** Each
sources `scripts/linux/lib/antfrastructure.sh` and calls `antfrastructure_exec`
(or `antfrastructure_source`) into the submodule. When behaviour needs to
change, change it **upstream** — a fix made in the wrapper is a fix the other
Python consumers never get.

`run-lint-gates.sh` is the same shape over the hub lint aggregator
(`linux/scripts/run-lint-gates.sh`): seven gates — shell lint, workflow lint
plus the CI image-ref check, secret scan, `ruff`, the shared-config drift check,
the consumer pin-forwarding check, and the ratchets. The wrapper passes
`--ratchets` itself, so the seventh is not optional here: it runs the doc-link
gate and the eight measurement gates over this tree, each reading its freeze
file from the repo root (`comment-size.allow`, `function-size.allow`,
`code-complexity.allow`; the other five are empty and absent, which means
nothing frozen). A row in one of those files is a queue entry with a reason, not
a permanent exemption — shrink the thing and delete the row in the same commit,
because a stale row fails the gate exactly like a new offender.
`.github/workflows/lint-gates.yml` calls the hub's reusable lint lane with
`ratchets: true`, which runs the same aggregator over the same root with the
same `--ratchets` — straight from `third_party/ANTfrastructure`, not through
this wrapper. The consumer root is passed explicitly on both paths, because the
hub half of that script lives inside the submodule and a self-derived root
would grade the wrong tree.

`lib/antfrastructure.sh` is a verbatim copy of ANTfrastructure's
[`shared/linux/templates/antfrastructure.sh`](third_party/ANTfrastructure/shared/linux/templates/README.md)
— the bash twin of `Resolve-BuildModule.ps1`, and the only other file that
cannot live upstream because it is what *finds* the submodule. Do not hand-edit
it; sync from upstream. It owns the not-found guard and the `WORKSPACE_ROOT`
export that every wrapper used to repeat.

**Both copies are machine-checked, not asserted.** `.antfrastructure-shared.manifest`
at the repo root declares the two ids this repo takes (`antfrastructure-sh`,
`resolve-build-module`) from the registry in
`third_party/ANTfrastructure/shared/config/shared-assets.manifest`; the
shared-config gate compares them on every lint run:

```bash
bash third_party/ANTfrastructure/shared/config/sync-shared-config.sh --repo-root . --check
```

An asset left out of the manifest is never compared — that is how an
intentional project-owned override is recorded. The word "verbatim" in a header
is not a check: before 2026-09-15 `Resolve-BuildModule.ps1` had silently fallen
16 body lines behind canonical while still claiming to be a verbatim copy.

| Wrapper | Upstream driver | Local addition |
| --- | --- | --- |
| `ci_tests.sh` | `python/ci_tests.sh` | unsets `UV_PYTHON` — redundant at the current pin, whose `uv_run` clears it itself (hub `e9e4b1d2`); the wrapper's comment says to drop it then |
| `ci_static_analysis.sh` | `python/ci_static_analysis.sh` | unsets `VIRTUAL_ENV` and `UV_PYTHON` and points `UV_PROJECT_ENVIRONMENT` at the venv the driver creates but never activates |
| `ci_build_docs.sh` | `python/ci_build_docs.sh` | none |
| `ci_packaging.sh` | `python/ci_packaging.sh` | installs `patchelf` — see § 3 |

Two upstream facts repeated here only because they bite before you reach a doc:

- Every ANTfrastructure PowerShell module declares `#requires -Version 7.0`, and
  so does `scripts/windows/Resolve-BuildModule.ps1` — launch with `pwsh`, never
  `powershell`. `Build-Windows.ps1` declares nothing itself, but it dot-sources
  that bootstrap first; under 5.1 the run stops there with a
  `ScriptRequiresException` naming 7.0 (measured 2026-09-25).
- Composite actions and the reusable workflows resolve at `@develop`, so an
  ANTfrastructure change a workflow depends on must be pushed **before** the
  consumer change.

**This repo's glue:** `scripts/windows/Resolve-BuildModule.ps1` — the one file
that cannot live upstream, because it is what *finds* the submodule. Note that
nested imports inside a `.psm1` are **module-private**, so every module you call
into must be named in the `Import-BuildModule` list explicitly.

## 3. Pitfalls specific to this project

Everything here is false or meaningless in another repo — that is why it is
written out rather than linked.

- **`ci_packaging.sh` installs `patchelf` before delegating — a duplicate
  step.** The binary wheel needs it (`auditwheel repair` rewrites the wheel's
  RPATHs), but upstream's driver has installed it itself since the file's first
  commit (hub `0972946b`, 2026-06-12), two months before this wrapper delegated
  to it, and OrchestrANT's wrapper carries no such step. The wrapper's header
  says upstream does not install it; that is wrong at the current pin.
- **`WORKSPACE_ROOT` is handled for you — do not remove it.** Upstream's
  `detect_workspace` derives it from the sourcing script's location, which for a
  *delegated* driver resolves inside `third_party/ANTfrastructure/` —
  so every tool would run against the submodule tree instead of this repo.
  `antfrastructure_exec` pins it to the repo root before handing off (it used to
  be repeated in every wrapper); `detect_workspace` honours a pre-set value and
  still overrides to `/workspace` in the container, so CI is unaffected. Listed
  here only because a wrapper that stops going through `antfrastructure_exec`
  loses it silently.
- **Do not re-add a `PACKAGE_NAME` default.** The pre-wrapper `ci_tests.sh`
  defaulted it to `orchestr_ant_ion` — the *sibling* project's name, copy-pasted.
  It only ever worked because CI passed the name explicitly. Upstream derives it
  from `pyproject.toml`, which is why that class of bug cannot recur; hardcoding
  it again reintroduces the failure mode.
- **`tests/remote/` is not a remote host — and CI never tests the client.**
  `tests/remote/` is the document root `tests/mock_webdav_server.py` serves
  (wsgidav on `127.0.0.1:8081`); `tests/test_webdav_client.py` starts that
  server from a module-scoped fixture and asserts on the files under
  `tests/remote/data`, so edit those and the tests change. The paths are
  relative, so run `pytest` from the repo root. Every CI lane runs
  `pytest tests/unit` only (the hub's `ci_tests.sh` on Linux,
  `Build-Windows.ps1` on Windows), so none runs `test_webdav_client.py` or
  `tests/integration/`, and the coverage they report comes from the `dummy.py`
  tests alone: a plain `pytest` from the root is the only run that exercises
  `webdavclient.py`.
- **There is no Flutter step here.** The pre-wrapper `ci_build_docs.sh` put
  `$WORKSPACE_ROOT/flutter/bin` on `PATH`, copied from a Flutter sibling. It was
  dropped rather than ported — if you see it reappear, it is copy-paste.

## 4. Build, run, test

```bash
uv sync

# The arguments linux-x64.yml passes. Bare, the drivers default to 3.14 (tests:
# "3.13 3.14"), which this project cannot install on x86_64: atheris ships no
# cp314 wheel (the comment in linux-x64.yml has the measurement).
bash scripts/linux/ci_tests.sh kataglyphis_webdavclient '3.13 3.14t'  # pytest tests/unit + coverage
bash scripts/linux/ci_static_analysis.sh x64 3.13  # codespell, bandit, vulture, ruff, ty
bash scripts/linux/ci_build_docs.sh                # Sphinx (driver default 3.13)
bash scripts/linux/ci_packaging.sh 3.13            # sdist + binary wheel (installs patchelf)

bash scripts/linux/run-lint-gates.sh     # the seven lint gates, ratchets included
```

Windows:

```powershell
pwsh -NoProfile -File .\scripts\windows\Build-Windows.ps1
```

CI lanes: `.github/workflows/linux-x64.yml` and `linux-arm64.yml` (the two rows
of one hub reusable lane, `arches` picking the row; keep their Python versions
equal), `.github/workflows/windows-x64.yml` and `.github/workflows/lint-gates.yml`
— every one of them configuration for an ANTfrastructure reusable workflow, do
not re-inline the steps. `scripts/linux/run-lint-gates.sh` is the same lint lane
for a local run. File and display names follow the family convention (owner
decision 2026-09-24): kebab-case, one file per platform + arch, display names
`<Platform> <Arch> · <what>`, shared lanes named the same in every repo (`Lint
gates`). The two Linux files split `ubuntu-26.04-amd64-arm64.yml` on 2026-09-25.
Every lane runs on every push and pull request to `main` and `develop`; none is
opted into by a commit-message token.

## 5. Docs owned by this repo

- Sphinx sources in `docs/`. `docs/source/README.md` and
  `docs/source/CHANGELOG.md` are copies: the docs driver copies the root
  `README.md` and `CHANGELOG.md` over them before every build, so edit the root
  files.
- `CHANGELOG.md` and `VERSION.txt` — the version is read from `VERSION.txt`, so
  bump it there.
- Update docs in the same PR as user-facing behaviour changes.
