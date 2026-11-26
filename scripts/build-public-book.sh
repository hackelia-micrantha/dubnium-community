#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Resolve both tools from the same immutable published package-set version.
NIXPKGS='https://flakehub.com/f/DeterminateSystems/nixpkgs-weekly/=0.1.1119549'
nix shell "${NIXPKGS}#mdbook" "${NIXPKGS}#mdbook-mermaid" -c bash -euc '
  repo="$1"
  book_version="$(mdbook --version)"
  mermaid_version="$(mdbook-mermaid --version)"
  test "$book_version" = "mdbook v0.5.4"
  test "$mermaid_version" = "mdbook-mermaid 0.17.1"
  mdbook build "$repo"
  # Retain the checked-in generator label format for parity.
  printf "mdbook %s; mdbook-mermaid %s\\n" "$book_version" "$mermaid_version" >&2
  python3 "$repo/scripts/prepare_public_book.py" \
    --root "$repo" \
    --output "$repo/site/docs" \
    --generator "mdbook $book_version; mdbook-mermaid $mermaid_version" \
    --generated-at "$(git -C "$repo" show -s --format=%cI HEAD)"
' bash "$REPO_DIR"
