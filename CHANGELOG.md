# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `scripts/linux/run-lint-gates.sh` and `.github/workflows/lint-gates.yml`: the
  family lint lane. Six gates over the tracked tree — shell lint, workflow lint
  plus the CI image-ref check, secret scan, `ruff`, the shared-config drift
  check and the consumer pin-forwarding check — all owned by ANTfrastructure's
  `linux/scripts/run-lint-gates.sh`. Before this the repo had no shell,
  workflow or secret linting at all.
- `.antfrastructure-shared.manifest`: declares the two upstream files this repo
  holds a copy of (`antfrastructure-sh`, `resolve-build-module`) so the
  shared-config gate compares them instead of trusting the word "verbatim" in a
  header. `.gitignore` had to un-ignore it — the PyInstaller `*.manifest` rule
  is unanchored.
- `.github/actionlint.yaml`: teaches the pinned actionlint the `ubuntu-26.04`
  runner labels it predates.

### Changed
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
- Placeholder for any bug fixes.

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
