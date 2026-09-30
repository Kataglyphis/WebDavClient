#!/usr/bin/env bash
# The hub lint aggregator over this repo; --ratchets is passed here so the owner and CI run the same gate.
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/antfrastructure.sh"

antfrastructure_exec "linux/scripts/run-lint-gates.sh" "$KATAGLYPHIS_REPO_ROOT" --ratchets "$@"
