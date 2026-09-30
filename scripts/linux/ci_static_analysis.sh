#!/usr/bin/env bash
# Wrapper around ANTfrastructure's linux/scripts/02-toolchain/python/ci_static_analysis.sh.
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/antfrastructure.sh"

# The driver never activates the venv it creates, so `uv run --active` falls back to the project env named here.
WORKSPACE_ROOT="${WORKSPACE_ROOT:-$KATAGLYPHIS_REPO_ROOT}"
if [ -d /workspace ] && [ -f /workspace/pyproject.toml ]; then
  WORKSPACE_ROOT="/workspace"
fi
export WORKSPACE_ROOT
export UV_PROJECT_ENVIRONMENT="${WORKSPACE_ROOT}/.venv_static_analysis"

antfrastructure_exec "linux/scripts/02-toolchain/python/ci_static_analysis.sh" "$@"
