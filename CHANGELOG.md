# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `scripts/linux/run-lint-gates.sh` and `.github/workflows/lint-gates.yml`: the
  family lint lane. Seven gates over the tracked tree — shell lint, workflow
  lint plus the CI image-ref check, secret scan, `ruff`, the shared-config
  drift check, the consumer pin-forwarding check and the ratchets — all owned
  by ANTfrastructure’s `linux/scripts/run-lint-gates.sh`. Before this the repo
  had no shell, workflow or secret linting at all.
- `comment-size.allow`, `function-size.allow`, `code-complexity.allow`: the
  ratchet freeze files. The wrapper passes `--ratchets` itself, so the seventh
  gate is not optional here: it runs the doc-link gate and eight measurement
  gates over this tree. Five measured clean and get no file at all. Every row
  in the three that exist carries a reason and is a queue entry, not an
  exemption — the contract fails on growth, on a new offender, on an
  unrecorded shrink AND on a stale row.
- `.antfrastructure-shared.manifest`: declares the two upstream files this repo
  holds a copy of (`antfrastructure-sh`, `resolve-build-module`) so the
  shared-config gate compares them instead of trusting the word "verbatim" in a
  header. `.gitignore` had to un-ignore it — the PyInstaller `*.manifest` rule
  is unanchored.
- `.github/actionlint.yaml`: teaches the pinned actionlint the `ubuntu-26.04`
  runner labels it predates.

