#!/usr/bin/env python3
"""Compare the checked-in public book with a fresh mdBook build."""

from __future__ import annotations
import argparse
import json
import re
import subprocess
from pathlib import Path

SEARCH_INDEX = re.compile(r"^searchindex-[0-9a-f]+\.js$", re.I)
SEARCH_INDEX_REFERENCE = re.compile(rb"searchindex-[0-9a-f]+\.js", re.I)
SEARCH_PREFIX = b"window.search = Object.assign(window.search, JSON.parse('"
SEARCH_SUFFIX = b"'));"

def canonical_search_index(content: bytes) -> bytes:
    if not content.startswith(SEARCH_PREFIX) or not content.endswith(SEARCH_SUFFIX):
        raise ValueError("search index has an unexpected mdBook wrapper")
    payload = json.loads(content[len(SEARCH_PREFIX):-len(SEARCH_SUFFIX)])
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

def normalized_artifact(files: dict[str, bytes]) -> dict[str, bytes]:
    normalized: dict[str, bytes] = {}
    for name, content in files.items():
        path = Path(name)
        if path.name == "publication.json":
            metadata = json.loads(content)
            content = json.dumps(
                {key: metadata.get(key) for key in ("schema_version", "generator")},
                sort_keys=True, separators=(",", ":"),
            ).encode("utf-8")
        elif SEARCH_INDEX.fullmatch(path.name):
            content = canonical_search_index(content)
            name = (path.parent / "searchindex-canonical.js").as_posix()
        elif path.suffix.lower() == ".html":
            content = SEARCH_INDEX_REFERENCE.sub(b"searchindex-canonical.js", content)
        if name in normalized:
            raise ValueError(f"artifact path collision after normalization: {name}")
        normalized[name] = content
    return normalized

def committed_artifact(root: Path) -> dict[str, bytes]:
    names = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", "HEAD", "--", "site/docs"],
        cwd=root, text=True,
    ).splitlines()
    return {
        name.removeprefix("site/docs/"): subprocess.check_output(
            ["git", "show", f"HEAD:{name}"], cwd=root
        )
        for name in names
    }

def filesystem_artifact(root: Path) -> dict[str, bytes]:
    docs = root / "site" / "docs"
    files: dict[str, bytes] = {}
    for path in docs.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"generated artifact contains symlink: {path.relative_to(docs)}")
        if path.is_file():
            files[path.relative_to(docs).as_posix()] = path.read_bytes()
    return files

def compare_artifacts(committed: dict[str, bytes], generated: dict[str, bytes]) -> list[str]:
    expected = normalized_artifact(committed)
    actual = normalized_artifact(generated)
    missing = sorted(expected.keys() - actual.keys())
    extra = sorted(actual.keys() - expected.keys())
    changed = sorted(name for name in expected.keys() & actual.keys() if expected[name] != actual[name])
    errors = []
    if missing:
        errors.append("generated book is missing: " + ", ".join(missing))
    if extra:
        errors.append("generated book added: " + ", ".join(extra))
    if changed:
        errors.append("generated book content differs: " + ", ".join(changed))
    return errors

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    root = parser.parse_args().root.resolve()
    try:
        errors = compare_artifacts(committed_artifact(root), filesystem_artifact(root))
    except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        errors = [str(error)]
    if errors:
        print("Generated public book does not match its checked-in artifact:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Generated public book matches its checked-in artifact")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
