#!/usr/bin/env bash
# setup-dependencies.sh - project wrapper around ANTfrastructure's dependency
# installer (linux/scripts/02-toolchain/setup-dependencies.sh).
#
# SOURCED, not exec'd: the upstream driver exports toolchain paths into the
# calling shell, so `. scripts/linux/setup-dependencies.sh` is the documented
# use and antfrastructure_exec would throw those exports away with the process.
#
# The hand-rolled resolver this replaced repeated the submodule path, the
# not-found guard and the hint text inline - and had already pointed at a driver
# path that moved upstream, failing with nothing but bash's "No such file or
# directory". antfrastructure_source owns all three now, so the next upstream
# move fails with an actionable message instead.
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/antfrastructure.sh"

antfrastructure_source "linux/scripts/02-toolchain/setup-dependencies.sh"
