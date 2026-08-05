#!/usr/bin/env python3
"""Offline conformance helpers for the Dubnium Capability Gateway v1 contracts."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata
from typing import Any, Iterable

MAX_REQUEST_BYTES = 65_536
MAX_DEPTH = 32
MAX_COLLECTION_ITEMS = 1_024
MAX_SAFE_INTEGER = 9_007_199_254_740_991
REQUEST_FIELDS = {
    "$schema",
    "contract_version",
    "request_id",
    "capability",
    "target_ref",
    "payload",
    "requested_constraints",
    "evidence_refs",
    "requested_at",
    "expires_at",
}
MANIFEST_FIELDS = {
    "$schema",
    "contract_version",
    "manifest_id",
    "request_id",
    "request_digest",
    "actor_ref",
    "capability",
    "target_ref",
    "normalized_payload",
    "normalized_payload_digest",
    "decision",
    "granted_constraints",
    "evidence_requirements",
    "issued_at",
    "expires_at",
}
CAPABILITY_FIELDS = {"name", "schema_version"}
DECISION_FIELDS = {
    "decision_ref",
    "request_digest",
    "policy_ref",
    "outcome",
    "expires_at",
}
EVIDENCE_REQUIREMENT_FIELDS = {"before_execution", "completion"}
REQUEST_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
REFERENCE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$")
CAPABILITY_NAME = re.compile(r"^[a-z][a-z0-9]*(?:\.[a-z][a-z0-9-]*)+$")
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
UTC_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


class ContractError(ValueError):
    """Stable conformance failure."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message

    def envelope(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}


class _DuplicateKey(ValueError):
    pass


def _pairs_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKey(key)
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ContractError("json.non_finite", f"non-finite JSON number is prohibited: {value}")


def parse_json_bytes(data: bytes, *, max_bytes: int = MAX_REQUEST_BYTES) -> Any:
    if len(data) > max_bytes:
        raise ContractError("input.too_large", f"input exceeds {max_bytes} bytes")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as caught:
        raise ContractError("json.invalid_utf8", "input must be valid UTF-8") from caught
    try:
        value = json.loads(
            text,
            object_pairs_hook=_pairs_without_duplicates,
            parse_constant=_reject_constant,
        )
    except _DuplicateKey as caught:
        raise ContractError("json.duplicate_key", f"duplicate JSON object key: {caught}") from caught
    except ContractError:
        raise
    except json.JSONDecodeError as caught:
        raise ContractError("json.invalid", f"invalid JSON at line {caught.lineno}, column {caught.colno}") from caught
    return normalize_json(value)


def load_json(path: Path, *, max_bytes: int = MAX_REQUEST_BYTES) -> Any:
    try:
        return parse_json_bytes(path.read_bytes(), max_bytes=max_bytes)
    except OSError as caught:
        raise ContractError("input.unreadable", f"cannot read input: {caught}") from caught


def normalize_json(value: Any, *, depth: int = 0) -> Any:
    if depth > MAX_DEPTH:
        raise ContractError("json.too_deep", f"JSON nesting exceeds {MAX_DEPTH}")
    if value is None:
        raise ContractError("json.null_prohibited", "null is prohibited; omit optional fields instead")
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        if abs(value) > MAX_SAFE_INTEGER:
            raise ContractError("json.integer_out_of_range", "integer exceeds the interoperable 53-bit range")
        return value
    if isinstance(value, float):
        raise ContractError("json.float_prohibited", "floating-point numbers are prohibited in v1")
    if isinstance(value, list):
        if len(value) > MAX_COLLECTION_ITEMS:
            raise ContractError("json.collection_too_large", "array exceeds the item limit")
        return [normalize_json(item, depth=depth + 1) for item in value]
    if isinstance(value, dict):
        if len(value) > MAX_COLLECTION_ITEMS:
            raise ContractError("json.collection_too_large", "object exceeds the entry limit")
        normalized: dict[str, Any] = {}
        for raw_key, raw_value in value.items():
            key = unicodedata.normalize("NFC", raw_key)
            if key in normalized:
                raise ContractError(
                    "json.normalized_duplicate_key",
                    f"object keys collide after NFC normalization: {key}",
                )
            normalized[key] = normalize_json(raw_value, depth=depth + 1)
        return normalized
    raise ContractError("json.unsupported_type", f"unsupported JSON value: {type(value).__name__}")


