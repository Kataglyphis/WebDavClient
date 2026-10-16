#!/usr/bin/env bash
# collect-release-assets.sh <artifacts dir> <out dir>: the lanes' wheels and sdist, flat and uniquely named, for a GitHub release.
set -euo pipefail

artifacts="${1:?usage: collect-release-assets.sh <artifacts dir> <out dir>}"
out="${2:?usage: collect-release-assets.sh <artifacts dir> <out dir>}"
mkdir -p "$out"
# Absolute, so every step below means the same folder whatever its working directory.
out="$(cd "$out" && pwd)"

# put <file>: one release file; a second one of the same name would silently replace the first.
put() {
  if [ -e "${out}/$(basename "$1")" ]; then
    printf 'two artifacts carry %s\n' "$(basename "$1")" >&2
    exit 1
  fi
  cp "$1" "${out}/"
}

for dir in "$artifacts"/*/; do
  name="$(basename "$dir")"
  # Test reports, coverage and logs are no deliverable.
  case "$name" in test-reports-*) continue ;; esac
  while IFS= read -r -d '' file; do
    case "$(basename "$file")" in
      # Every lane builds the pure wheel and the sdist under one name; Linux x64's copy ships.
      *-py3-none-any.whl|*.tar.gz) case "$name" in packages-linux-x64-*) put "$file" ;; esac ;;
      *.whl) put "$file" ;;
    esac
  done < <(find "$dir" -type f \( -name '*.whl' -o -name '*.tar.gz' \) -not -path '*/docs/*' -not -path '*/logs/*' -print0)
done

if [ -z "$(ls -A "$out")" ]; then
  printf 'no packages under %s\n' "$artifacts" >&2
  exit 1
fi
ls -1 "$out"
