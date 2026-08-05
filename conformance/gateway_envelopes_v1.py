#!/usr/bin/env python3
"""Offline submission and status conformance for Capability Gateway v1."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import sys
from typing import Any


def _load_core():
    path = Path(__file__).with_name("capability_gateway_v1.py")
    spec = importlib.util.spec_from_file_location("capability_gateway_v1_envelopes", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load core conformance module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


core = _load_core()
SUBMISSION_FIELDS = {
    "$schema",
    "contract_version",
    "request_id",
    "request_digest",
    "state",
    "error",
}
STATUS_FIELDS = {
    "$schema",
    "contract_version",
    "request_id",
    "request_digest",
    "state",
    "provider_operation_ref",
    "terminal_result",
    "error",
    "evidence_refs",
    "updated_at",
}
ERROR_FIELDS = {"code", "message", "field"}
STATES = {
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
ERROR_STATES = {"denied", "failed", "indeterminate"}
MAX_TERMINAL_RESULT_BYTES = 4096


def _request_id(value: Any, name: str = "request_id") -> str:
    text = core._expect_string(value, name, max_length=128)
    if not core.REQUEST_ID.fullmatch(text):
        raise core.ContractError("request.invalid_id", f"{name} contains unsupported characters")
    return text


def validate_error(value: Any) -> dict[str, str]:
    error = core._expect_object(value, "error")
    core._expect_fields(error, ERROR_FIELDS, "error")
    code = core._expect_string(core._require(error, "code", "error"), "error.code", max_length=128)
    if not core.CAPABILITY_NAME.fullmatch(code):
        raise core.ContractError("error.invalid_code", "error.code must be a dotted lowercase identifier")
    message = core._expect_string(core._require(error, "message", "error"), "error.message", max_length=512)
    normalized = {"code": code, "message": message}
    if "field" in error:
        normalized["field"] = core._expect_string(error["field"], "error.field", max_length=256)
    return normalized


def _optional_identity(
    envelope: dict[str, Any],
    *,
    expected_request_id: str | None,
    expected_digest: str | None,
) -> tuple[str | None, str | None]:
    has_id = "request_id" in envelope
    has_digest = "request_digest" in envelope
    if has_id != has_digest:
        raise core.ContractError(
            "submission.partial_identity",
            "request_id and request_digest must be present together",
        )
    if not has_id:
        return None, None
    request_id = _request_id(envelope["request_id"])
    digest = core._expect_digest(envelope["request_digest"], "request_digest")
    if expected_request_id is not None and request_id != expected_request_id:
        raise core.ContractError("envelope.request_id_mismatch", "request_id does not match the normalized request")
    if expected_digest is not None and digest != expected_digest:
        raise core.ContractError("envelope.digest_mismatch", "request_digest does not match the normalized request")
    return request_id, digest


def validate_submission(
    document: Any,
    *,
    expected_request_id: str | None = None,
    expected_digest: str | None = None,
) -> dict[str, Any]:
    submission = core._expect_object(core.normalize_json(document), "capability submission")
    core._expect_fields(submission, SUBMISSION_FIELDS, "capability submission")
    if core._require(submission, "contract_version", "capability submission") != "1.0":
        raise core.ContractError("contract.unsupported_version", "submission contract_version must be 1.0")
    state = core._expect_string(core._require(submission, "state", "capability submission"), "submission.state", max_length=16)
    if state not in {"accepted", "rejected"}:
        raise core.ContractError("submission.invalid_state", "submission.state must be accepted or rejected")
    request_id, digest = _optional_identity(
        submission,
        expected_request_id=expected_request_id,
        expected_digest=expected_digest,
    )
    normalized: dict[str, Any] = {"contract_version": "1.0", "state": state}
    if request_id is not None and digest is not None:
        normalized.update({"request_id": request_id, "request_digest": digest})
    if state == "accepted":
        if request_id is None:
            raise core.ContractError("submission.missing_identity", "accepted submission requires request identity")
        if "error" in submission:
            raise core.ContractError("submission.unexpected_error", "accepted submission cannot contain error")
    else:
        normalized["error"] = validate_error(core._require(submission, "error", "capability submission"))
    return normalized


def validate_status(
    document: Any,
    *,
    expected_request_id: str | None = None,
    expected_digest: str | None = None,
) -> dict[str, Any]:
    status = core._expect_object(core.normalize_json(document), "capability status")
    core._expect_fields(status, STATUS_FIELDS, "capability status")
    if core._require(status, "contract_version", "capability status") != "1.0":
        raise core.ContractError("contract.unsupported_version", "status contract_version must be 1.0")
    request_id, digest = _optional_identity(
        status,
        expected_request_id=expected_request_id,
        expected_digest=expected_digest,
    )
    if request_id is None or digest is None:
        raise core.ContractError("status.missing_identity", "status requires request identity")
    state = core._expect_string(core._require(status, "state", "capability status"), "status.state", max_length=32)
    if state not in STATES:
        raise core.ContractError("status.invalid_state", "status.state is unsupported")
    updated_at = core._expect_timestamp(core._require(status, "updated_at", "capability status"), "updated_at")
    normalized: dict[str, Any] = {
        "contract_version": "1.0",
        "request_id": request_id,
        "request_digest": digest,
        "state": state,
        "updated_at": updated_at,
    }
    if "provider_operation_ref" in status:
        normalized["provider_operation_ref"] = core._expect_reference(
            status["provider_operation_ref"], "provider_operation_ref"
        )
    if "evidence_refs" in status:
        normalized["evidence_refs"] = core._expect_reference_list(
            status["evidence_refs"], "evidence_refs", max_items=32
        )
    if "terminal_result" in status:
        if state not in {"succeeded", "failed"}:
            raise core.ContractError("status.nonterminal_result", "terminal_result is allowed only for succeeded or failed")
        result = core._expect_object(status["terminal_result"], "terminal_result")
        if len(core.canonical_json_bytes(result)) > MAX_TERMINAL_RESULT_BYTES:
            raise core.ContractError("status.result_too_large", "terminal_result exceeds 4096 canonical bytes")
        normalized["terminal_result"] = result
    if state in ERROR_STATES:
        normalized["error"] = validate_error(core._require(status, "error", "capability status"))
    elif "error" in status:
        raise core.ContractError("status.unexpected_error", f"state {state} cannot contain error")
    return normalized


def run_fixture_suite(root: Path) -> list[str]:
    errors: list[str] = []
    request = core.load_json(root / "positive" / "request.json")
    normalized_request = core.normalize_request(request)
    request_id = normalized_request["request_id"]
    digest = core.digest_value(normalized_request)
    try:
        submission = core.load_json(root / "positive" / "submission.json")
        validate_submission(
            submission,
            expected_request_id=request_id,
            expected_digest=digest,
        )
        status = core.load_json(root / "positive" / "status.json")
        validate_status(
            status,
            expected_request_id=request_id,
            expected_digest=digest,
        )
        rejected = core.load_json(root / "positive" / "rejected-submission.json")
        validate_submission(rejected)
    except core.ContractError as caught:
        errors.append(f"positive envelope fixture failed: {caught.code}: {caught.message}")
    negative = {
        "submission-partial-identity.json": (validate_submission, "submission.partial_identity"),
        "submission-accepted-with-error.json": (validate_submission, "submission.unexpected_error"),
        "status-digest-mismatch.json": (validate_status, "envelope.digest_mismatch"),
        "status-nonterminal-result.json": (validate_status, "status.nonterminal_result"),
        "status-failure-without-error.json": (validate_status, "contract.missing_field"),
    }
    for filename, (validator, expected_code) in negative.items():
        candidate = core.load_json(root / "negative" / filename)
        try:
            validator(
                candidate,
                expected_request_id=request_id,
                expected_digest=digest,
            )
        except core.ContractError as caught:
            if caught.code != expected_code:
                errors.append(f"{filename}: expected {expected_code}, got {caught.code}")
        else:
            errors.append(f"{filename}: fixture unexpectedly passed")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    submission = subcommands.add_parser("validate-submission")
    submission.add_argument("document", type=Path)
    status = subcommands.add_parser("validate-status")
    status.add_argument("document", type=Path)
    fixtures = subcommands.add_parser("run-fixtures")
    fixtures.add_argument("root", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "validate-submission":
            value = validate_submission(core.load_json(args.document))
            sys.stdout.buffer.write(core.canonical_json_bytes(value) + b"\n")
        elif args.command == "validate-status":
            value = validate_status(core.load_json(args.document))
            sys.stdout.buffer.write(core.canonical_json_bytes(value) + b"\n")
        else:
            errors = run_fixture_suite(args.root)
            if errors:
                for error in errors:
                    print(f"- {error}", file=sys.stderr)
                return 1
            print("Capability Gateway v1 submission/status fixtures passed")
    except core.ContractError as caught:
        print(f"{caught.code}: {caught.message}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
