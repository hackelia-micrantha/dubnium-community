#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"

nix shell nixpkgs#mdbook nixpkgs#mdbook-mermaid -c mdbook build "$REPO_DIR"
python3 "$REPO_DIR/scripts/prepare_public_book.py" \
  --root "$REPO_DIR" \
  --output "$REPO_DIR/site/docs" \
  --generator "$(nix shell nixpkgs#mdbook nixpkgs#mdbook-mermaid -c sh -c 'printf "mdbook %s; mdbook-mermaid %s" "$(mdbook --version | awk "{print $2}")" "$(mdbook-mermaid --version | awk "{print $2}")"')" \
  --generated-at "$(git -C "$REPO_DIR" show -s --format=%cI HEAD)"
