#!/usr/bin/env bash
# ci_tests.sh - project wrapper around ANTfrastructure's generic Python CI test
# runner (linux/scripts/02-toolchain/python/ci_tests.sh).
#
# The local copy defaulted PACKAGE_NAME to 'orchestr_ant_ion' - the SIBLING
# project's name, copy-pasted. It only ever worked because CI derives the name
# explicitly. Upstream derives it from pyproject.toml, so that cannot recur.
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/antfrastructure.sh"

# UV_PYTHON OUTRANKS THE VENV THE DRIVER JUST ACTIVATED. This image exports
# UV_PYTHON=/opt/venv/bin/python, and upstream's uv_run is `uv run --active`
# with it still in scope - so on any interpreter but the image's own, uv finds
# the mismatch, DELETES the freshly synced .venv-<ver> and rebuilds it with
# /opt/venv's CPython and default groups only. `pytest` lives in the `tests`
# EXTRA, so it is not in that set and the run dies with
# "Failed to spawn: `pytest`" (reproduced locally on 3.13). The matrix only ever
# escaped this by testing the one version the image happens to ship.
# uv_sync_project clears exactly this variable for its own call and says why;
# uv_run does not. Drop this when it does.
unset UV_PYTHON

antfrastructure_exec "linux/scripts/02-toolchain/python/ci_tests.sh" "$@"
