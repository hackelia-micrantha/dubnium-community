#!/usr/bin/env python3
"""Build a deterministic, bounded public Capability Gateway contract bundle."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import tarfile
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "release" / "contract-bundle-version.txt"
INCLUDE_ROOTS = ("api", "changes", "conformance", "examples", "schemas", "spec")
INCLUDE_FILES = ("LICENSE", "NOTICE", "SECURITY.md")
MAX_FILE_BYTES = 1_000_000
MAX_TOTAL_BYTES = 10_000_000


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def selected_files() -> list[Path]:
    files: list[Path] = []
    for root_name in INCLUDE_ROOTS:
        root = ROOT / root_name
        if not root.is_dir():
            raise ValueError(f"missing release root: {root_name}")
        files.extend(path for path in root.rglob("*") if path.is_file())
    for name in INCLUDE_FILES:
        path = ROOT / name
        if path.is_file():
            files.append(path)
    result = sorted(set(files), key=lambda p: p.relative_to(ROOT).as_posix())
    total = 0
    for path in result:
        if path.is_symlink():
            raise ValueError(f"symlink prohibited in release: {path}")
        size = path.stat().st_size
        if size > MAX_FILE_BYTES:
            raise ValueError(f"release file exceeds limit: {path}")
        total += size
    if total > MAX_TOTAL_BYTES:
        raise ValueError("release input exceeds total size limit")
    return result


def manifest(version: str, source_commit: str, files: Iterable[Path]) -> dict[str, object]:
    entries = []
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        data = path.read_bytes()
        entries.append({"path": relative, "sha256": sha256_bytes(data), "size": len(data)})
    return {
        "schema_version": 1,
        "bundle": "dubnium-capability-gateway-contracts",
        "version": version,
        "source_commit": source_commit,
        "contract_profile": "capability-gateway-v1alpha",
        "compatibility": "experimental-pre-1.0",
        "canonicalization": "RFC 8785 with Dubnium domain-separated SHA-256 digests",
        "files": entries,
    }


def sbom(version: str, source_commit: str, files: Iterable[Path]) -> dict[str, object]:
    package_id = "SPDXRef-Package-dubnium-capability-gateway-contracts"
    file_entries = []
    relationships = []
    for index, path in enumerate(files, start=1):
        relative = path.relative_to(ROOT).as_posix()
        file_id = f"SPDXRef-File-{index}"
        file_entries.append({
            "SPDXID": file_id,
            "fileName": relative,
            "checksums": [{"algorithm": "SHA256", "checksumValue": sha256_bytes(path.read_bytes())}],
        })
        relationships.append({"spdxElementId": package_id, "relationshipType": "CONTAINS", "relatedSpdxElement": file_id})
    return {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": f"dubnium-capability-gateway-contracts-{version}",
        "documentNamespace": f"https://github.com/hackelia-micrantha/dubnium-community/releases/{version}/{source_commit}",
        "creationInfo": {"created": "1970-01-01T00:00:00Z", "creators": ["Tool: scripts/build_contract_release.py"]},
        "packages": [{
            "SPDXID": package_id,
            "name": "dubnium-capability-gateway-contracts",
            "versionInfo": version,
            "downloadLocation": "NOASSERTION",
            "filesAnalyzed": True,
            "licenseConcluded": "Apache-2.0",
            "licenseDeclared": "Apache-2.0",
            "copyrightText": "NOASSERTION",
        }],
        "files": file_entries,
        "relationships": relationships,
        "annotations": [{
            "annotationDate": "1970-01-01T00:00:00Z",
            "annotationType": "OTHER",
            "annotator": "Tool: scripts/build_contract_release.py",
            "comment": f"Python {platform.python_version()}; no third-party runtime dependencies are bundled.",
        }],
    }


def canonical_json(data: object) -> bytes:
    return (json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def add_bytes(tar: tarfile.TarFile, name: str, data: bytes) -> None:
    info = tarfile.TarInfo(name)
    info.size = len(data)
    info.mode = 0o644
    info.mtime = 0
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    tar.addfile(info, fileobj=__import__("io").BytesIO(data))


def build(output: Path, source_commit: str) -> list[Path]:
    version = VERSION_FILE.read_text(encoding="utf-8").strip()
    if not version:
        raise ValueError("empty release version")
    files = selected_files()
    manifest_bytes = canonical_json(manifest(version, source_commit, files))
    sbom_bytes = canonical_json(sbom(version, source_commit, files))
    output.mkdir(parents=True, exist_ok=True)
    stem = f"dubnium-capability-gateway-contracts-{version}"
    archive = output / f"{stem}.tar.gz"
    manifest_path = output / f"{stem}.manifest.json"
    sbom_path = output / f"{stem}.spdx.json"
    manifest_path.write_bytes(manifest_bytes)
    sbom_path.write_bytes(sbom_bytes)
    with archive.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped:
            with tarfile.open(fileobj=zipped, mode="w", format=tarfile.USTAR_FORMAT) as tar:
                prefix = PurePosixPath(stem)
                for path in files:
                    add_bytes(tar, str(prefix / path.relative_to(ROOT).as_posix()), path.read_bytes())
                add_bytes(tar, str(prefix / "release-manifest.json"), manifest_bytes)
                add_bytes(tar, str(prefix / "release-sbom.spdx.json"), sbom_bytes)
    checksum_path = output / "SHA256SUMS"
    outputs = [archive, manifest_path, sbom_path]
    checksum_path.write_text("".join(f"{sha256_bytes(path.read_bytes())}  {path.name}\n" for path in outputs), encoding="utf-8")
    return [*outputs, checksum_path]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("dist"))
    parser.add_argument("--source-commit", default=os.environ.get("SOURCE_COMMIT", "unknown"))
    args = parser.parse_args()
    for path in build(args.output, args.source_commit):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
