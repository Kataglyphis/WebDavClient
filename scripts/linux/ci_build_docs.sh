#!/usr/bin/env bash
# Wrapper around ANTfrastructure's linux/scripts/02-toolchain/python/ci_build_docs.sh.
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/antfrastructure.sh"

antfrastructure_exec "linux/scripts/02-toolchain/python/ci_build_docs.sh" "$@"
