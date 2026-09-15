#!/usr/bin/env bash
# ci_static_analysis.sh - project wrapper around ANTfrastructure's generic Python
# static-analysis runner (linux/scripts/02-toolchain/python/ci_static_analysis.sh).
#
# The local copy reimplemented the same codespell/bandit/vulture/ruff/ty pipeline
# with its own venv lifecycle. Upstream owns both and derives the package name
# from pyproject.toml.
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/antfrastructure.sh"

# THE UPSTREAM DRIVER NEVER ACTIVATES THE VENV IT CREATES: ci-common.sh's
# uv_venv_ensure activates only one that ALREADY existed, and a runner always
# takes the create path. Its gates then run through `uv run --active`, which
# binds this image's VIRTUAL_ENV=/opt/venv - root-owned, while the image is
# uid-1001 - so all six died identically and before running a single check:
# "failed to remove file `/opt/venv/...`: Permission denied" (run 35015680349,
# reproduced locally in the same image). ci_build_docs.sh carries the one-line
# uv_venv_activate this driver is missing; until that lands upstream, clearing
# the two image variables and naming the environment has the same effect.
# WORKSPACE_ROOT is derived by detect_workspace's own rule, not a second opinion.
WORKSPACE_ROOT="${WORKSPACE_ROOT:-$KATAGLYPHIS_REPO_ROOT}"
if [ -d /workspace ] && [ -f /workspace/pyproject.toml ]; then
  WORKSPACE_ROOT="/workspace"
fi
export WORKSPACE_ROOT
export UV_PROJECT_ENVIRONMENT="${WORKSPACE_ROOT}/.venv_static_analysis"
unset VIRTUAL_ENV UV_PYTHON

antfrastructure_exec "linux/scripts/02-toolchain/python/ci_static_analysis.sh" "$@"
