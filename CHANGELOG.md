# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **The README logo is the family's ant** (2026-10-17, owner: one icon in every repository),
  drawn from OmniAccelerANT's `assets/icons/kataglyphis_app_icon.svg`.
- **The README is a short overview** (owner, 2026-10-19: every README links into its docs, and
  ANTfrastructure's `repository-family.md` holds contributing, licence and contact for the family).
  Installation, usage, tests and static analysis moved to the new `docs/source/getting-started.md`,
  which is in the Sphinx toctree. The empty Roadmap, Useful tools and Acknowledgements sections,
  the commented-out Vulkan literature and the unused Best-README-Template link definitions are
  gone. The clone URL is `https://`, as for every family repository, and the logo has an absolute
  URL, so it also shows on the docs site and in the package's long description.
- **`.github/copilot-instructions.md` points at `AGENTS.md`** and names five of its rules, in
  English. It was a 213-line German template with C++, Rust and Dart sections for code this
  repository does not have.
- **`AGENTS.md` links ANTfrastructure instead of restating it** (2026-10-19): the lint gates and
  the freeze-file contract, the bootstrap copies' body mode and their drift history, the
  module-private PowerShell imports, `git-sync-branches.sh`, the workflow naming and the
  CI-round and release rule point at the hub's pages; this repo's lanes, release files and
  exceptions stay. `doc-dupes-hub.allow` turns on the hub's `doc-dupes --against-hub` gate.
- **The docs site wears the family theme** (2026-10-19): `docs/source/conf.py` calls
  `sphinx_kataglyphis.setup_theme()`, so the site gets the current brand CSS, the family logo and
  favicon, the Kataglyphis code palette, `<page> — WebDavClient` titles and GitHub heading anchors
  on every level (`myst_heading_anchors` 6, was 3). `docs/Makefile` and `make.bat` install the
  theme editable from the hub's vendored DocumANTation before every build; a uv path source would
  fail every `uv sync --locked` of a checkout without submodules. The `sys.path` entry the old
  `conf.py` added resolved against the working directory to the repository's parent; autodoc
  imports the package the docs venv installs.
- **`release.yml` calls the hub's `release-publish.yml`** (2026-10-19) for its version check and
  its release job, which collects with this repo's `collect` options (the wheels and the sdist,
  the pure wheel and the sdist from Linux x64 only, reports and logs left out), tags
  `v<version>` and publishes. `scripts/linux/collect-release-assets.sh`, its suite and
  `linux-x64.yml`'s `release-collector` job are gone; the hub's suite runs these options over this
  repo's uploads. Over v0.10.1's real uploads (run 39048087762) the old and the hub collector pick
  the same 10 files, the release's assets but `SHA256SUMS`. ANTfrastructure moves to c3fc7585.

### Removed
- **`exhale_args` in `docs/source/conf.py`, and `breathe` and `exhale` in the `docs` extra**:
  Doxygen tooling for C++ that no page loaded. The docs build without them gives zero warnings,
  as before.
- **`docs/source/_static/css/custom.css`**, an 81-line fork of the brand sheet that still painted
  links the pre-cyan green; the theme ships the generated one.

### Fixed
- **`AGENTS.md` names what a release carries instead of "six binary wheels"**: a cp314 and a
  cp314t wheel from each of Linux x86_64 and aarch64 and Windows amd64 and arm64 (eight, as
  v0.10.1 has), Linux x64's pure wheel and sdist, and `SHA256SUMS`.
- **`docs/source/CHANGELOG.md` matches `CHANGELOG.md` again**; it lacked the 0.10.0 and 0.10.1
  sections, and `docs/Makefile` builds from the tracked copy. 0.10.0's link to the hub's
  `AGENTS.md` is absolute, so it resolves from the copy too.
- **The dead links a live-site audit found (2026-10-19) are gone.** The docs index linked
  `py-modindex.html`, which Sphinx did not write, and the API page's `:no-index:` left the eight
  links back from the highlighted source without a target; the page now indexes `WebDavClient`
  and its methods. The README's *Automatic Dependency Submission* badge named a workflow this
  repository does not have. The coverage report and both test reports, published with every docs
  build, are linked from the docs index.
