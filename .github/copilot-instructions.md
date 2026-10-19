# Copilot instructions

[`AGENTS.md`](../AGENTS.md) is this repository's rulebook; read it before suggesting a change.
This file only names the five rules a suggestion breaks most easily:

1. **`scripts/linux/*.sh` are wrappers over ANTfrastructure**, all but `collect-release-assets.sh`:
   change behaviour upstream, never in the wrapper. `scripts/linux/lib/antfrastructure.sh` and
   `scripts/windows/Resolve-BuildModule.ps1` are synced from the hub's templates; never hand-edit
   them ([§ 2](../AGENTS.md#2-what-antfrastructure-owns--links-only)).
2. **Module-level mutable state needs a lock.** Every module is compiled with Cython and the cp314t
   wheel runs it with the GIL off, so a new cache, global or lazily built object comes with a lock
   and a test in `tests/` that drives it from threads
   ([§ 3](../AGENTS.md#3-pitfalls-specific-to-this-project)).
3. **No `PACKAGE_NAME` default in a wrapper, and `packages.find` keeps its `include`**: the
   first pointed at the sibling project, the second shipped `third_party/` in every wheel (§ 3).
4. **Edit the root `README.md` and `CHANGELOG.md`**, then re-sync their copies in `docs/source/`
   in the same commit; the version lives in `VERSION.txt` only
   ([§ 5](../AGENTS.md#5-docs-owned-by-this-repo)).
5. **Comments: one line, only the why**; the comment-size gate fails longer blocks
   ([hub `AGENTS.md`](../third_party/ANTfrastructure/AGENTS.md#comments-one-line-only-the-why)).
