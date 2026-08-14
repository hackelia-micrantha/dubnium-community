#!/usr/bin/env python3
"""Lightweight public-repository architecture and disclosure checks."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = {
    "README.md",
    "LICENSE",
    "NOTICE",
    "LICENSING.md",
    "THIRD_PARTY_NOTICES.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "GOVERNANCE.md",
    "TRADEMARKS.md",
    "COMPATIBILITY.md",
    "ROADMAP.md",
    "package.json",
    "wrangler.jsonc",
    ".github/CODEOWNERS",
    ".github/dependabot.yml",
    ".github/workflows/contract-ci.yml",
    "docs/repository-layout.md",
    "docs/content-markers.md",
    "docs/publication-review.md",
    "docs/publication-boundary.md",
    "docs/standards.md",
    "docs/ci-security.md",
    "docs/branch-protection.md",
    "docs/release-integrity.md",
    "scripts/classify_changes.py",
    "scripts/check_contract_tree.py",
    "scripts/check_workflow_security.py",
}

PUBLIC_ROOTS = {
    "spec",
    "schemas",
    "api",
    "packages",
    "conformance",
    "reference",
    "examples",
    "policy-examples",
    "changes",
    "release",
}

MARKED_POLICY_FILES = {
    "LICENSING.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "GOVERNANCE.md",
    "TRADEMARKS.md",
    "COMPATIBILITY.md",
    "ROADMAP.md",
    "docs/repository-layout.md",
    "docs/content-markers.md",
    "docs/publication-review.md",
    "docs/publication-boundary.md",
    "docs/standards.md",
    "docs/ci-security.md",
    "docs/branch-protection.md",
    "docs/release-integrity.md",
}

PRIVATE_OWNER_REPOSITORY_PATTERN = re.compile(
    r"github\.com/ryjen/[A-Za-z0-9_.-]+(?:\.git)?(?:/|$)", re.I
)
PRIVATE_OWNER_ISSUE_PATTERN = re.compile(r"\bryjen/[A-Za-z0-9_.-]+#\d+\b", re.I)

PROHIBITED_PUBLIC_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("SSH Git dependency", re.compile(r"(?:git\+ssh://|ssh://git@|git@[^\s:]+:)", re.I)),
    ("local file dependency", re.compile(r"(?:file://|file:\.\.?/|path\s*=\s*[\"']?/)", re.I)),
    ("local home path", re.compile(r"(?:/home/|/Users/|[A-Z]:\\\\Users\\\\)", re.I)),
    ("loopback endpoint", re.compile(r"(?:localhost|127\.0\.0\.1|\[::1\])", re.I)),
    ("private IPv4 endpoint", re.compile(r"(?:10\.(?:\d{1,3}\.){2}\d{1,3}|192\.168\.(?:\d{1,3}\.)\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.(?:\d{1,3}\.)\d{1,3})")),
    ("private-owner repository coordinate", PRIVATE_OWNER_REPOSITORY_PATTERN),
    ("private-owner issue coordinate", PRIVATE_OWNER_ISSUE_PATTERN),
)

MARKER_PATTERN = re.compile(
    r"^Status: (?:experimental|v1alpha|v1beta|stable)$.*?"
    r"^Content: (?:normative|informative)$.*?"
    r"^Canonical source: .+$.*?"
    r"^Generated: (?:no|yes from .+)$",
    re.M | re.S,
)

CLOUDFLARE_WORKER_NAME = "dubnium"
CLOUDFLARE_COMPATIBILITY_DATE = "2026-08-06"
CLOUDFLARE_WRANGLER_VERSION = "4.114.0"
CLOUDFLARE_ASSET_DIRECTORY = "./site"
CLOUDFLARE_DEPLOY_COMMAND = "wrangler deploy"
CLOUDFLARE_PREVIEW_COMMAND = "wrangler versions upload"

TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".nix",
    ".py",
    ".rs",
    ".go",
    ".js",
    ".ts",
    ".tsx",
    ".sh",
}


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_text(path: Path) -> str | None:
    if path.suffix not in TEXT_SUFFIXES and path.name not in {"NOTICE", "LICENSE"}:
        return None
    if path.stat().st_size > 1_000_000:
        return None
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def read_json_object(path: Path, label: str, errors: list[str]) -> dict[str, object] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"invalid {label}: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"invalid {label}: root must be an object")
        return None
    return value


def check_required(errors: list[str]) -> None:
    for item in sorted(REQUIRED_FILES):
        if not (ROOT / item).is_file():
            errors.append(f"missing required file: {item}")

    for directory in sorted(PUBLIC_ROOTS):
        path = ROOT / directory
        if not path.is_dir():
            errors.append(f"missing public monorepo directory: {directory}/")
        elif not (path / "README.md").is_file():
            errors.append(f"missing boundary README: {directory}/README.md")


def check_cloudflare_build(errors: list[str]) -> None:
    wrangler_path = ROOT / "wrangler.jsonc"
    package_path = ROOT / "package.json"
    site_index = ROOT / "site" / "index.html"

    if not site_index.is_file():
        errors.append("missing Cloudflare static asset entry point: site/index.html")

    if not wrangler_path.is_file() or not package_path.is_file():
        return

    wrangler = read_json_object(wrangler_path, "wrangler.jsonc", errors)
    package = read_json_object(package_path, "package.json", errors)
    if wrangler is None or package is None:
        return

    if wrangler.get("name") != CLOUDFLARE_WORKER_NAME:
        errors.append(f"Cloudflare Worker name must be exactly '{CLOUDFLARE_WORKER_NAME}'")

    if wrangler.get("compatibility_date") != CLOUDFLARE_COMPATIBILITY_DATE:
        errors.append(
            f"Cloudflare compatibility_date must be exactly '{CLOUDFLARE_COMPATIBILITY_DATE}'"
        )

    assets = wrangler.get("assets")
    asset_directory = assets.get("directory") if isinstance(assets, dict) else None
    if not isinstance(asset_directory, str) or asset_directory.rstrip("/") != CLOUDFLARE_ASSET_DIRECTORY:
        errors.append("Cloudflare assets.directory must resolve to './site/'")

    if package.get("private") is not True:
        errors.append("Cloudflare package must be private")

    scripts = package.get("scripts")
    if not isinstance(scripts, dict):
        errors.append("package.json scripts must be an object")
    else:
        if scripts.get("deploy") != CLOUDFLARE_DEPLOY_COMMAND:
            errors.append(f"package.json deploy script must be '{CLOUDFLARE_DEPLOY_COMMAND}'")
        if scripts.get("preview") != CLOUDFLARE_PREVIEW_COMMAND:
            errors.append(f"package.json preview script must be '{CLOUDFLARE_PREVIEW_COMMAND}'")

    dev_dependencies = package.get("devDependencies")
    wrangler_version = dev_dependencies.get("wrangler") if isinstance(dev_dependencies, dict) else None
    if wrangler_version != CLOUDFLARE_WRANGLER_VERSION:
        errors.append(f"Wrangler must be pinned exactly to {CLOUDFLARE_WRANGLER_VERSION}")


def check_symlinks(errors: list[str]) -> None:
    for path in ROOT.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.is_symlink():
            errors.append(f"symlink is not allowed in reviewed source: {relative(path)}")


def check_markers(errors: list[str]) -> None:
    marked_paths = {ROOT / item for item in MARKED_POLICY_FILES}
    for public_root in PUBLIC_ROOTS:
        marked_paths.update((ROOT / public_root).rglob("*.md"))

    for path in sorted(marked_paths):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        header = "\n".join(text.splitlines()[:12])
        if not MARKER_PATTERN.search(header):
            errors.append(f"missing or malformed content markers: {relative(path)}")

        if "Canonical source: site/" in header:
            errors.append(f"generated site cannot be canonical source: {relative(path)}")


def check_public_roots(errors: list[str]) -> None:
    for public_root in sorted(PUBLIC_ROOTS):
        for path in (ROOT / public_root).rglob("*"):
            if not path.is_file():
                continue
            text = read_text(path)
            if text is None:
                continue
            for label, pattern in PROHIBITED_PUBLIC_PATTERNS:
                if pattern.search(text):
                    errors.append(f"{label} in public implementation path: {relative(path)}")


def check_private_coordinate_leakage(errors: list[str]) -> None:
    for base in (ROOT / "README.md", ROOT / "docs"):
        paths = [base] if base.is_file() else list(base.rglob("*.md"))
        for path in paths:
            text = path.read_text(encoding="utf-8")
            if PRIVATE_OWNER_REPOSITORY_PATTERN.search(text):
                errors.append(f"private-owner repository coordinate in public documentation: {relative(path)}")
            if PRIVATE_OWNER_ISSUE_PATTERN.search(text):
                errors.append(f"private-owner issue coordinate in public documentation: {relative(path)}")


def main() -> int:
    errors: list[str] = []
    check_required(errors)
    check_cloudflare_build(errors)
    check_symlinks(errors)
    check_markers(errors)
    check_public_roots(errors)
    check_private_coordinate_leakage(errors)

    if errors:
        print("repository policy check failed:", file=sys.stderr)
        for error in sorted(set(errors)):
            print(f"- {error}", file=sys.stderr)
        return 1

    print("repository policy check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