- **`AGENTS.md` matches the code again**: the lint aggregator runs eight gates, not seven; the
  `WORKSPACE_ROOT` pitfall names `ci_packaging.sh`, the one wrapper that runs its driver without
  `antfrastructure_exec` and so exports the variable itself; and `scripts/windows/` also holds
  `setup-dependencies.ps1`.

## [0.10.1] - 2026-10-17

### Added
- **Windows arm64 wheels** (2026-10-17): the Windows arm64 lane builds `cp314-cp314-win_arm64` and
  `cp314-cp314t-win_arm64` natively on `windows-11-arm`, after its tests, with Visual Studio's own
  clang-cl, and installs each alone into a fresh venv where every compiled module must load (the
  `cp314t` one with the GIL off). The release collector picks them up beside the `win_amd64` pair,
  and its suite expects ten files now. Until now a release carried no Windows arm64 wheel, because
  the hub's arm64 container cross-builds no GIL Cython wheel. ANTfrastructure moves to f24e7530
  (`python-ci-windows.yml`'s `arm64-wheels`). Owner rule of the same day: every release ships Windows
  arm64 next to x64.

## [0.10.0] - 2026-10-16

### Changed
- **Every push to `main` releases `v<version>`, and only when all four lanes are green** (2026-10-16,
  `release.yml`, the family's rule in [ANTfrastructure's `branch-and-release-strategy.md`](https://github.com/Kataglyphis/ANTfrastructure/blob/develop/docs/branch-and-release-strategy.md)).
  The version is `VERSION.txt`'s; the release carries the binary wheels of Linux x64, Linux arm64 and
  Windows x64 (cp314 and cp314t each), the pure wheel and the sdist, which every lane builds and Linux
  x64's copy ships (`scripts/linux/collect-release-assets.sh`; its suite runs with Linux x64 on every
  push). The hub moves to 15bc7d6c, which carries the release script.
- **A push runs Linux x64 and the lint gates; Linux arm64, Windows x64 and Windows arm64 run on request**
  (2026-10-16), the family's CI rule ([ANTfrastructure's `branch-and-release-strategy.md`](https://github.com/Kataglyphis/ANTfrastructure/blob/develop/docs/branch-and-release-strategy.md)).
  `on-request.yml` starts the lanes a pushed commit message asks for with the ci token (`windows`,
  `arm64`, `all`), every lane keeps its Run workflow button, and each lane's concurrency group names
  the lane and its caller.
- **ruff 0.17.0, ANTfrastructure 3a0ab1c3 -> 0768e5e0 and the lock's maintenance (2026-10-13).** The hub's tool
  batch moves `RUFF_VERSION` to 0.17.0, so `pyproject.toml`, `.pre-commit-config.yaml` and `uv.lock` follow it in
  the same commit, as the consumer-pins gate requires. `uv lock --upgrade` with uv 0.13.0, the hub's pin, writes lock
  revision 5 and moves ten packages, ty 0.0.86, numpy 2.5.4 and pre-commit 4.7.0 among them. `linux-x64.yml`'s
  two-line comment is one line again; the comment-size ratchet had failed the lint lane on it since 2026-10-12.
  In `:latest`: the seven lint gates and the six static-analysis gates pass, and so do 22 tests (2 skipped) on
  CPython 3.15.0 and 3.14.4, and 23 (1 skipped) on 3.14t.
- **The suite on the installed cp314t wheel runs through the hub's step (2026-10-12).**
  `scripts/linux/ci_packaging.sh` calls the hub's `test-free-threaded-wheel.sh` (hub ff91d46d, CON66) with
  `--extra tests --copy tests --copy pytest.ini --env KATAGLYPHIS_EXPECT_COMPILED=1`, in place of the local
  `scripts/linux/test-free-threaded-wheel.sh`, which is gone. The lock's set now comes from `uv export --locked`
  rather than `--frozen`. A local run of the wrapper in `:latest` proved 3 compiled modules and passed all 24 tests.

### Added
- **The whole suite runs against the installed cp314t wheel on both Linux rows (2026-10-11).**
  The 3.14t test leg tested the uncompiled sources, and the hub's proof only creates each
  compiled module without running it. `scripts/linux/ci_packaging.sh` now runs
  `scripts/linux/test-free-threaded-wheel.sh` after the hub driver. It installs the locked
  `tests` extra and the `cp314t` wheel into a fresh 3.14t venv, and runs pytest from a copy of
  `tests/` that has no package directory beside it. `tests/unit/test_free_threading.py` fails
  when importing the package re-enables the GIL, and, under `KATAGLYPHIS_EXPECT_COMPILED=1`,
  when a module is not the compiled one. `tests/test_webdav_client.py` adds eight threads that
  share one client and one destination. Locally in `:latest`: 22 passed on the wheel. Both
  negative controls fail: a wheel built without `freethreading_compatible` gives
  `assert True is False` and the hub's proof exits 1, and a run from the checkout imports the sources.
- **A `packaging` extra with auditwheel (2026-10-07).** The hub's Linux packaging repairs the
  Cython wheels to manylinux with the packaging venv's auditwheel once the hub pin carries
  0fb3bd95; PATH never had one, so the Linux binaries shipped as `linux_<arch>`.
- **A proved free-threaded wheel beside the GIL one (2026-10-07).** `pyproject.toml` drops
  `Programming Language :: Python :: 3.14t`, which is no trove classifier (PyPI refuses an
  upload that names it), for the official `Programming Language :: Python :: Free Threading
  :: 2 - Beta`: Beta, because the 3.14t test legs gate. The hub's packaging drivers read that
  classifier: once the hub pin carries them, they build a second Cython wheel on the image's
  3.14t (`cp314-cp314t`) and load its compiled modules in a fresh 3.14t venv, failing when the
  GIL comes back on. `setup.py` therefore sets Cython's `freethreading_compatible=True`
  (`cython>=3.1`, the first with the directive); without it the proof fails, as a local
  negative control showed. Proved locally with the hub's new drivers in `:latest` and
  `:winamd64`: both lanes ship `kataglyphis_webdavclient-0.0.1-cp314-cp314t-{linux_x86_64,win_amd64}.whl`,
  its 3 compiled modules keep the GIL off, and the 18 tests pass on 3.14t against the installed
  wheel with `sys._is_gil_enabled()` still False.
- **A Windows arm64 test lane** (`.github/workflows/windows-arm64.yml`, "Windows arm64 ·
  test", 2026-10-01). It is the hub's runner-native `windows-11-arm` job (`arm64-tests`,
  hub 0ef3f68d): no container and no build, just the whole pytest suite on the 3.14 and
  3.14t legs. It uses arm64 CPython from uv, pinned and SHA-checked by the hub. The lock
  resolves from `win_arm64` wheels alone since py-spy and line_profiler stay off ARM64.
  ANTfrastructure moves from 65d61617 to 0ef3f68d.
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
- **`uv.lock` maintenance: every locked package at its newest release (2026-10-07).** The
  owner's "bleeding edge" rule covers the lock too, and no Renovate manager reported this drift
  because the hub's shared preset had no `lockFileMaintenance`. `uv lock --upgrade` moved 41
  packages; the majors are chardet 6, filelock 4, more-itertools 11 and rich 15, all
  transitive, and pytest-benchmark 5.3 swaps py-cpuinfo for py-cpuinfo2. ty goes 0.0.23 ->
  0.0.85, numpy 2.4.3 -> 2.5.3 (cp314t wheels on PyPI), cython 3.3.0. ruff stays at the hub's
  0.16.10. No code change was needed: in `:latest`, `ci_static_analysis.sh` passes its 6 gates
  (ty 0.0.85 included), `ci_tests.sh` passes 18 tests on 3.14 and on 3.14t (bcrypt 5.0.0 and
  numpy 2.5.3 from free-threaded wheels), and `run-lint-gates.sh` passes 7/7.
- **Windows packaging is the hub's `Invoke-CiPackaging.ps1` on 3.14 (2026-10-07).**
  `scripts/windows/Build-Windows.ps1` built in a 3.13 venv with a bare `uv build`, which ignores
  the venv and takes whatever interpreter uv finds, a free-threaded one included. The driver asks
  for `3.14+gil`, as the Linux lane does, and adds the free-threaded wheel above.
- **Comments are one line, only the why (2026-09-30).** The family rule, in
  [the hub's `AGENTS.md`](https://github.com/Kataglyphis/ANTfrastructure/blob/develop/AGENTS.md#comments-one-line-only-the-why)
  and linked from `AGENTS.md`: 27 files lose their comment blocks, and code is unchanged.
  ANTfrastructure moves from `f65ccae9` to `497ba711` for the gate that grades every
  language and the bootstrap templates the two local copies follow. Its `versions.env`
  pins ruff at 0.16.8, so `pyproject.toml`, `.pre-commit-config.yaml` and `uv.lock`
  follow (0.16.7 and 0.16.8 report the same findings here).
- **The Linux lane runs on 3.14 again, and atheris is 3.1.0.** The 3.13 pin of
  2026-09-15 (below, under *Fixed*) existed because atheris 3.0.0 shipped no
  cp314 wheel. atheris 3.1.0 ships cp312, cp313 and cp314 wheels, so `uv.lock`
  moves to it and the lane's tests, static analysis, docs and packaging run on
  3.14, the image's interpreter; 3.14t stays experimental. The marker gains
  `python_version >= '3.12'`, because 3.1.0 has no sdist and no cp310/cp311
  wheel. A source build is still no way out: atheris' `find_libfuzzer.sh` looks
  for `lib/linux/libclang_rt.fuzzer_no_main-x86_64.a`, which the family image's
  per-target compiler-rt layout does not provide, and 3.0.0 refuses to import
  on 3.14 even once built with `LIBFUZZER_LIB` (measured 2026-09-29).
- **The Linux wrappers no longer unset `VIRTUAL_ENV`/`UV_PYTHON`.** The family
  image stopped exporting both with hub CON18 (`:latest` of 2026-09-29), so
  `ci_tests.sh` and `ci_static_analysis.sh` dropped the lines described under
  *Fixed* below; `UV_PROJECT_ENVIRONMENT` in the latter stays, because the
  driver still never activates the venv it creates.
- **2026-09-25: one workflow per platform + arch, and every lane a thin caller.**
  `ubuntu-26.04-amd64-arm64.yml` is split into `linux-x64.yml` ("Linux x64 · build
  + test") and `linux-arm64.yml` ("Linux arm64 · build + test"), both calling
  ANTfrastructure's `python-ci-linux.yml` with `arches: x64` / `arches: arm64`. The
  docs deploy stays on the x64 row, so only that file passes the FTP secrets.
  `lint-gates.yml` now calls the hub's reusable lint lane with `ratchets: true`,
  which runs what `scripts/linux/run-lint-gates.sh` runs locally; its header had
  asked for exactly this switch the day that lane existed. The README badges
  follow the new files.
- **2026-09-25: ANTfrastructure's reusable workflows and composite actions are
  called at `@develop`**, no longer `@main` as the older entry below says. Since
  2026-09-16 every lane also runs on pushes and pull requests to `develop`, not
  only `main`. The hub pin is `f65ccae9` (2026-09-16), which is on the hub's
  `main`, as is the `3c83a5e3` the NOTE below warns about.
- **2026-09-24: the workflows follow the family naming convention** (owner
  decision). `windows-2025.yml` is `windows-x64.yml` ("Windows x64 · build +
  test") and the lint lane's display name is plain `Lint gates`, as in every
  other repo. Triggers, jobs and job ids are unchanged; the README badges
  follow the new file. `ubuntu-26.04-amd64-arm64.yml` keeps its name for now:
  its split into `linux-x64.yml` and `linux-arm64.yml` needs a hub
  reusable-lane input that is not on hub `main` yet.
- **The hub pin moved to ANTfrastructure `3c83a5e3`** (from the published
  `72730743`). The published hub still listed WebDavClient under `unconfirmed`
  in its `.github/consumers.json`, and the workflow-conventions gate refuses a
  tree it cannot key its allow rows to, so that gate could not pass at the old
  pin at all. NOTE: `3c83a5e3` is NOT PUSHED anywhere yet — do not push this
  repo before ANTfrastructure is, or the gitlink resolves to nothing.
- `scripts/linux/lib/antfrastructure.sh` re-synced against the new pin (hub
  commit `08137b27` rewrote the template). `ANTFRASTRUCTURE_DIR` now resolves
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
- **Every compiled module builds with clang-cl on Windows; the first one used MSVC's `cl` until now
  (2026-10-12).** `ClangBuildExt` set the compiler's `cc` to `clang-cl` before the first `compile()`,
  which then ran `initialize()` and put `cl.exe` back, so `kataglyphis_webdavclient/dummy.c` compiled
  and linked with MSVC's tools in every Windows build (run 38214955666). `build_extension` now
  initializes the compiler first. The `spawn` hook meant to catch this is gone: setuptools 84 never
  calls it.
- **One loguru file sink per log file, not one per client (2026-10-11).** Every
  `WebDavClient()` called `logger.add("logs/downloadMd_s.log")`. Eight clients built on eight
  threads wrote each line eight times and rotated the file eight times (measured on 3.14t).
  The sinks are now a lock-guarded module set keyed by absolute path. That is the only mutable
  module state the thread-safety audit found, and `freethreading_compatible=True` rests on it.
- **Downloads are renamed into place (2026-10-11).** Each file streams into a private
  `.<name>.<uuid>.part` beside it, then replaces the target. Threads that share a destination
  no longer truncate each other's file, and the response is closed on every status.
  Windows denies a replace while another thread replaces the same target, and the first CI
  run failed with `PermissionError` on windows-11-arm (run 38142999677). There the replace
  retries for up to about 4 s; elsewhere the error is final.
- **Wheels ship only the package (2026-10-11).** `[tool.setuptools.packages.find]` had no
  `include`, so namespace discovery packed `third_party/`, `scripts/` and `images/`, 218
  packages, into every wheel. The pure wheel drops from 363 KB to 12 KB.
- **`cythonize(force=True)` (2026-10-11).** An in-tree `.c` left by an earlier build was reused
  as is, so a changed compiler directive did not reach the next wheel.
- **CI tests the WebDAV client again** (2026-10-01).
  - Every lane now runs the whole configured suite: all 10 tests, including the 6
    `test_webdav_client.py` tests against the mock server and the integration test.
  - Since 2025-10-20 all lanes had run `tests/unit` only (3 dummy tests). Before that, the
    single Linux x64 lane ran all of `tests/`.
  - The free-threaded 3.14t leg now really tests: it syncs only the tests extra and gates.
    Before, it synced nothing and passed on a warning.
  - Two dependency changes make that possible:
    - atheris is removed. Nothing used it, and it has no cp314t wheel.
    - bcrypt is overridden to >=5. wsgidav caps it below 5, and 4.x has no free-threaded
      wheel; the mock server runs without auth.
  - Windows gates on every leg instead of letting 3.14 and up fail.
  - py-spy and line_profiler leave the tests extra on Windows arm64
    (`platform_machine != 'ARM64'`). py-spy has no win_arm64 wheel, and line_profiler has
    none for 3.14t. No test imports either, so the lock now resolves from wheels alone
    there, for the arm64 test job that comes next.
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
  Invisible until the pin reached `d339cd52`: upstream ran those six behind
  `|| true` until 2026-09-08.
- The two findings that surfaced once the analysers ran for real, fixed rather
  than ignored: `ruff` CPY001 over twelve files (the MIT `LICENSE`'s notice now
  heads each one), and `vulture` on `myst_heading_anchors`, which was the one
  Sphinx setting missing from `conf.py`'s own `_SPHINX_EXPORTS` tuple.

### Security
- **The open Dependabot alerts in `uv.lock` are fixed** (2026-10-01), with
  `uv lock --upgrade-package` for exactly the affected packages:
  - wsgidav 4.3.3 → 4.3.5, which adds bcrypt and passlib;
  - lxml 6.0.2 → 6.1.3;
  - urllib3 2.6.3 → 2.8.0;
  - soupsieve 2.8.3 → 2.10;
  - requests 2.32.5 → 2.34.2;
  - idna 3.11 → 3.20;
  - setuptools 82.0.1 → 84.0.0;
  - pygments 2.19.2 → 2.21.0;
  - virtualenv 21.2.0 → 21.14.2, which brings python-discovery 1.1.3 → 1.6.1. GitHub only
    raised this alert after rescanning the updated lock.

  The five Dependabot PRs merged the same day (#22–#26) had already moved pytest past its
  advisory.

---

No version has been released yet: `VERSION.txt` reads `0.0.1`, and the
repository carries no tags (2026-09-25).

<!-- Add past versions below this line -->

<!-- Example:
## [0.9.0] - 2024-01-15

### Added
- Beta release features.
-->

---

<!-- Links for diffs -->
[Unreleased]: https://github.com/Kataglyphis/WebDavClient/compare/v0.10.1...HEAD
[0.10.1]: https://github.com/Kataglyphis/WebDavClient/compare/v0.10.0...v0.10.1