def canonical_json_bytes(value: Any) -> bytes:
    normalized = normalize_json(value)
    return json.dumps(
        normalized,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest_value(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _expect_object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError("contract.type", f"{name} must be an object")
    return value


def _expect_fields(value: dict[str, Any], allowed: set[str], name: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ContractError("contract.unknown_field", f"{name} contains unknown fields: {', '.join(unknown)}")


def _require(value: dict[str, Any], field: str, name: str) -> Any:
    if field not in value:
        raise ContractError("contract.missing_field", f"{name} is missing required field: {field}")
    return value[field]


def _expect_string(value: Any, name: str, *, max_length: int = 512) -> str:
    if not isinstance(value, str) or not value or len(value) > max_length:
        raise ContractError("contract.string", f"{name} must be a non-empty string up to {max_length} characters")
    return value


def _expect_reference(value: Any, name: str) -> str:
    text = _expect_string(value, name, max_length=256)
    if not REFERENCE.fullmatch(text):
        raise ContractError("contract.reference", f"{name} must be a stable reference")
    return text


def _expect_digest(value: Any, name: str) -> str:
    text = _expect_string(value, name, max_length=71)
    if not DIGEST.fullmatch(text):
        raise ContractError("contract.digest", f"{name} must be a lowercase sha256 digest")
    return text


def _expect_timestamp(value: Any, name: str) -> str:
    text = _expect_string(value, name, max_length=20)
    if not UTC_TIMESTAMP.fullmatch(text):
        raise ContractError("contract.timestamp", f"{name} must use YYYY-MM-DDTHH:MM:SSZ")
    try:
        datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as caught:
        raise ContractError("contract.timestamp", f"{name} is not a valid UTC timestamp") from caught
    return text


def parse_timestamp(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def _expect_reference_list(value: Any, name: str, *, max_items: int = 16) -> list[str]:
    if not isinstance(value, list) or len(value) > max_items:
        raise ContractError("contract.reference_list", f"{name} must be an array with at most {max_items} items")
    refs = [_expect_reference(item, f"{name}[{index}]") for index, item in enumerate(value)]
    if len(refs) != len(set(refs)):
        raise ContractError("contract.duplicate_reference", f"{name} contains duplicate references")
    return refs


def validate_capability(value: Any) -> dict[str, Any]:
    capability = _expect_object(value, "capability")
    _expect_fields(capability, CAPABILITY_FIELDS, "capability")
    name = _expect_string(_require(capability, "name", "capability"), "capability.name", max_length=128)
    if not CAPABILITY_NAME.fullmatch(name):
        raise ContractError("capability.invalid_name", "capability.name must be a dotted lowercase identifier")
    version = _require(capability, "schema_version", "capability")
    if not isinstance(version, int) or isinstance(version, bool) or version != 1:
        raise ContractError("capability.unsupported_version", "capability.schema_version must be 1")
    return {"name": name, "schema_version": version}


def validate_noop_payload(value: Any) -> dict[str, Any]:
    payload = _expect_object(value, "payload")
    _expect_fields(payload, {"message", "repeat"}, "payload")
    message = _expect_string(_require(payload, "message", "payload"), "payload.message", max_length=64)
    repeat = _require(payload, "repeat", "payload")
    if not isinstance(repeat, int) or isinstance(repeat, bool) or not 1 <= repeat <= 3:
        raise ContractError("payload.repeat", "payload.repeat must be an integer from 1 through 3")
    return {"message": message, "repeat": repeat}


def validate_requested_constraints(value: Any, capability_name: str) -> dict[str, Any]:
    constraints = _expect_object(value, "requested_constraints")
    if capability_name == "example.noop":
        _expect_fields(constraints, {"max_result_bytes"}, "requested_constraints")
        maximum = _require(constraints, "max_result_bytes", "requested_constraints")
        if not isinstance(maximum, int) or isinstance(maximum, bool) or not 64 <= maximum <= 4096:
            raise ContractError(
                "constraint.max_result_bytes",
                "requested_constraints.max_result_bytes must be an integer from 64 through 4096",
            )
        return {"max_result_bytes": maximum}
    if constraints:
        raise ContractError("constraint.unsupported", "this capability does not define requested constraints")
    return {}


def normalize_request(document: Any) -> dict[str, Any]:
    request = _expect_object(normalize_json(document), "capability request")
    _expect_fields(request, REQUEST_FIELDS, "capability request")
    if _require(request, "contract_version", "capability request") != "1.0":
        raise ContractError("contract.unsupported_version", "contract_version must be 1.0")
    request_id = _expect_string(_require(request, "request_id", "capability request"), "request_id", max_length=128)
    if not REQUEST_ID.fullmatch(request_id):
        raise ContractError("request.invalid_id", "request_id contains unsupported characters")
    capability = validate_capability(_require(request, "capability", "capability request"))
    target_ref = _expect_reference(_require(request, "target_ref", "capability request"), "target_ref")
    raw_payload = _require(request, "payload", "capability request")
    payload = validate_noop_payload(raw_payload) if capability["name"] == "example.noop" else _expect_object(raw_payload, "payload")
    requested_constraints = validate_requested_constraints(
        request.get("requested_constraints", {}), capability["name"]
    )
    evidence_refs = _expect_reference_list(request.get("evidence_refs", []), "evidence_refs")
    requested_at = _expect_timestamp(_require(request, "requested_at", "capability request"), "requested_at")
    normalized: dict[str, Any] = {
        "contract_version": "1.0",
        "request_id": request_id,
        "capability": capability,
        "target_ref": target_ref,
        "payload": payload,
        "requested_constraints": requested_constraints,
        "evidence_refs": evidence_refs,
        "requested_at": requested_at,
    }
    if "expires_at" in request:
        expires_at = _expect_timestamp(request["expires_at"], "expires_at")
        if parse_timestamp(expires_at) <= parse_timestamp(requested_at):
            raise ContractError("request.invalid_expiry", "expires_at must be later than requested_at")
        normalized["expires_at"] = expires_at
    return normalized


def request_digest(document: Any) -> str:
    return digest_value(normalize_request(document))


def _validate_decision(value: Any, expected_digest: str) -> dict[str, Any]:
    decision = _expect_object(value, "decision")
    _expect_fields(decision, DECISION_FIELDS, "decision")
    decision_ref = _expect_reference(_require(decision, "decision_ref", "decision"), "decision.decision_ref")
    decision_digest = _expect_digest(_require(decision, "request_digest", "decision"), "decision.request_digest")
    if decision_digest != expected_digest:
        raise ContractError("manifest.decision_digest_mismatch", "decision is not bound to the request digest")
    policy_ref = _expect_reference(_require(decision, "policy_ref", "decision"), "decision.policy_ref")
    outcome = _expect_string(_require(decision, "outcome", "decision"), "decision.outcome", max_length=32)
    if outcome != "allow":
        raise ContractError("manifest.not_authorized", "only a final allow decision is executable")
    expires_at = _expect_timestamp(_require(decision, "expires_at", "decision"), "decision.expires_at")
    return {
        "decision_ref": decision_ref,
        "request_digest": decision_digest,
        "policy_ref": policy_ref,
        "outcome": outcome,
        "expires_at": expires_at,
    }


def _validate_granted_constraints(
    value: Any,
    requested: dict[str, Any],
    capability_name: str,
) -> dict[str, Any]:
    granted = _expect_object(value, "granted_constraints")
    if capability_name == "example.noop":
        _expect_fields(granted, {"max_result_bytes"}, "granted_constraints")
        maximum = _require(granted, "max_result_bytes", "granted_constraints")
        if not isinstance(maximum, int) or isinstance(maximum, bool) or maximum < 1:
            raise ContractError("constraint.max_result_bytes", "granted max_result_bytes must be a positive integer")
        requested_maximum = requested.get("max_result_bytes")
        if not isinstance(requested_maximum, int) or maximum > requested_maximum:
            raise ContractError("manifest.constraint_widening", "granted constraints widen the normalized request")
        return {"max_result_bytes": maximum}
    if granted:
        raise ContractError("manifest.constraint_widening", "granted constraints are unsupported for this capability")
    return {}


def validate_manifest(
    request_document: Any,
    manifest_document: Any,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    request = normalize_request(request_document)
    expected_digest = digest_value(request)
    manifest = _expect_object(normalize_json(manifest_document), "authorized manifest")
    _expect_fields(manifest, MANIFEST_FIELDS, "authorized manifest")
    if _require(manifest, "contract_version", "authorized manifest") != "1.0":
        raise ContractError("contract.unsupported_version", "manifest contract_version must be 1.0")
    manifest_id = _expect_reference(_require(manifest, "manifest_id", "authorized manifest"), "manifest_id")
    request_id = _expect_string(_require(manifest, "request_id", "authorized manifest"), "manifest.request_id", max_length=128)
    if request_id != request["request_id"]:
        raise ContractError("manifest.request_id_mismatch", "manifest request_id does not match the request")
    manifest_digest = _expect_digest(_require(manifest, "request_digest", "authorized manifest"), "manifest.request_digest")
    if manifest_digest != expected_digest:
        raise ContractError("manifest.digest_mismatch", "manifest request_digest does not match the normalized request")
    actor_ref = _expect_reference(_require(manifest, "actor_ref", "authorized manifest"), "actor_ref")
    capability = validate_capability(_require(manifest, "capability", "authorized manifest"))
    if capability != request["capability"]:
        raise ContractError("manifest.capability_mismatch", "manifest capability does not match the request")
    target_ref = _expect_reference(_require(manifest, "target_ref", "authorized manifest"), "manifest.target_ref")
    if target_ref != request["target_ref"]:
        raise ContractError("manifest.target_mismatch", "manifest target does not match the request")
    payload = normalize_json(_expect_object(_require(manifest, "normalized_payload", "authorized manifest"), "normalized_payload"))
    if payload != request["payload"]:
        raise ContractError("manifest.payload_mismatch", "manifest payload does not match the normalized request")
    payload_digest = _expect_digest(
        _require(manifest, "normalized_payload_digest", "authorized manifest"),
        "normalized_payload_digest",
    )
    if payload_digest != digest_value(request["payload"]):
        raise ContractError("manifest.payload_digest_mismatch", "normalized_payload_digest is incorrect")
    decision = _validate_decision(_require(manifest, "decision", "authorized manifest"), expected_digest)
    granted_constraints = _validate_granted_constraints(
        _require(manifest, "granted_constraints", "authorized manifest"),
        request["requested_constraints"],
        capability["name"],
    )
    requirements = _expect_object(
        _require(manifest, "evidence_requirements", "authorized manifest"),
        "evidence_requirements",
    )
    _expect_fields(requirements, EVIDENCE_REQUIREMENT_FIELDS, "evidence_requirements")
    evidence_requirements = {
        "before_execution": _expect_reference_list(
            _require(requirements, "before_execution", "evidence_requirements"),
            "evidence_requirements.before_execution",
        ),
        "completion": _expect_reference_list(
            _require(requirements, "completion", "evidence_requirements"),
            "evidence_requirements.completion",
        ),
    }
    missing_evidence = sorted(set(evidence_requirements["before_execution"]) - set(request["evidence_refs"]))
    if missing_evidence:
        raise ContractError("manifest.missing_evidence", "required pre-execution evidence is absent from the request")
    issued_at = _expect_timestamp(_require(manifest, "issued_at", "authorized manifest"), "issued_at")
    expires_at = _expect_timestamp(_require(manifest, "expires_at", "authorized manifest"), "manifest.expires_at")
    issued_time = parse_timestamp(issued_at)
    expiry_time = parse_timestamp(expires_at)
    if issued_time >= expiry_time:
        raise ContractError("manifest.invalid_lifetime", "manifest expires_at must be later than issued_at")
    if expiry_time > parse_timestamp(decision["expires_at"]):
        raise ContractError("manifest.expiry_widening", "manifest expiry exceeds the decision expiry")
    request_expiry = request.get("expires_at")
    if isinstance(request_expiry, str) and expiry_time > parse_timestamp(request_expiry):
        raise ContractError("manifest.expiry_widening", "manifest expiry exceeds the request expiry")
    effective_now = now or datetime.now(timezone.utc)
    if expiry_time <= effective_now:
        raise ContractError("manifest.expired", "authorized manifest has expired")
    return {
        "contract_version": "1.0",
        "manifest_id": manifest_id,
        "request_id": request_id,
        "request_digest": manifest_digest,
        "actor_ref": actor_ref,
        "capability": capability,
        "target_ref": target_ref,
        "normalized_payload": payload,
        "normalized_payload_digest": payload_digest,
        "decision": decision,
        "granted_constraints": granted_constraints,
        "evidence_requirements": evidence_requirements,
        "issued_at": issued_at,
        "expires_at": expires_at,
    }


def execute_no_effect(request_document: Any, manifest_document: Any) -> dict[str, Any]:
    request = normalize_request(request_document)
    manifest = validate_manifest(request_document, manifest_document)
    if request["capability"]["name"] != "example.noop":
        raise ContractError("provider.unsupported_capability", "reference provider supports only example.noop")
    payload = request["payload"]
    output = {"echo": [payload["message"] for _ in range(payload["repeat"])]}
    if len(canonical_json_bytes(output)) > manifest["granted_constraints"]["max_result_bytes"]:
        raise ContractError("provider.result_too_large", "deterministic result exceeds the granted bound")
    return {
        "contract_version": "1.0",
        "capability": request["capability"],
        "request_id": request["request_id"],
        "request_digest": digest_value(request),
        "status": "succeeded",
        "output": output,
    }


def _negative_cases(root: Path) -> Iterable[tuple[str, str, str]]:
    return (
        ("request-unknown-field.json", "request", "contract.unknown_field"),
        ("request-duplicate-key.json", "request", "json.duplicate_key"),
        ("request-null.json", "request", "json.null_prohibited"),
        ("manifest-digest-mismatch.json", "manifest", "manifest.digest_mismatch"),
        ("manifest-expired.json", "manifest", "manifest.expired"),
        ("manifest-request-expiry-widening.json", "manifest", "manifest.expiry_widening"),
        ("manifest-issued-after-expiry.json", "manifest", "manifest.invalid_lifetime"),
        ("manifest-constraint-widening.json", "manifest", "manifest.constraint_widening"),
        ("manifest-payload-mismatch.json", "manifest", "manifest.payload_mismatch"),
    )


def run_fixture_suite(root: Path) -> list[str]:
    errors: list[str] = []
    positive = root / "positive"
    negative = root / "negative"
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
        first_result = execute_no_effect(request, manifest)
        second_result = execute_no_effect(request, manifest)
        if first_result != second_result:
            errors.append("no-effect provider result is not deterministic")
    except (ContractError, OSError) as caught:
        errors.append(f"positive fixture failed: {caught}")
        return errors

    for filename, kind, expected_code in _negative_cases(root):
        path = negative / filename
        try:
            candidate = load_json(path)
            if kind == "request":
                normalize_request(candidate)
            else:
                validate_manifest(request, candidate, now=datetime(2030, 1, 1, tzinfo=timezone.utc))
        except ContractError as caught:
            if caught.code != expected_code:
                errors.append(f"{filename}: expected {expected_code}, got {caught.code}")
        else:
            errors.append(f"{filename}: fixture unexpectedly passed")
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


if __name__ == "__main__":
    raise SystemExit(main())
