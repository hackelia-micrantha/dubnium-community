"""Portable submission, status, provider-operation, and error envelopes for v1alpha."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .contract_primitives_v1 import (
    ContractError,
    REQUEST_ID,
    _expect_digest,
    _expect_fields,
    _expect_object,
    _expect_reference,
    _expect_reference_list,
    _expect_string,
    _expect_timestamp,
    _require,
)
from .jcs_v1 import load_json, normalize_json
from .request_contract_v1 import validate_capability

SUBMISSION_FIELDS = {
    "$schema",
    "contract_version",
    "request_id",
    "outcome",
    "request_digest",
    "status_ref",
    "error",
    "submitted_at",
}
STATUS_FIELDS = {
    "$schema",
    "contract_version",
    "request_id",
    "request_digest",
    "gateway_state",
    "provider_operation",
    "result",
    "error",
    "updated_at",
}
PROVIDER_OPERATION_FIELDS = {"provider_ref", "operation_ref", "phase"}
RESULT_FIELDS = {"output", "evidence_refs"}
ERROR_FIELDS = {"code", "message", "field", "retryable"}

SUBMISSION_OUTCOMES = {"accepted", "rejected"}
GATEWAY_STATES = {
    "received",
    "validated",
    "policy-pending",
    "denied",
    "authorized",
    "dispatched",
    "succeeded",
    "failed",
    "indeterminate",
}
TERMINAL_STATES = {"denied", "succeeded", "failed", "indeterminate"}
ERROR_TERMINAL_STATES = {"denied", "failed", "indeterminate"}
PROVIDER_PHASES = {"accepted", "running", "completed", "failed", "indeterminate"}


def normalize_error(value: Any) -> dict[str, Any]:
    error = _expect_object(value, "error")
    _expect_fields(error, ERROR_FIELDS, "error")
    code = _expect_string(_require(error, "code", "error"), "error.code", max_length=128)
    if not all(character.islower() or character.isdigit() or character in "._-" for character in code):
        raise ContractError("error.invalid_code", "error.code must be a stable lowercase identifier")
    message = _expect_string(_require(error, "message", "error"), "error.message", max_length=512)
    retryable = _require(error, "retryable", "error")
    if not isinstance(retryable, bool):
        raise ContractError("error.retryable", "error.retryable must be a boolean")
    normalized: dict[str, Any] = {
        "code": code,
        "message": message,
        "retryable": retryable,
    }
    if "field" in error:
        normalized["field"] = _expect_string(error["field"], "error.field", max_length=128)
    return normalized


def normalize_provider_operation(value: Any) -> dict[str, Any]:
    operation = _expect_object(value, "provider_operation")
    _expect_fields(operation, PROVIDER_OPERATION_FIELDS, "provider_operation")
    provider_ref = _expect_reference(_require(operation, "provider_ref", "provider_operation"), "provider_operation.provider_ref")
    operation_ref = _expect_reference(_require(operation, "operation_ref", "provider_operation"), "provider_operation.operation_ref")
    phase = _expect_string(_require(operation, "phase", "provider_operation"), "provider_operation.phase", max_length=32)
    if phase not in PROVIDER_PHASES:
        raise ContractError("provider.invalid_phase", "provider_operation.phase is unsupported")
    return {
        "provider_ref": provider_ref,
        "operation_ref": operation_ref,
        "phase": phase,
    }


def normalize_submission(value: Any) -> dict[str, Any]:
    submission = _expect_object(normalize_json(value), "capability submission")
    _expect_fields(submission, SUBMISSION_FIELDS, "capability submission")
    if _require(submission, "contract_version", "capability submission") != "1.0":
        raise ContractError("contract.unsupported_version", "submission contract_version must be 1.0")
    request_id = _expect_string(_require(submission, "request_id", "capability submission"), "submission.request_id", max_length=128)
    if not REQUEST_ID.fullmatch(request_id):
        raise ContractError("request.invalid_id", "submission request_id contains unsupported characters")
    outcome = _expect_string(_require(submission, "outcome", "capability submission"), "submission.outcome", max_length=16)
    if outcome not in SUBMISSION_OUTCOMES:
        raise ContractError("submission.invalid_outcome", "submission outcome is unsupported")
    submitted_at = _expect_timestamp(_require(submission, "submitted_at", "capability submission"), "submission.submitted_at")
    normalized: dict[str, Any] = {
        "contract_version": "1.0",
        "request_id": request_id,
        "outcome": outcome,
        "submitted_at": submitted_at,
    }
    if "request_digest" in submission:
        normalized["request_digest"] = _expect_digest(submission["request_digest"], "submission.request_digest")
    if outcome == "accepted":
        if "error" in submission:
            raise ContractError("submission.error_on_accept", "accepted submission must not carry an error")
        normalized["status_ref"] = _expect_reference(_require(submission, "status_ref", "capability submission"), "submission.status_ref")
    else:
        if "status_ref" in submission:
            raise ContractError("submission.status_on_reject", "rejected submission must not carry status_ref")
        normalized["error"] = normalize_error(_require(submission, "error", "capability submission"))
    return normalized


def normalize_result(value: Any) -> dict[str, Any]:
    result = _expect_object(value, "result")
    _expect_fields(result, RESULT_FIELDS, "result")
    output = normalize_json(_expect_object(_require(result, "output", "result"), "result.output"))
    evidence_refs = _expect_reference_list(result.get("evidence_refs", []), "result.evidence_refs")
    return {"output": output, "evidence_refs": evidence_refs}


def normalize_status(value: Any) -> dict[str, Any]:
    status = _expect_object(normalize_json(value), "capability status")
    _expect_fields(status, STATUS_FIELDS, "capability status")
    if _require(status, "contract_version", "capability status") != "1.0":
        raise ContractError("contract.unsupported_version", "status contract_version must be 1.0")
    request_id = _expect_string(_require(status, "request_id", "capability status"), "status.request_id", max_length=128)
    if not REQUEST_ID.fullmatch(request_id):
        raise ContractError("request.invalid_id", "status request_id contains unsupported characters")
    request_digest = _expect_digest(_require(status, "request_digest", "capability status"), "status.request_digest")
    gateway_state = _expect_string(_require(status, "gateway_state", "capability status"), "gateway_state", max_length=32)
    if gateway_state not in GATEWAY_STATES:
        raise ContractError("status.invalid_state", "gateway_state is unsupported")
    updated_at = _expect_timestamp(_require(status, "updated_at", "capability status"), "status.updated_at")
    normalized: dict[str, Any] = {
        "contract_version": "1.0",
        "request_id": request_id,
        "request_digest": request_digest,
        "gateway_state": gateway_state,
        "updated_at": updated_at,
    }
    operation = status.get("provider_operation")
    if gateway_state in {"dispatched", "succeeded", "failed", "indeterminate"}:
        normalized["provider_operation"] = normalize_provider_operation(_require(status, "provider_operation", "capability status"))
    elif operation is not None:
        raise ContractError("status.premature_provider_operation", "provider_operation is not allowed before dispatch")
    if gateway_state == "succeeded":
        normalized["result"] = normalize_result(_require(status, "result", "capability status"))
        if "error" in status:
            raise ContractError("status.error_on_success", "succeeded status must not carry an error")
    elif gateway_state in ERROR_TERMINAL_STATES:
        normalized["error"] = normalize_error(_require(status, "error", "capability status"))
        if "result" in status:
            raise ContractError("status.result_on_error", "error terminal status must not carry result")
    else:
        if "result" in status or "error" in status:
            raise ContractError("status.premature_terminal_payload", "nonterminal status must not carry result or error")
    return normalized


def _phase_is_valid_for_state(state: str, phase: str) -> bool:
    if state == "dispatched":
        return phase in {"accepted", "running"}
    if state == "succeeded":
        return phase == "completed"
    if state == "failed":
        return phase == "failed"
    if state == "indeterminate":
        return phase == "indeterminate"
    return True


def validate_status_transition(previous: Any, current: Any) -> dict[str, Any]:
    before = normalize_status(previous)
    after = normalize_status(current)
    if before["request_id"] != after["request_id"] or before["request_digest"] != after["request_digest"]:
        raise ContractError("status.identity_mismatch", "status transition changes request identity")
    if before["gateway_state"] in TERMINAL_STATES and before != after:
        raise ContractError("status.terminal_mutation", "terminal status is immutable")
    if not _phase_is_valid_for_state(after["gateway_state"], after.get("provider_operation", {}).get("phase", "")):
        raise ContractError("status.phase_mismatch", "provider phase does not match Gateway state")
    previous_operation = before.get("provider_operation")
    current_operation = after.get("provider_operation")
    if previous_operation is not None and current_operation is not None:
        if previous_operation["provider_ref"] != current_operation["provider_ref"] or previous_operation["operation_ref"] != current_operation["operation_ref"]:
            raise ContractError("status.operation_substitution", "provider operation identity changed")
    return after


def run_envelope_fixture_suite(root: Path) -> list[str]:
    errors: list[str] = []
    positive = root / "positive"
    negative = root / "negative"
    try:
        normalize_submission(load_json(positive / "submission.json"))
        normalize_submission(load_json(positive / "submission-rejected.json"))
        dispatched = normalize_status(load_json(positive / "status-dispatched.json"))
        succeeded = normalize_status(load_json(positive / "status-succeeded.json"))
        validate_status_transition(dispatched, succeeded)
    except (ContractError, OSError) as caught:
        errors.append(f"positive envelope fixture failed: {caught}")
        return errors
    negative_cases = (
        ("submission-accepted-with-error.json", normalize_submission, "submission.error_on_accept"),
        ("submission-rejected-with-status.json", normalize_submission, "submission.status_on_reject"),
        ("status-succeeded-with-error.json", normalize_status, "status.error_on_success"),
        ("status-pending-with-result.json", normalize_status, "status.premature_terminal_payload"),
    )
    for filename, validator, expected_code in negative_cases:
        try:
            validator(load_json(negative / filename))
        except ContractError as caught:
            if caught.code != expected_code:
                errors.append(f"{filename}: expected {expected_code}, got {caught.code}")
        else:
            errors.append(f"{filename}: fixture unexpectedly passed")
    return errors
