#!/usr/bin/env python3
"""Validate generated Dubnium book output before public deployment."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ALLOWED_SUFFIXES = {
    ".html", ".css", ".js", ".json", ".svg", ".png", ".jpg", ".jpeg",
    ".webp", ".gif", ".woff", ".woff2", ".ttf", ".eot", ".txt", ".map",
}
ALLOWED_BASENAMES = {".nojekyll"}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
PUBLICATION_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{7,127}$")
RFC3339_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")
PRIVATE_METADATA_FIELDS = {
    "source_repository",
    "source_commit",
    "source_path",
    "workflow_id",
    "workflow_run_id",
    "job_id",
}
PRIVATE_PATTERNS = {
    "private repository URL": re.compile(r"github\.com/ryjen/dubnium(?:/|$)", re.I),
    "private edit link": re.compile(r"github\.com/ryjen/dubnium/edit/", re.I),
    "internal documentation path": re.compile(r"docs/internal|/internal/", re.I),
    "private IPv4 address": re.compile(
        r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b"
    ),
    "absolute home path": re.compile(r"/(?:home|Users)/[A-Za-z0-9._-]+/"),
    "secret-like assignment": re.compile(r"\b(?:TOKEN|PASSWORD|SECRET|PRIVATE_KEY)\s*=\s*[^\s<]+", re.I),
}
LOCALHOST_ENDPOINT = re.compile(
    r"(?:https?://)?(?:localhost|127\.0\.0\.1)(?::\d+)?",
    re.I,
)
HTML_URL_ATTRIBUTE = re.compile(
    r'''\b(?:href|src|action)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+))''',
    re.I | re.S,
)
MERMAID_BUNDLE = re.compile(r"^mermaid-[0-9a-f]+\.min\.js$", re.I)
SEARCH_INDEX = re.compile(r"^searchindex-[0-9a-f]+\.js$", re.I)
TEXT_SUFFIXES = {".html", ".css", ".js", ".json", ".svg", ".txt", ".map"}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def normalized_changed_paths(paths: list[str]) -> list[str]:
    return [path.strip().lstrip("./") for path in paths if path.strip()]


def validate_changed_paths(paths: list[str]) -> list[str]:
    normalized = normalized_changed_paths(paths)
    if not any(path == "site/docs" or path.startswith("site/docs/") for path in normalized):
        return []
    unexpected = sorted(
        path for path in normalized
        if path != "site/docs" and not path.startswith("site/docs/")
    )
    if not unexpected:
        return []
    return ["publication changes must be confined to site/docs/: " + ", ".join(unexpected)]


def publication_metadata_changed(paths: list[str]) -> bool:
    return "site/docs/publication.json" in normalized_changed_paths(paths)


def contains_localhost_endpoint(relative: Path, suffix: str, text: str) -> bool:
    if SEARCH_INDEX.fullmatch(relative.name):
        return False
    if suffix == ".html":
        for match in HTML_URL_ATTRIBUTE.finditer(text):
            value = next(group for group in match.groups() if group is not None)
            if LOCALHOST_ENDPOINT.search(value):
                return True
        return False
    return bool(LOCALHOST_ENDPOINT.search(text))


def should_scan_private(relative: Path, label: str) -> bool:
    return not (
        label == "secret-like assignment"
        and MERMAID_BUNDLE.fullmatch(relative.name)
    )


def validate_public_metadata(metadata: dict[object, object], errors: list[str]) -> None:
    required_fields = {
        "schema_version",
        "publication_id",
        "content_digest",
        "generator",
        "generated_at",
    }
    missing = sorted(required_fields - metadata.keys())
    if missing:
        fail(errors, f"publication.json missing public fields: {', '.join(missing)}")

    if metadata.get("schema_version") != 2:
        fail(errors, "publication.json schema_version must be 2")
    if not PUBLICATION_ID_RE.fullmatch(str(metadata.get("publication_id", ""))):
        fail(errors, "publication.json publication_id has invalid syntax")
    if not SHA256_RE.fullmatch(str(metadata.get("content_digest", ""))):
        fail(errors, "publication.json content_digest must be sha256:<64 lowercase hex characters>")
    if not str(metadata.get("generator", "")).startswith("mdbook "):
        fail(errors, "publication.json generator must identify an mdbook version")
    if not RFC3339_RE.fullmatch(str(metadata.get("generated_at", ""))):
        fail(errors, "publication.json generated_at must be UTC RFC 3339")

    leaked_fields = sorted(PRIVATE_METADATA_FIELDS & metadata.keys())
    if leaked_fields:
        fail(errors, "publication.json public schema forbids private provenance fields: " + ", ".join(leaked_fields))


def validate_legacy_metadata(metadata: dict[object, object], errors: list[str]) -> None:
    required_fields = {"source_repository", "source_commit", "generator", "generated_at"}
    missing = sorted(required_fields - metadata.keys())
    if missing:
        fail(errors, f"publication.json missing legacy fields: {', '.join(missing)}")
    if not str(metadata.get("source_repository", "")).strip():
        fail(errors, "publication.json legacy source_repository must be non-empty")
    if not SHA_RE.fullmatch(str(metadata.get("source_commit", ""))):
        fail(errors, "publication.json legacy source_commit must be a full lowercase SHA-1")
    if not str(metadata.get("generator", "")).startswith("mdbook "):
        fail(errors, "publication.json generator must identify an mdbook version")
    if not RFC3339_RE.fullmatch(str(metadata.get("generated_at", ""))):
        fail(errors, "publication.json generated_at must be UTC RFC 3339")


def validate(root: Path, *, require_public_schema: bool = False) -> list[str]:
    errors: list[str] = []
    docs = root / "site" / "docs"
    if not docs.exists():
        return errors
    if docs.is_symlink():
        return ["site/docs must not be a symlink"]

    for path in (docs / "index.html", docs / "publication.json"):
        if not path.is_file():
            fail(errors, f"missing required file: {path.relative_to(root)}")

    metadata_path = docs / "publication.json"
    if metadata_path.is_file():
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            fail(errors, f"invalid publication.json: {exc}")
        else:
            if not isinstance(metadata, dict):
                fail(errors, "publication.json must contain a JSON object")
            elif metadata.get("schema_version") == 2:
                validate_public_metadata(metadata, errors)
            elif require_public_schema:
                fail(errors, "changed publications must use publication.json schema_version 2")
            else:
                validate_legacy_metadata(metadata, errors)

    for path in docs.rglob("*"):
        relative = path.relative_to(root)
        if path.is_symlink():
            fail(errors, f"symlinks are not allowed: {relative}")
            continue
        if not path.is_file():
            continue
        if path.name in ALLOWED_BASENAMES:
            continue
        suffix = path.suffix.lower()
        if suffix not in ALLOWED_SUFFIXES:
            fail(errors, f"unexpected generated file type: {relative}")
            continue
        if suffix not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            fail(errors, f"expected UTF-8 text file: {relative}")
            continue
        if contains_localhost_endpoint(relative, suffix, text):
            fail(errors, f"{relative}: contains localhost endpoint")
        for label, pattern in PRIVATE_PATTERNS.items():
            if should_scan_private(relative, label) and pattern.search(text):
                fail(errors, f"{relative}: contains {label}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--changed-paths-stdin", action="store_true")
    args = parser.parse_args()

    changed_paths = sys.stdin.read().splitlines() if args.changed_paths_stdin else []
    errors = validate(
        Path(args.root).resolve(),
        require_public_schema=publication_metadata_changed(changed_paths),
    )
    if args.changed_paths_stdin:
        errors.extend(validate_changed_paths(changed_paths))
    if errors:
        print("Public book publication validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Public book publication boundary validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
