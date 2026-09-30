#!/usr/bin/env bash
# Sourced, not exec'd: the upstream driver exports toolchain paths into the calling shell.
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/antfrastructure.sh"

antfrastructure_source "linux/scripts/02-toolchain/setup-dependencies.sh"
