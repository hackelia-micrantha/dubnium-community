#!/usr/bin/env python3
"""Validate the public contract tree without network access or third-party packages."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Iterable

MAX_BYTES = 1_000_000
MAX_DEPTH = 64
MAX_COLLECTION_ITEMS = 10_000
JSON_SCHEMA_2020_12 = "https://json-schema.org/draft/2020-12/schema"
SCHEMA_ID_PREFIX = "https://schemas.micrantha.com/dubnium/"
OPENAPI_VERSION = "3.1.2"
MARKERS = re.compile(
    r"^Status: (?:experimental|v1alpha|v1beta|stable)$.*?"
    r"^Content: normative$.*?"
    r"^Canonical source: .+$.*?"
    r"^Generated: (?:no|yes from .+)$",
    re.M | re.S,
)
BCP14 = re.compile(r"\b(?:MUST|MUST NOT|SHOULD|SHOULD NOT|MAY)\b")


class DuplicateKeyError(ValueError):
    pass


class NonFiniteNumberError(ValueError):
    pass


def normalize_repo_path(path: str) -> str:
    normalized = path.strip().replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def object_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate key: {key}")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise NonFiniteNumberError(f"non-finite JSON number: {value}")


def load_json(path: Path) -> Any:
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise ValueError(f"file exceeds {MAX_BYTES} byte limit")
    text = path.read_text(encoding="utf-8")
    return json.loads(
        text,
        object_pairs_hook=object_without_duplicates,
        parse_constant=reject_constant,
    )


def inspect_shape(value: Any, *, depth: int = 0) -> None:
    if depth > MAX_DEPTH:
        raise ValueError(f"JSON nesting exceeds {MAX_DEPTH}")
    if isinstance(value, dict):
        if len(value) > MAX_COLLECTION_ITEMS:
            raise ValueError(f"object exceeds {MAX_COLLECTION_ITEMS} entries")
        for child in value.values():
            inspect_shape(child, depth=depth + 1)
    elif isinstance(value, list):
        if len(value) > MAX_COLLECTION_ITEMS:
            raise ValueError(f"array exceeds {MAX_COLLECTION_ITEMS} entries")
        for child in value:
            inspect_shape(child, depth=depth + 1)
    elif isinstance(value, float) and not math.isfinite(value):
        raise ValueError("non-finite number")


def iter_refs(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        ref = value.get("$ref")
        if isinstance(ref, str):
            yield ref
        for child in value.values():
            yield from iter_refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_refs(child)


def resolve_local_ref(
    source: Path,
    ref: str,
    root: Path,
    *,
    allowed_roots: tuple[Path, ...] | None = None,
) -> Path | None:
    if ref.startswith("#"):
        return None
    if "://" in ref or ref.startswith("//"):
        raise ValueError(f"remote reference is prohibited: {ref}")
    path_part = ref.split("#", 1)[0]
    if not path_part:
        return None
    candidate = (source.parent / path_part).resolve()
    root_resolved = root.resolve()
    try:
        candidate.relative_to(root_resolved)
    except ValueError as exc:
        raise ValueError(f"reference escapes bundled root: {ref}") from exc

    if allowed_roots is not None:
        allowed = False
        for allowed_root in allowed_roots:
            try:
                candidate.relative_to(allowed_root.resolve())
            except ValueError:
                continue
            allowed = True
            break
        if not allowed:
            raise ValueError(f"reference targets an unapproved bundled path: {ref}")

    if not candidate.is_file():
        raise ValueError(f"unresolved bundled reference: {ref}")
    return candidate


def detect_cycles(graph: dict[Path, set[Path]]) -> list[str]:
    errors: list[str] = []
    visiting: set[Path] = set()
    visited: set[Path] = set()

    def visit(node: Path, stack: list[Path]) -> None:
        if node in visited:
            return
        if node in visiting:
            cycle = stack[stack.index(node) :] + [node]
            errors.append("cyclic schema reference: " + " -> ".join(item.name for item in cycle))
            return
        visiting.add(node)
        stack.append(node)
        for target in sorted(graph.get(node, set())):
            visit(target, stack)
        stack.pop()
        visiting.remove(node)
        visited.add(node)

    for node in sorted(graph):
        visit(node, [])
    return errors


def validate_schemas(root: Path) -> list[str]:
    errors: list[str] = []
    schema_root = root / "schemas"
    graph: dict[Path, set[Path]] = {}
    ids: dict[str, Path] = {}

    for path in sorted(schema_root.rglob("*.json")) if schema_root.is_dir() else []:
        relative = path.relative_to(root).as_posix()
        try:
            document = load_json(path)
            inspect_shape(document)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"{relative}: invalid JSON schema: {exc}")
            continue
        if not isinstance(document, dict):
            errors.append(f"{relative}: schema root must be an object")
            continue
        if document.get("$schema") != JSON_SCHEMA_2020_12:
            errors.append(f"{relative}: $schema must be {JSON_SCHEMA_2020_12}")
        schema_id = document.get("$id")
        if not isinstance(schema_id, str) or not schema_id.startswith(SCHEMA_ID_PREFIX):
            errors.append(f"{relative}: $id must start with {SCHEMA_ID_PREFIX}")
        elif schema_id in ids:
            errors.append(f"{relative}: duplicate $id also used by {ids[schema_id].relative_to(root)}")
        else:
            ids[schema_id] = path

        graph[path.resolve()] = set()
        for ref in iter_refs(document):
            try:
                target = resolve_local_ref(path, ref, schema_root)
            except ValueError as exc:
                errors.append(f"{relative}: {exc}")
                continue
            if target is not None:
                graph[path.resolve()].add(target.resolve())

    errors.extend(detect_cycles(graph))
    return errors


def validate_openapi(root: Path) -> list[str]:
    errors: list[str] = []
    api_root = root / "api"
    schema_root = root / "schemas"
    if not api_root.is_dir():
        return errors

    for path in sorted(api_root.rglob("*")):
        if not path.is_file() or path.name == "README.md":
            continue
        relative = path.relative_to(root).as_posix()
        if path.suffix.lower() in {".yaml", ".yml"}:
            errors.append(f"{relative}: YAML OpenAPI requires a reviewed pinned parser; use JSON initially")
            continue
        if path.suffix.lower() != ".json":
            continue
        try:
            document = load_json(path)
            inspect_shape(document)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"{relative}: invalid OpenAPI JSON: {exc}")
            continue
        if not isinstance(document, dict):
            errors.append(f"{relative}: OpenAPI root must be an object")
            continue
        if document.get("openapi") != OPENAPI_VERSION:
            errors.append(f"{relative}: openapi must be {OPENAPI_VERSION}")
        if not isinstance(document.get("info"), dict):
            errors.append(f"{relative}: info object is required")
        if not isinstance(document.get("paths"), dict):
            errors.append(f"{relative}: paths object is required")
        for ref in iter_refs(document):
            try:
                resolve_local_ref(
                    path,
                    ref,
                    root,
                    allowed_roots=(api_root, schema_root),
                )
            except ValueError as exc:
                errors.append(f"{relative}: {exc}")
    return errors


def validate_specs(root: Path) -> list[str]:
    errors: list[str] = []
    spec_root = root / "spec"
    if not spec_root.is_dir():
        return errors
    for path in sorted(spec_root.rglob("*.md")):
        if path.name == "README.md":
            continue
        relative = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        header = "\n".join(text.splitlines()[:12])
        if not MARKERS.search(header):
            errors.append(f"{relative}: normative specification markers are missing or malformed")
        if not BCP14.search(text):
            errors.append(f"{relative}: normative specification must contain at least one BCP 14 requirement")
    return errors


def validate_examples(root: Path) -> list[str]:
    errors: list[str] = []
    examples_root = root / "examples"
    schema_root = root / "schemas"
    if not examples_root.is_dir():
        return errors
    for path in sorted(examples_root.rglob("*.json")):
        relative = path.relative_to(root).as_posix()
        try:
            document = load_json(path)
            inspect_shape(document)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"{relative}: invalid example JSON: {exc}")
            continue
        if not isinstance(document, dict):
            errors.append(f"{relative}: example root must be an object")
            continue
        schema_ref = document.get("$schema")
        if not isinstance(schema_ref, str):
            errors.append(f"{relative}: example must identify its bundled schema with $schema")
            continue
        try:
            resolve_local_ref(path, schema_ref, root)
        except ValueError as exc:
            errors.append(f"{relative}: {exc}")
        target = (path.parent / schema_ref.split("#", 1)[0]).resolve()
        if schema_root.resolve() not in target.parents:
            errors.append(f"{relative}: example $schema must resolve beneath schemas/")
    return errors


def is_contract_path(path: str) -> bool:
    normalized = normalize_repo_path(path)
    if normalized in {"spec/README.md", "schemas/README.md", "api/README.md"}:
        return False
    return normalized.startswith(("spec/", "schemas/", "api/"))


def validate_change_record(changed_paths: list[str]) -> list[str]:
    if not any(is_contract_path(path) for path in changed_paths):
        return []
    normalized = [normalize_repo_path(path) for path in changed_paths]
    has_record = any(
        path.startswith("changes/")
        and path.lower().endswith(".md")
        and path != "changes/README.md"
        for path in normalized
    )
    return [] if has_record else ["contract changes require a Markdown record under changes/"]


def validate(root: Path, changed_paths: list[str] | None = None) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_schemas(root))
    errors.extend(validate_openapi(root))
    errors.extend(validate_specs(root))
    errors.extend(validate_examples(root))
    if changed_paths is not None:
        errors.extend(validate_change_record(changed_paths))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--changed-paths-stdin", action="store_true")
    args = parser.parse_args()
    changed_paths = sys.stdin.read().splitlines() if args.changed_paths_stdin else None
    errors = validate(Path(args.root).resolve(), changed_paths)
    if errors:
        print("contract tree validation failed:", file=sys.stderr)
        for error in sorted(set(errors)):
            print(f"- {error}", file=sys.stderr)
        return 1
    print("contract tree validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