### Changed
- **2026-09-24: the workflows follow the family naming convention** (owner
  decision). `windows-2025.yml` is `windows-x64.yml` ("Windows x64 · build +
  test") and the lint lane's display name is plain `Lint gates`, as in every
  other repo. Triggers, jobs and job ids are unchanged; the README badges
  follow the new file. `ubuntu-26.04-amd64-arm64.yml` keeps its name for now:
  its split into `linux-x64.yml` and `linux-arm64.yml` needs a hub
  reusable-lane input that is not on hub `main` yet.
- **The hub pin moved to ANTfrastructure `19286e9f`** (from the published
  `4f6f516a`). The published hub still listed WebDavClient under `unconfirmed`
  in its `.github/consumers.json`, and the workflow-conventions gate refuses a
  tree it cannot key its allow rows to, so that gate could not pass at the old
  pin at all. NOTE: `19286e9f` is NOT PUSHED anywhere yet — do not push this
  repo before ANTfrastructure is, or the gitlink resolves to nothing.
- `scripts/linux/lib/antfrastructure.sh` re-synced against the new pin (hub
  commit `e03bbe42` rewrote the template). `ANTFRASTRUCTURE_DIR` now resolves
  in a documented order — explicit env, then the submodule, then an
  `antfrastructure-tools` sibling clone — and the not-found error picks its
  hint from whether `.gitmodules` actually declares the submodule.
- The two reusable-lane callers declare `permissions: contents: read`, which is
  what `python-ci-linux.yml` and `python-ci-windows.yml` declare themselves; a
  called workflow runs on the caller’s token, and the only registry credential
  in either lane is `secrets.GHCR_PAT`. Without it GITHUB_TOKEN fell through to
  the repository default.
- `*.allow` joins the `eol=lf` rules in `.gitattributes`: those files are read
  only by the hub’s Python gates, which run in the Linux container.
- **The hub submodule moved from `ExternalLib/Kataglyphis-ContainerHub` to
  `third_party/ANTfrastructure`**, matching every other consumer, and
  `.gitmodules` now points at `https://github.com/Kataglyphis/ANTfrastructure.git`.
  The upstream repository was renamed from Kataglyphis-ContainerHub to
  ANTfrastructure; every reference in this repo followed, including the
  `containerhub_*` bootstrap entry points (now `antfrastructure_*`),
  `scripts/linux/lib/containerhub.sh` (now `lib/antfrastructure.sh`), and this
  repo's own name, which dropped its `Kataglyphis-` prefix.
- The two reusable-workflow lanes now call
  `Kataglyphis/ANTfrastructure/.github/workflows/python-ci-{linux,windows}.yml@main`.
  The Linux lane's file was renamed `ubuntu-24.04-amd64-arm64.yml` ->
  `ubuntu-26.04-amd64-arm64.yml`: the reusable lane pins `ubuntu-26.04` and
  `ubuntu-26.04-arm`, so the old file name had been wrong since adoption.
- `scripts/windows/Resolve-BuildModule.ps1` re-synced from the upstream
  template. The local copy had fallen 16 body lines behind: the `.ps1` arm of
  `Resolve-BuildModule` (which is what makes `Initialize-CiEnvironment.ps1`
  reachable) and the dot-source guard in `Import-BuildModule` were both missing.
- `ruff` is pinned to `0.16.7` in `pyproject.toml` and `.pre-commit-config.yaml`,
  forwarded from ANTfrastructure's `versions.env` and checked by the
  consumer-pins gate. The three numbers had drifted apart — the lockfile carried
  0.15.6 while pre-commit asked for 0.13.2.
- `.github/github_copilot_instructions.md` renamed to
  `.github/copilot-instructions.md`, the path GitHub Copilot actually reads.

### Deprecated
- Placeholder for soon-to-be removed features.

### Removed
- Placeholder for now removed features.

### Fixed
- `tests/integration/test_dummy.py` patched `numpy.random.normal` while
  `SimpleMLPreprocessor` calls `np.random.default_rng().normal(...)`, so the
  fixture was never used and the label assertion was a fair coin on four rows —
  passing about one run in sixteen. It now patches `default_rng`. Pre-existing:
  neither file had changed since `origin/main`.
- Four references the doc-link gate resolves to nothing: two cross-repo pointers
  that named the hub’s `AGENTS.md` and `docs/adopting-in-a-new-project.md` as if
  they were this repo’s, and a relative `LICENSE` link in the two WebDAV test
  fixtures that has never existed beside them.
- **The Linux lane pinned 3.14, where this project cannot install.** `tests`
  declares `atheris`, every lane syncs `--all-extras`, and atheris 3.0.0 ships
  cp311/cp312/cp313 wheels and nothing newer, so 3.14 falls back to an sdist
  whose build needs a Clang with libFuzzer and fails. That build did succeed in
  the family image on 2026-08-14 (run `31823466662`); it no longer does, on a
  runner or on a dev box with the same image. The lane's test, static-analysis
  and packaging interpreters are 3.13 now — the newest every locked dependency
  of this project actually ships; 3.14t stays because the driver treats it as
  experimental and its sync failure only warns. Restore 3.14 when atheris ships
  a cp314 wheel, or give atheris a marker instead of the lane a pin.
- **Neither half of the Linux lane's gating ran, for one shared reason.**
  Upstream's `uv_run` is `uv run --active` with the image's
  `UV_PYTHON=/opt/venv/bin/python` and `VIRTUAL_ENV=/opt/venv` still in scope,
  while its sibling `uv_sync_project` clears exactly those two for its own call
  and documents why. Static analysis: its driver never activates the venv it
  creates (`uv_venv_ensure` activates only one that already existed), so all six
  gates hit root-owned `/opt/venv` and died with `Permission denied` before
  running a check. Tests: `uv_run` found the activated `.venv-<ver>` disagreeing
  with `UV_PYTHON`, deleted it, rebuilt it with the image's interpreter and
  default groups — and `pytest` is in the `tests` EXTRA, so the run died with
  ``Failed to spawn: `pytest` ``. The matrix only ever escaped that by testing
  the one interpreter the image happens to ship. The two wrappers now clear
  those variables (and static analysis names `UV_PROJECT_ENVIRONMENT`, doing
  what the `uv_venv_activate` `ci_build_docs.sh` already carries would do).
  Invisible until the pin reached `604294e2`: upstream ran those six behind
  `|| true` until 2026-09-08.
- The two findings that surfaced once the analysers ran for real, fixed rather
  than ignored: `ruff` CPY001 over twelve files (the MIT `LICENSE`'s notice now
  heads each one), and `vulture` on `myst_heading_anchors`, which was the one
  Sphinx setting missing from `conf.py`'s own `_SPHINX_EXPORTS` tuple.

### Security
- Placeholder for vulnerabilities patched.

---

## [1.0.0] - YYYY-MM-DD

### Added
- Initial release.

<!-- Add past versions below this line -->

<!-- Example:
## [0.9.0] - 2024-01-15

### Added
- Beta release features.
-->

---

<!-- Links for diffs -->
[Unreleased]: https://your.repo.url/compare/v1.0.0...HEAD
[1.0.0]: https://your.repo.url/releases/tag/v1.0.0
