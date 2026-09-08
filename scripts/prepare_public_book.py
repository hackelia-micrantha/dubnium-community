#!/usr/bin/env python3
"""Validate and prepare the generated public Dubnium book artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

EXPECTED_SOURCE = Path("docs/external")
EXPECTED_DESTINATION = Path("site/docs")
PUBLIC_SUMMARY_TARGETS = {
    "README.md",
    "how-dubnium-works.md",
    "components.md",
    "operator-journey.md",
    "operator-tooling.md",
    "runner-controller.md",
    "runtime-modes.md",
    "writable-configuration.md",
    "principles.md",
    "vision.md",
    "architecture.md",
    "reproducibility.md",
    "observability.md",
    "ai-and-automation.md",
    "governance.md",
    "public-contracts.md",
    "status.md",
    "community.md",
}
PUBLIC_SOURCE_FILES = PUBLIC_SUMMARY_TARGETS | {"SUMMARY.md"}
ALLOWED_SUFFIXES = {
    ".html", ".css", ".js", ".json", ".svg", ".png", ".jpg", ".jpeg",
    ".webp", ".gif", ".woff", ".woff2", ".ttf", ".eot", ".txt",
}
ALLOWED_BASENAMES = {".nojekyll"}
TEXT_SUFFIXES = {".html", ".css", ".js", ".json", ".svg", ".txt"}
FORBIDDEN = {
    "private repository URL": re.compile(r"github\.com/ryjen/dubnium", re.I),
    "private issue reference": re.compile(r"\bryjen/dubnium#\d+\b", re.I),
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
SUMMARY_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
MERMAID_BUNDLE = re.compile(r"^mermaid-[0-9a-f]+\.min\.js$", re.I)
SEARCH_INDEX = re.compile(r"^searchindex-[0-9a-f]+\.js$", re.I)


def validate_source(root: Path) -> list[str]:
    errors: list[str] = []
    source = root / EXPECTED_SOURCE
    if not source.is_dir():
        return [f"missing public source directory: {EXPECTED_SOURCE}"]

    source_files: set[str] = set()
    for path in source.rglob("*"):
        if path.is_symlink():
            errors.append(f"public source symlink is not allowed: {path.relative_to(root)}")
        if "internal" in path.parts:
            errors.append(f"internal path entered public source graph: {path.relative_to(root)}")
        if path.is_file():
            source_files.add(path.relative_to(source).as_posix())

    unexpected_source_files = sorted(source_files - PUBLIC_SOURCE_FILES)
    if unexpected_source_files:
        errors.append(
            "public source contains unallowlisted files: " + ", ".join(unexpected_source_files)
        )

    summary = source / "SUMMARY.md"
    if not summary.is_file():
        errors.append("missing public source summary: docs/external/SUMMARY.md")
        return errors
    try:
        text = summary.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        errors.append("public source summary must be UTF-8")
        return errors

    targets = {
        target.split("#", 1)[0]
        for target in SUMMARY_LINK.findall(text)
        if target.split("#", 1)[0].endswith(".md")
    }
    unexpected = sorted(targets - PUBLIC_SUMMARY_TARGETS)
    missing = sorted(PUBLIC_SUMMARY_TARGETS - targets)
    if unexpected:
        errors.append("public SUMMARY references non-overview pages: " + ", ".join(unexpected))
    if missing:
        errors.append("public SUMMARY is missing required overview pages: " + ", ".join(missing))
    for target in sorted(PUBLIC_SUMMARY_TARGETS):
        if not (source / target).is_file():
            errors.append(f"public SUMMARY target is missing: {target}")
    return errors


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


def should_scan_forbidden(relative: Path, label: str) -> bool:
    return not (
        label == "secret-like assignment"
        and MERMAID_BUNDLE.fullmatch(relative.name)
    )


def validate_output(output: Path) -> list[str]:
    errors: list[str] = []
    if not (output / "index.html").is_file():
        errors.append("generated output is missing index.html")
    for path in output.rglob("*"):
        relative = path.relative_to(output)
        if path.is_symlink():
            errors.append(f"generated symlink is not allowed: {relative}")
            continue
        if not path.is_file():
            continue
        if path.name in ALLOWED_BASENAMES:
            continue
        suffix = path.suffix.lower()
        if suffix not in ALLOWED_SUFFIXES:
            errors.append(f"unexpected generated file type: {relative}")
            continue
        if suffix not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"expected UTF-8 generated file: {relative}")
            continue
        if contains_localhost_endpoint(relative, suffix, text):
            errors.append(f"{relative}: contains localhost endpoint")
        for label, pattern in FORBIDDEN.items():
            if should_scan_forbidden(relative, label) and pattern.search(text):
                errors.append(f"{relative}: contains {label}")
    return errors


def normalize_timestamp(value: str) -> str:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("generated timestamp must include a timezone")
    return parsed.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def calculate_content_digest(output: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(output.rglob("*")):
        if not path.is_file() or path.name == "publication.json":
            continue
        relative = path.relative_to(output).as_posix().encode("utf-8")
        content = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def write_provenance(output: Path, generator: str, generated_at: str) -> None:
    content_digest = calculate_content_digest(output)
    payload = {
        "schema_version": 2,
        "publication_id": f"dubnium-book-{content_digest[:20]}",
        "content_digest": f"sha256:{content_digest}",
        "generator": generator,
        "generated_at": normalize_timestamp(generated_at),
    }
    (output / "publication.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def replace_destination(output: Path, destination_root: Path) -> None:
    destination = destination_root / EXPECTED_DESTINATION
    if destination.resolve().parent != (destination_root / "site").resolve():
        raise ValueError("destination must resolve exactly beneath site/")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(output, destination)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--destination-root", type=Path)
    parser.add_argument("--generator", required=True)
    parser.add_argument("--generated-at", required=True)
    args = parser.parse_args()

    errors = validate_source(args.root.resolve())
    errors.extend(validate_output(args.output.resolve()))
    if errors:
        print("Public book preparation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    write_provenance(args.output, args.generator, args.generated_at)
    if args.destination_root:
        replace_destination(args.output.resolve(), args.destination_root.resolve())
    print("Public book artifact prepared")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
