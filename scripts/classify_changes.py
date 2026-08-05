#!/usr/bin/env python3
"""Classify repository changes for the always-running contract CI gate."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import PurePosixPath

CATEGORIES = ("contract", "implementation", "site", "policy", "build")

POLICY_FILES = {
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
}


def normalize(path: str) -> str:
    return path.strip().replace("\\", "/").lstrip("./")


def classify_path(path: str) -> set[str]:
    normalized = normalize(path)
    if not normalized:
        return set()

    parts = PurePosixPath(normalized).parts
    top = parts[0] if parts else ""
    categories: set[str] = set()

    if top in {"spec", "schemas", "api", "changes"}:
        categories.add("contract")
    if top in {"packages", "conformance", "reference", "examples", "policy-examples"}:
        categories.add("implementation")
    if top == "site" or normalized in {
        "scripts/validate_publication.py",
        "tests/test_validate_publication.py",
        ".github/workflows/validate-publication.yml",
        ".github/workflows/pages.yml",
    }:
        categories.add("site")
    if normalized in POLICY_FILES or top == "docs" or normalized.startswith(".github/ISSUE_TEMPLATE/") or normalized in {
        ".github/pull_request_template.md",
        ".github/CODEOWNERS",
    }:
        categories.add("policy")
    if top == ".github" or top == "release" or normalized.startswith("scripts/") or normalized.startswith("tests/"):
        categories.add("build")

    if not categories:
        categories.add("implementation")
    return categories


def classify(paths: list[str]) -> dict[str, bool]:
    result = {category: False for category in CATEGORIES}
    for path in paths:
        for category in classify_path(path):
            result[category] = True
    result["any"] = any(result.values())
    return result


def write_github_output(result: dict[str, bool], output_path: str) -> None:
    with open(output_path, "a", encoding="utf-8") as handle:
        for key, value in result.items():
            handle.write(f"{key}={'true' if value else 'false'}\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--stdin", action="store_true", help="Read newline-delimited paths from stdin")
    parser.add_argument(
        "--github-output",
        nargs="?",
        const="",
        default=None,
        help="Write boolean outputs to this path or to GITHUB_OUTPUT when omitted",
    )
    args = parser.parse_args()

    paths = list(args.paths)
    if args.stdin:
        paths.extend(sys.stdin.read().splitlines())

    result = classify(paths)
    print(json.dumps(result, sort_keys=True))

    if args.github_output is not None:
        output_path = args.github_output or os.environ.get("GITHUB_OUTPUT", "")
        if not output_path:
            print("--github-output requires a path or GITHUB_OUTPUT", file=sys.stderr)
            return 2
        write_github_output(result, output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
