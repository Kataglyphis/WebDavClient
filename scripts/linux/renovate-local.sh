#!/usr/bin/env bash
# Keep policy in the hub driver; see docs/source/getting-started.md#dependency-updates.
set -euo pipefail

_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# ADJUST: scripts/linux/lib/ in platform-split consumers, scripts/lib/ in flat Flutter ones.
source "${_SCRIPT_DIR}/lib/antfrastructure.sh"

# The copied bootstrap initializes the hub only for a real apply.
antfrastructure_renovate_exec linux/scripts/renovate-local.sh "$KATAGLYPHIS_REPO_ROOT" "$@"
