#!/usr/bin/env bash
# ci_static_analysis.sh - project wrapper around ANTfrastructure's generic Python
# static-analysis runner (linux/scripts/02-toolchain/python/ci_static_analysis.sh).
#
# The local copy reimplemented the same codespell/bandit/vulture/ruff/ty pipeline
# with its own venv lifecycle. Upstream owns both and derives the package name
# from pyproject.toml.
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/antfrastructure.sh"

# THE UPSTREAM DRIVER NEVER ACTIVATES THE VENV IT CREATES: uv_venv_ensure
# activates only one that ALREADY existed, and a runner always creates. Its
# gates run `uv run --active`, which with no active venv falls back to the
# project environment - so name it as the venv the driver just created (what
# ci_build_docs.sh's uv_venv_activate does). The `unset VIRTUAL_ENV UV_PYTHON`
# that sat here went once the image stopped exporting both (hub CON18, `:latest`
# of 2026-09-29): they aimed uv at the root-owned /opt/venv (run 35015680349).
# WORKSPACE_ROOT is derived by detect_workspace's own rule, not a second opinion.
WORKSPACE_ROOT="${WORKSPACE_ROOT:-$KATAGLYPHIS_REPO_ROOT}"
if [ -d /workspace ] && [ -f /workspace/pyproject.toml ]; then
  WORKSPACE_ROOT="/workspace"
fi
export WORKSPACE_ROOT
export UV_PROJECT_ENVIRONMENT="${WORKSPACE_ROOT}/.venv_static_analysis"

antfrastructure_exec "linux/scripts/02-toolchain/python/ci_static_analysis.sh" "$@"
