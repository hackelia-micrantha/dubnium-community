#!/usr/bin/env python3
"""Verify and safely consume a Dubnium public contract release bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import tarfile
import tempfile

MAX_MEMBERS = 5_000
MAX_MEMBER_BYTES = 1_000_000
MAX_TOTAL_BYTES = 12_000_000


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_checksums(directory: Path) -> None:
    checksum_file = directory / "SHA256SUMS"
    if not checksum_file.is_file():
        raise ValueError("missing SHA256SUMS")
    for line in checksum_file.read_text(encoding="utf-8").splitlines():
        expected, separator, name = line.partition("  ")
        if not separator or len(expected) != 64 or "/" in name or "\\" in name:
            raise ValueError("malformed checksum entry")
        target = directory / name
        if not target.is_file() or sha256(target) != expected:
            raise ValueError(f"checksum mismatch: {name}")


def safe_members(archive: Path) -> list[tarfile.TarInfo]:
    with tarfile.open(archive, mode="r:gz") as tar:
        members = tar.getmembers()
    if not members or len(members) > MAX_MEMBERS:
        raise ValueError("invalid archive member count")
    total = 0
    prefix: str | None = None
    for member in members:
        path = PurePosixPath(member.name)
        if path.is_absolute() or ".." in path.parts or not path.parts:
            raise ValueError(f"unsafe archive path: {member.name}")
        if member.issym() or member.islnk() or member.isdev() or member.isfifo():
            raise ValueError(f"unsupported archive member: {member.name}")
        if not member.isfile():
            raise ValueError(f"non-file archive member: {member.name}")
        prefix = prefix or path.parts[0]
        if path.parts[0] != prefix or len(path.parts) < 2:
            raise ValueError("archive must use one bounded top-level directory")
        if member.size < 0 or member.size > MAX_MEMBER_BYTES:
            raise ValueError(f"archive member exceeds limit: {member.name}")
        total += member.size
    if total > MAX_TOTAL_BYTES:
        raise ValueError("archive exceeds total extraction limit")
    return members


def extract_and_verify(archive: Path, destination: Path) -> Path:
    members = safe_members(archive)
    with tarfile.open(archive, mode="r:gz") as tar:
        for member in members:
            target = destination.joinpath(*PurePosixPath(member.name).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            source = tar.extractfile(member)
            if source is None:
                raise ValueError(f"cannot read archive member: {member.name}")
            target.write_bytes(source.read())
    root = destination / PurePosixPath(members[0].name).parts[0]
    manifest_path = root / "release-manifest.json"
    if not manifest_path.is_file():
        raise ValueError("missing embedded release manifest")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or manifest.get("bundle") != "dubnium-capability-gateway-contracts":
        raise ValueError("unsupported release manifest")
    declared = manifest.get("files")
    if not isinstance(declared, list):
        raise ValueError("manifest files must be an array")
    for entry in declared:
        relative = PurePosixPath(entry["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("unsafe manifest path")
        target = root.joinpath(*relative.parts)
        if not target.is_file() or target.stat().st_size != entry["size"] or sha256(target) != entry["sha256"]:
            raise ValueError(f"manifest mismatch: {relative}")
    return root


def run_conformance(root: Path) -> None:
    commands = (
        ["python3", "conformance/capability_gateway_v1.py", "run-fixtures", "conformance/fixtures/v1"],
        ["python3", "conformance/gateway_envelopes_v1.py", "run-fixtures", "conformance/fixtures/v1"],
    )
    for command in commands:
        subprocess.run(command, cwd=root, check=True, timeout=60)


def verify(directory: Path, run_tests: bool = True) -> None:
    verify_checksums(directory)
    archives = list(directory.glob("dubnium-capability-gateway-contracts-*.tar.gz"))
    if len(archives) != 1:
        raise ValueError("expected exactly one contract archive")
    with tempfile.TemporaryDirectory() as temp:
        root = extract_and_verify(archives[0], Path(temp))
        if run_tests:
            run_conformance(root)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--no-conformance", action="store_true")
    args = parser.parse_args()
    verify(args.directory, run_tests=not args.no_conformance)
    print("contract release verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
