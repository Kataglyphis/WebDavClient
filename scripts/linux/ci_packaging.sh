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

antfrastructure_exec "linux/scripts/02-toolchain/python/ci_packaging.sh" "$@"
