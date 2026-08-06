"""Fixture runner and CLI for Capability Gateway v1alpha."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any

from .contract_primitives_v1 import ContractError, _require
from .jcs_v1 import canonical_json_bytes, load_json
from .manifest_contract_v1 import validate_manifest
from .reference_runtime_v1 import BoundedRequestRegistry, execute_no_effect
from .request_contract_v1 import normalize_request, request_digest


def run_fixture_suite(root: Path) -> list[str]:
    errors: list[str] = []
    positive = root / "positive"
    negative = root / "negative"
    synthetic = root / "synthetic"
    request_path = positive / "request.json"
    manifest_path = positive / "authorized-manifest.json"
    try:
        request = load_json(request_path)
        expected_canonical = (positive / "request.canonical.json").read_bytes()
        actual_canonical = canonical_json_bytes(normalize_request(request))
        if actual_canonical != expected_canonical:
            errors.append("positive canonical request bytes do not match")
        expected_digest = (positive / "request.digest.txt").read_text(encoding="utf-8").strip()
        actual_digest = request_digest(request)
        if actual_digest != expected_digest:
            errors.append(f"positive request digest mismatch: expected {expected_digest}, got {actual_digest}")
        manifest = load_json(manifest_path)
        validate_manifest(request, manifest, now=datetime(2030, 1, 1, tzinfo=timezone.utc))
        if execute_no_effect(request, manifest) != execute_no_effect(request, manifest):
            errors.append("no-effect provider result is not deterministic")

        registry = BoundedRequestRegistry()
        if registry.bind(request) != "new":
            errors.append("first request-id binding was not new")
        registry.mark_dispatched(request["request_id"])
        if registry.bind(request) != "existing":
            errors.append("identical request-id retry was not idempotent")
        registry.mark_dispatched(request["request_id"])
        if registry.dispatch_count(request["request_id"]) != 1:
            errors.append("identical retry caused duplicate dispatch")

        unicode_value = load_json(positive / "unicode-order.json")
        expected_unicode = (positive / "unicode-order.canonical.json").read_bytes()
        if canonical_json_bytes(unicode_value) != expected_unicode:
            errors.append("Unicode JCS ordering vector does not match")
        if canonical_json_bytes({"value": "é"}) == canonical_json_bytes({"value": "é"}):
            errors.append("caller strings were silently Unicode-normalized")

        deployment = normalize_request(load_json(synthetic / "deployment-apply-request.json"))
        if deployment["capability"]["name"] != "deployment.apply":
            errors.append("synthetic deployment capability name is not deployment.apply")
    except (ContractError, OSError) as caught:
        errors.append(f"positive fixture failed: {caught}")
        return errors

    request_cases = (
        ("request-unknown-field.json", "contract.unknown_field"),
        ("request-duplicate-key.json", "json.duplicate_key"),
        ("request-null.json", "json.null_prohibited"),
    )
    for filename, expected_code in request_cases:
        try:
            normalize_request(load_json(negative / filename))
        except ContractError as caught:
            if caught.code != expected_code:
                errors.append(f"{filename}: expected {expected_code}, got {caught.code}")
        else:
            errors.append(f"{filename}: fixture unexpectedly passed")

    manifest_cases = (
        ("manifest-digest-mismatch.json", "manifest.digest_mismatch"),
        ("manifest-expired-rfc8785.json", "manifest.expired"),
        ("manifest-expiry-widening-rfc8785.json", "manifest.expiry_widening"),
        ("manifest-constraint-widening-rfc8785.json", "manifest.constraint_widening"),
        ("manifest-payload-mismatch-rfc8785.json", "manifest.payload_mismatch"),
    )
    for filename, expected_code in manifest_cases:
        try:
            validate_manifest(request, load_json(negative / filename), now=datetime(2030, 1, 1, tzinfo=timezone.utc))
        except ContractError as caught:
            if caught.code != expected_code:
                errors.append(f"{filename}: expected {expected_code}, got {caught.code}")
        else:
            errors.append(f"{filename}: fixture unexpectedly passed")

    try:
        conflict = load_json(negative / "request-id-conflict.json")
        registry = BoundedRequestRegistry()
        registry.bind(_require(conflict, "first", "request-id conflict"))
        registry.bind(_require(conflict, "second", "request-id conflict"))
    except ContractError as caught:
        if caught.code != "request.id_conflict":
            errors.append(f"request-id-conflict.json: expected request.id_conflict, got {caught.code}")
    else:
        errors.append("request-id-conflict.json: fixture unexpectedly passed")
    return errors


def _write_json(value: Any) -> None:
    sys.stdout.buffer.write(canonical_json_bytes(value) + b"\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    for name in ("validate-request", "canonicalize", "digest"):
        command = subcommands.add_parser(name)
        command.add_argument("request", type=Path)
    manifest = subcommands.add_parser("validate-manifest")
    manifest.add_argument("request", type=Path)
    manifest.add_argument("manifest", type=Path)
    fixtures = subcommands.add_parser("run-fixtures")
    fixtures.add_argument("root", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "validate-request":
            _write_json(normalize_request(load_json(args.request)))
        elif args.command == "canonicalize":
            sys.stdout.buffer.write(canonical_json_bytes(normalize_request(load_json(args.request))) + b"\n")
        elif args.command == "digest":
            print(request_digest(load_json(args.request)))
        elif args.command == "validate-manifest":
            _write_json(validate_manifest(load_json(args.request), load_json(args.manifest)))
        elif args.command == "run-fixtures":
            errors = run_fixture_suite(args.root)
            if errors:
                for item in errors:
                    print(f"- {item}", file=sys.stderr)
                return 1
            print("Capability Gateway v1 conformance fixtures passed")
    except ContractError as caught:
        print(json.dumps({"error": caught.envelope()}, sort_keys=True), file=sys.stderr)
        return 1
    return 0
