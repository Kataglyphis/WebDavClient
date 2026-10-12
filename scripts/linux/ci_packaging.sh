#!/usr/bin/env bash
# Wrapper around the hub's python/ci_packaging.sh; patchelf stays local because no second consumer needs it.
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/antfrastructure.sh"

if ! command -v patchelf >/dev/null 2>&1; then
  echo "[INFO] Installing patchelf (needed to repair the binary wheel's RPATHs)"
  SUDO=""
  if [ "$(id -u)" -ne 0 ] && command -v sudo >/dev/null 2>&1; then SUDO="sudo"; fi
  $SUDO apt-get update -y && $SUDO apt-get install -y patchelf
fi

driver="$(antfrastructure_path "linux/scripts/02-toolchain/python/ci_packaging.sh")"
export WORKSPACE_ROOT="${WORKSPACE_ROOT:-$KATAGLYPHIS_REPO_ROOT}"
bash "${driver}" "$@"

# The hub proves the cp314t wheel only by loading its modules; this runs the suite on them.
bash "$(antfrastructure_path "linux/scripts/02-toolchain/python/test-free-threaded-wheel.sh")" --python-version "${1:-3.14}" \
  --extra tests --copy tests --copy pytest.ini --env KATAGLYPHIS_EXPECT_COMPILED=1 -- -v
