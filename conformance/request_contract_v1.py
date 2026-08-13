"""Capability request normalization and domain-separated digest rules."""

from __future__ import annotations

from typing import Any

from .constraint_profiles_v1 import (
    DEFAULT_CONSTRAINT_PROFILES,
    ConstraintProfileRegistry,
    normalize_requested_constraints,
)
from .contract_primitives_v1 import (
    CAPABILITY_NAME,
    REQUEST_ID,
    ContractError,
    _expect_fields,
    _expect_object,
    _expect_reference,
    _expect_reference_list,
    _expect_string,
    _expect_timestamp,
    _require,
    parse_timestamp,
)
from .jcs_v1 import REQUEST_DIGEST_DOMAIN, digest_value, normalize_json

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
CAPABILITY_FIELDS = {"name", "schema_version"}


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


def validate_requested_constraints(
    value: Any,
    capability_name: str,
    schema_version: int = 1,
    *,
    constraint_profiles: ConstraintProfileRegistry = DEFAULT_CONSTRAINT_PROFILES,
) -> dict[str, Any]:
    return normalize_requested_constraints(
        value,
        capability_name=capability_name,
        schema_version=schema_version,
        profiles=constraint_profiles,
    )


def normalize_request(
    document: Any,
    *,
    constraint_profiles: ConstraintProfileRegistry = DEFAULT_CONSTRAINT_PROFILES,
) -> dict[str, Any]:
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
        request.get("requested_constraints", {}),
        capability["name"],
        capability["schema_version"],
        constraint_profiles=constraint_profiles,
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


def request_digest(
    document: Any,
    *,
    constraint_profiles: ConstraintProfileRegistry = DEFAULT_CONSTRAINT_PROFILES,
) -> str:
    return digest_value(
        normalize_request(document, constraint_profiles=constraint_profiles),
        domain=REQUEST_DIGEST_DOMAIN,
    )
