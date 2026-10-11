#!/usr/bin/env bash
# Reproducible public-workflow syntax and semantics check.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

if [[ "$(uname -s)" != Linux || "$(uname -m)" != x86_64 ]]; then
  echo "workflow syntax check requires Linux x86_64 (the public CI runner target)" >&2
  exit 1
fi

version=1.7.7
archive="actionlint_${version}_linux_amd64.tar.gz"
checksum=023070a287cd8cccd71515fedc843f1985bf96c436b7effaecce67290e7e0757
temp_dir="$(mktemp -d "${TMPDIR:-/tmp}/dubnium-actionlint.XXXXXXXX")"
trap 'rm -rf -- "$temp_dir"' EXIT

curl --fail --location --silent --show-error --retry 2 --connect-timeout 10 --max-time 60 \
  "https://github.com/rhysd/actionlint/releases/download/v${version}/${archive}" \
  --output "$temp_dir/$archive"

if ! printf '%s  %s\n' "$checksum" "$temp_dir/$archive" | sha256sum --check --status; then
  echo "actionlint release archive checksum verification failed" >&2
  exit 1
fi

# Extract only the verified executable, not arbitrary paths from the archive.
python3 - "$temp_dir/$archive" "$temp_dir/actionlint" <<'PY'
import shutil
import sys
import tarfile

with tarfile.open(sys.argv[1], "r:gz") as archive_file:
    member = archive_file.getmember("actionlint")
    if not member.isfile():
        raise ValueError("expected actionlint executable")
    source = archive_file.extractfile(member)
    if source is None:
        raise ValueError("missing actionlint executable")
    with source, open(sys.argv[2], "wb") as destination:
        shutil.copyfileobj(source, destination)
PY
chmod 700 "$temp_dir/actionlint"

mapfile -d '' workflows < <(
  find .github/workflows -maxdepth 1 -type f \( -name '*.yml' -o -name '*.yaml' \) -print0 | sort -z
)
if ((${#workflows[@]} == 0)); then
  echo "no GitHub Actions workflow files found" >&2
  exit 1
fi

"$temp_dir/actionlint" -oneline "${workflows[@]}"

fixture=tests/fixtures/workflows/invalid-multiline-run.yml
if "$temp_dir/actionlint" -oneline \
  -stdin-filename .github/workflows/invalid-multiline-run.yml - \
  < "$fixture" > "$temp_dir/fixture.log" 2>&1; then
  echo "actionlint failed open on the malformed workflow regression fixture" >&2
  exit 1
fi
if ! grep -q 'could not parse as YAML' "$temp_dir/fixture.log"; then
  echo "malformed workflow fixture was rejected for the wrong reason" >&2
  cat "$temp_dir/fixture.log" >&2
  exit 1
fi

echo "GitHub Actions workflow syntax, semantics, and negative regression fixture passed"
