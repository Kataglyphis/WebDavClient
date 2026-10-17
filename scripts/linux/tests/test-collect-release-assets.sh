#!/usr/bin/env bash
# test-collect-release-assets.sh: collect-release-assets.sh against artifact trees shaped like the lanes' uploads.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
collect="${here}/../collect-release-assets.sh"
work="$(mktemp -d)"
trap 'rm -rf "${work}"' EXIT
fails=0
check() {
  if "${@:2}"; then printf 'ok    %s\n' "$1"; else printf 'FAIL  %s\n' "$1"; fails=$((fails + 1)); fi
}

a="${work}/artifacts"
p=kataglyphis_webdavclient-0.0.1
for pair in x64:x86_64 arm64:aarch64; do
  arch="${pair%%:*}" m="${pair##*:}" d="${a}/packages-linux-${pair%%:*}-source-and-binary"
  mkdir -p "${d}" "${a}/test-reports-${arch}"
  for abi in cp314-cp314 cp314-cp314t; do printf '%s' "${arch}" > "${d}/${p}-${abi}-manylinux2014_${m}.manylinux_2_17_${m}.whl"; done
  printf '%s' "${arch}" > "${d}/${p}-py3-none-any.whl"
  printf '%s' "${arch}" > "${d}/${p}.tar.gz"
  printf 'xml' > "${a}/test-reports-${arch}/report.xml"
done
w="${a}/python-package-windows-source-and-binaries"
mkdir -p "${w}/dist" "${w}/docs/test_results" "${w}/logs"
for abi in cp314-cp314 cp314-cp314t; do printf 'win' > "${w}/dist/${p}-${abi}-win_amd64.whl"; done
printf 'win' > "${w}/dist/${p}-py3-none-any.whl"
printf 'win' > "${w}/dist/${p}.tar.gz"
printf 'cov' > "${w}/docs/test_results/coverage-3.14.xml"
printf 'log' > "${w}/logs/build-windows.log"
wa="${a}/packages-windows-arm64-wheels"
mkdir -p "${wa}"
for abi in cp314-cp314 cp314-cp314t; do printf 'arm' > "${wa}/${p}-${abi}-win_arm64.whl"; done

out="${work}/release"
check "it collects, though all three lanes carry the pure wheel and the sdist" bash "${collect}" "${a}" "${out}"
check "the eight binary wheels, Windows arm64's two among them" test "$(find "${out}" -name '*-cp314-*.whl' | wc -l)" = 8
check "one pure wheel and one sdist, Linux x64's" test "$(cat "${out}/${p}-py3-none-any.whl")$(cat "${out}/${p}.tar.gz")" = x64x64
check "ten files and nothing else: no report, coverage or log" test "$(find "${out}" -type f | wc -l)" = 10
check "relative paths, as release.yml passes them" bash -c "cd '${work}' && bash '${collect}' artifacts release-relative >/dev/null && test -e release-relative/${p}-cp314-cp314t-win_amd64.whl"

mkdir -p "${a}/packages-linux-x64-copy"
cp "${w}/dist/${p}-cp314-cp314-win_amd64.whl" "${a}/packages-linux-x64-copy/"
check "two artifacts with one binary wheel fail rather than overwrite" bash -c "! bash '${collect}' '${a}' '${work}/release2' >/dev/null 2>&1"
mkdir -p "${work}/none/x"
check "no packages at all fail" bash -c "! bash '${collect}' '${work}/none' '${work}/release3' >/dev/null 2>&1"

if [ "${fails}" -gt 0 ]; then
  printf '%d of the collect checks failed\n' "${fails}"
  exit 1
fi
printf 'collect-release-assets: all checks passed\n'
