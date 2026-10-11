#!/usr/bin/env bash
# The whole pytest suite against the installed free-threaded wheel: the 3.14t test leg runs the sources, this runs the Cython build.
# Usage: test-free-threaded-wheel.sh [free-threaded version, default 3.14t]; run from ci_packaging.sh after the hub driver filled dist/.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${root}"
ft_version="${1:-3.14t}"

if [ "${PYTHON_FREE_THREADED_WHEEL:-auto}" = off ] || [ -n "${PACKAGING_CROSS_TARGET:-}" ]; then
  echo "[INFO] free-threaded wheel tests skipped: this run builds no free-threaded wheel"
  exit 0
fi

abi="cp$(printf '%s' "${ft_version%t}" | tr -d .)t"
shopt -s nullglob
wheels=(dist/*-"${abi}"-*.whl)
if [ "${#wheels[@]}" -ne 1 ]; then
  echo "[ERROR] expected one ${abi} wheel in dist/, found ${#wheels[@]}" >&2
  exit 1
fi

python="$(UV_PYTHON_DOWNLOADS=never uv python find "${ft_version}")"
work="$(mktemp -d)"
trap 'rm -rf "${work}"' EXIT

uv venv --python "${python}" "${work}/venv"
uv export --frozen --no-emit-project --extra tests --format requirements.txt -o "${work}/requirements.txt" >/dev/null
uv pip install --python "${work}/venv/bin/python" -r "${work}/requirements.txt"
uv pip install --python "${work}/venv/bin/python" --no-deps "${wheels[0]}"

# A copy without the package directory: run from the checkout, the sources would shadow the installed modules.
mkdir "${work}/run"
cp -r tests pytest.ini "${work}/run/"
cd "${work}/run"
echo "[INFO] free-threaded wheel tests: ${wheels[0]##*/} on ${python}"
KATAGLYPHIS_EXPECT_COMPILED=1 "${work}/venv/bin/python" -m pytest -p no:cacheprovider -v
