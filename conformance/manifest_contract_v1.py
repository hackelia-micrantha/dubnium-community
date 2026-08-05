"""Authorized manifest validation for Capability Gateway v1alpha."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .contract_primitives_v1 import (
    ContractError,
    _expect_digest,
    _expect_fields,
    _expect_object,
    _expect_reference,
    _expect_reference_list,
    _expect_string,
    _expect_timestamp,
    _require,
    parse_timestamp,
)
from .jcs_v1 import normalize_json, payload_digest
from .request_contract_v1 import normalize_request, request_digest, validate_capability

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
DECISION_FIELDS = {
    "decision_ref",
    "request_digest",
    "policy_ref",
    "outcome",
    "expires_at",
}
EVIDENCE_REQUIREMENT_FIELDS = {"before_execution", "completion"}


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
    expected_digest = request_digest(request)
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
    normalized_payload_digest = _expect_digest(
        _require(manifest, "normalized_payload_digest", "authorized manifest"),
        "normalized_payload_digest",
    )
    if normalized_payload_digest != payload_digest(request["payload"]):
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
        "normalized_payload_digest": normalized_payload_digest,
        "decision": decision,
        "granted_constraints": granted_constraints,
        "evidence_requirements": evidence_requirements,
        "issued_at": issued_at,
        "expires_at": expires_at,
    }
