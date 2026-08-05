from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

MAX_RAW_BYTES = 65_536
MAX_DEPTH = 64
MAX_COLLECTION_ITEMS = 64
MAX_STRING_LENGTH = 4096
MAX_KEY_LENGTH = 128
MAX_SAFE_INTEGER = 9_007_199_254_740_991
MAX_RETAINED_REQUESTS = 128
DIGEST_DOMAIN = b"dubnium.capability-request.v1\x00"

REQUEST_ID_RE = re.compile(r"^req_[a-z0-9][a-z0-9_-]{7,63}$")
MANIFEST_ID_RE = re.compile(r"^manifest_[a-z0-9][a-z0-9_-]{7,63}$")
CAPABILITY_RE = re.compile(r"^[a-z][a-z0-9-]*(?:\.[a-z][a-z0-9-]*)+$")
SCHEMA_VERSION_RE = re.compile(r"^[1-9][0-9]{0,3}$")
KIND_RE = re.compile(r"^[a-z][a-z0-9-]*$")
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
TIMESTAMP_RE = re.compile(
    r"^[0-9]{4}-(?:0[1-9]|1[0-2])-(?:[0-2][0-9]|3[01])T"
    r"(?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]Z$"
)

REQUEST_REQUIRED = {
    "contract_version",
    "request_id",
    "capability",
    "target",
    "payload",
    "evidence",
    "requested_at",
}
REQUEST_OPTIONAL = {"expires_at"}
MANIFEST_REQUIRED = {
    "contract_version",
    "manifest_id",
    "request",
    "request_digest",
    "actor",
    "authorization",
    "issued_at",
}


class ContractViolation(ValueError):
    def __init__(self, code: str, detail: str, *, retryable: bool = False):
        super().__init__(detail)
        self.code = code
        self.detail = detail
        self.retryable = retryable


class DuplicateKeyViolation(ContractViolation):
    def __init__(self, key: str):
        super().__init__("duplicate_key", f"duplicate JSON object member: {key}")


def _object_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyViolation(key)
        result[key] = value
    return result


def _reject_float(value: str) -> None:
    raise ContractViolation(
        "schema_validation_failed",
        f"floating-point JSON number is prohibited: {value}",
    )


def _parse_int(value: str) -> int:
    parsed = int(value, 10)
    if abs(parsed) > MAX_SAFE_INTEGER:
        raise ContractViolation(
            "schema_validation_failed",
            f"integer exceeds safe range: {value}",
        )
    return parsed


def parse_json_bytes(data: bytes, *, max_bytes: int = MAX_RAW_BYTES) -> Any:
    if len(data) > max_bytes:
        raise ContractViolation("body_too_large", "raw request exceeds byte limit")
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ContractViolation("invalid_json", "request is not valid UTF-8") from exc
    if text.startswith("\ufeff"):
        raise ContractViolation("invalid_json", "UTF-8 byte-order mark is prohibited")
    try:
        value = json.loads(
            text,
            object_pairs_hook=_object_without_duplicates,
            parse_float=_reject_float,
            parse_int=_parse_int,
            parse_constant=_reject_float,
        )
    except ContractViolation:
        raise
    except json.JSONDecodeError as exc:
        raise ContractViolation("invalid_json", "request is not valid JSON") from exc
    validate_canonical_value(value)
    return value


def _reject_surrogates(value: str) -> None:
    if any(0xD800 <= ord(char) <= 0xDFFF for char in value):
        raise ContractViolation(
            "schema_validation_failed",
            "lone UTF-16 surrogate code point is prohibited",
        )


def validate_canonical_value(value: Any, *, depth: int = 0) -> None:
    if depth > MAX_DEPTH:
        raise ContractViolation(
            "schema_validation_failed",
            f"JSON nesting exceeds {MAX_DEPTH}",
        )
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, int) and not isinstance(value, bool):
        if abs(value) > MAX_SAFE_INTEGER:
            raise ContractViolation(
                "schema_validation_failed",
                "integer exceeds safe range",
            )
        return
    if isinstance(value, float):
        raise ContractViolation(
            "schema_validation_failed",
            "floating-point values are prohibited",
        )
    if isinstance(value, str):
        _reject_surrogates(value)
        if len(value) > MAX_STRING_LENGTH:
            raise ContractViolation(
                "schema_validation_failed",
                f"string exceeds {MAX_STRING_LENGTH} characters",
            )
        return
    if isinstance(value, list):
        if len(value) > MAX_COLLECTION_ITEMS:
            raise ContractViolation(
                "schema_validation_failed",
                f"array exceeds {MAX_COLLECTION_ITEMS} items",
            )
        for item in value:
            validate_canonical_value(item, depth=depth + 1)
        return
    if isinstance(value, dict):
        if len(value) > MAX_COLLECTION_ITEMS:
            raise ContractViolation(
                "schema_validation_failed",
                f"object exceeds {MAX_COLLECTION_ITEMS} members",
            )
        for key, item in value.items():
            if not isinstance(key, str) or not key:
                raise ContractViolation(
                    "schema_validation_failed",
                    "object member names must be non-empty strings",
                )
            _reject_surrogates(key)
            if len(key) > MAX_KEY_LENGTH:
                raise ContractViolation(
                    "schema_validation_failed",
                    f"object member name exceeds {MAX_KEY_LENGTH} characters",
                )
            validate_canonical_value(item, depth=depth + 1)
        return
    raise ContractViolation(
        "schema_validation_failed",
        f"unsupported JSON value type: {type(value).__name__}",
    )


def _utf16_sort_key(value: str) -> tuple[int, ...]:
    encoded = value.encode("utf-16-be")
    return tuple(
        int.from_bytes(encoded[index : index + 2], "big")
        for index in range(0, len(encoded), 2)
    )


def _encode_string(value: str) -> str:
    _reject_surrogates(value)
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _serialize_jcs(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int) and not isinstance(value, bool):
        if abs(value) > MAX_SAFE_INTEGER:
            raise ContractViolation(
                "schema_validation_failed",
                "integer exceeds safe range",
            )
        return str(value)
    if isinstance(value, float):
        raise ContractViolation(
            "schema_validation_failed",
            "floating-point values are prohibited",
        )
    if isinstance(value, str):
        return _encode_string(value)
    if isinstance(value, list):
        return "[" + ",".join(_serialize_jcs(item) for item in value) + "]"
    if isinstance(value, dict):
        members = []
        for key in sorted(value, key=_utf16_sort_key):
            members.append(_encode_string(key) + ":" + _serialize_jcs(value[key]))
        return "{" + ",".join(members) + "}"
    raise ContractViolation(
        "schema_validation_failed",
        f"unsupported JSON value type: {type(value).__name__}",
    )


def canonical_bytes(value: Any) -> bytes:
    validate_canonical_value(value)
    return _serialize_jcs(value).encode("utf-8")


def request_digest(request: dict[str, Any]) -> str:
    validate_request(request)
    digest = hashlib.sha256(DIGEST_DOMAIN + canonical_bytes(request)).hexdigest()
    return f"sha256:{digest}"


def parse_timestamp(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not TIMESTAMP_RE.fullmatch(value):
        raise ContractViolation(
            "invalid_timestamp",
            f"{field} must use whole-second UTC RFC 3339",
        )
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise ContractViolation("invalid_timestamp", f"{field} is not a real timestamp") from exc
    return parsed.replace(tzinfo=timezone.utc)


def _require_exact_keys(
    value: dict[str, Any],
    *,
    required: set[str],
    optional: set[str] = frozenset(),
    label: str,
) -> None:
    missing = sorted(required - value.keys())
    unknown = sorted(value.keys() - required - optional)
    if missing:
        raise ContractViolation(
            "schema_validation_failed",
            f"{label} missing fields: {', '.join(missing)}",
        )
    if unknown:
        raise ContractViolation(
            "schema_validation_failed",
            f"{label} unknown fields: {', '.join(unknown)}",
        )


def _validate_uri(value: Any, field: str) -> None:
    if not isinstance(value, str) or len(value) < 8 or len(value) > 512 or ":" not in value:
        raise ContractViolation("schema_validation_failed", f"{field} must be a bounded URI")


def _validate_digest(value: Any, field: str) -> None:
    if not isinstance(value, str) or not DIGEST_RE.fullmatch(value):
        raise ContractViolation(
            "schema_validation_failed",
            f"{field} must be a SHA-256 digest reference",
        )


def _validate_evidence(value: Any, field: str = "evidence") -> None:
    if not isinstance(value, list) or len(value) > 16:
        raise ContractViolation(
            "schema_validation_failed",
            f"{field} must be an array of at most 16 items",
        )
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ContractViolation(
                "schema_validation_failed",
                f"{field}[{index}] must be an object",
            )
        _require_exact_keys(
            item,
            required={"kind", "reference", "digest"},
            label=f"{field}[{index}]",
        )
        if not isinstance(item["kind"], str) or not KIND_RE.fullmatch(item["kind"]):
            raise ContractViolation(
                "schema_validation_failed",
                f"{field}[{index}].kind is invalid",
            )
        _validate_uri(item["reference"], f"{field}[{index}].reference")
        _validate_digest(item["digest"], f"{field}[{index}].digest")


def validate_echo_payload(payload: Any) -> None:
    if not isinstance(payload, dict):
        raise ContractViolation(
            "schema_validation_failed",
            "example.echo payload must be an object",
        )
    _require_exact_keys(
        payload,
        required={"message", "repeat", "max_output_bytes"},
        label="example.echo payload",
    )
    message = payload["message"]
    repeat = payload["repeat"]
    max_output_bytes = payload["max_output_bytes"]
    if not isinstance(message, str) or not (1 <= len(message) <= 256):
        raise ContractViolation(
            "schema_validation_failed",
            "example.echo message length is invalid",
        )
    _reject_surrogates(message)
    if not isinstance(repeat, int) or isinstance(repeat, bool) or not (1 <= repeat <= 4):
        raise ContractViolation(
            "schema_validation_failed",
            "example.echo repeat must be an integer from 1 to 4",
        )
    if (
        not isinstance(max_output_bytes, int)
        or isinstance(max_output_bytes, bool)
        or not (1 <= max_output_bytes <= 4096)
    ):
        raise ContractViolation(
            "schema_validation_failed",
            "example.echo max_output_bytes must be an integer from 1 to 4096",
        )


def validate_request(request: Any) -> dict[str, Any]:
    if not isinstance(request, dict):
        raise ContractViolation(
            "schema_validation_failed",
            "CapabilityRequest must be an object",
        )
    _require_exact_keys(
        request,
        required=REQUEST_REQUIRED,
        optional=REQUEST_OPTIONAL,
        label="CapabilityRequest",
    )
    validate_canonical_value(request)
    if request["contract_version"] != "1":
        raise ContractViolation(
            "unsupported_contract_version",
            "only Capability Gateway contract version 1 is supported",
        )
    if not isinstance(request["request_id"], str) or not REQUEST_ID_RE.fullmatch(request["request_id"]):
        raise ContractViolation("schema_validation_failed", "request_id is invalid")

    capability = request["capability"]
    if not isinstance(capability, dict):
        raise ContractViolation("schema_validation_failed", "capability must be an object")
    _require_exact_keys(
        capability,
        required={"name", "schema_version"},
        label="capability",
    )
    if not isinstance(capability["name"], str) or not CAPABILITY_RE.fullmatch(capability["name"]):
        raise ContractViolation("schema_validation_failed", "capability.name is invalid")
    if not isinstance(capability["schema_version"], str) or not SCHEMA_VERSION_RE.fullmatch(capability["schema_version"]):
        raise ContractViolation(
            "schema_validation_failed",
            "capability.schema_version is invalid",
        )
    if capability["name"] == "example.echo":
        if capability["schema_version"] != "1":
            raise ContractViolation(
                "unsupported_capability_version",
                "example.echo supports schema version 1",
            )
        validate_echo_payload(request["payload"])

    target = request["target"]
    if not isinstance(target, dict):
        raise ContractViolation("schema_validation_failed", "target must be an object")
    _require_exact_keys(target, required={"kind", "reference"}, label="target")
    if not isinstance(target["kind"], str) or not KIND_RE.fullmatch(target["kind"]):
        raise ContractViolation("schema_validation_failed", "target.kind is invalid")
    _validate_uri(target["reference"], "target.reference")

    if not isinstance(request["payload"], dict):
        raise ContractViolation("schema_validation_failed", "payload must be an object")
    _validate_evidence(request["evidence"])

    requested_at = parse_timestamp(request["requested_at"], "requested_at")
    if "expires_at" in request:
        expires_at = parse_timestamp(request["expires_at"], "expires_at")
        if expires_at <= requested_at:
            raise ContractViolation(
                "invalid_timestamp",
                "expires_at must be later than requested_at",
            )
    return request


def problem(
    violation: ContractViolation,
    *,
    request_id: str | None = None,
    digest: str | None = None,
) -> dict[str, Any]:
    status_by_code = {
        "invalid_json": 400,
        "duplicate_key": 400,
        "body_too_large": 413,
        "unsupported_contract_version": 422,
        "unsupported_capability_version": 422,
        "schema_validation_failed": 422,
        "invalid_timestamp": 422,
        "request_id_conflict": 409,
        "capability_not_admitted": 403,
        "governance_denied": 403,
        "governance_indeterminate": 503,
        "manifest_invalid": 422,
        "manifest_expired": 410,
        "manifest_widening": 403,
        "provider_failed": 500,
        "state_limit_exceeded": 503,
        "internal_error": 500,
    }
    status = status_by_code.get(violation.code, 500)
    result: dict[str, Any] = {
        "type": f"https://schemas.micrantha.com/dubnium/problems/{violation.code}",
        "title": violation.code.replace("_", " "),
        "status": status,
        "code": violation.code,
        "retryable": violation.retryable,
        "detail": violation.detail[:512],
    }
    if request_id is not None:
        result["request_id"] = request_id
    if digest is not None:
        result["request_digest"] = digest
    return result


def build_manifest(
    request: dict[str, Any],
    *,
    manifest_id: str,
    actor_ref: str,
    authentication_method: str,
    decision_ref: str,
    issued_at: str,
    expires_at: str,
    granted_constraints: dict[str, Any],
    policy_ref: str | None = None,
    approval_refs: list[str] | None = None,
    before_execution: list[str] | None = None,
    completion: list[str] | None = None,
) -> dict[str, Any]:
    validate_request(request)
    if not MANIFEST_ID_RE.fullmatch(manifest_id):
        raise ContractViolation("manifest_invalid", "manifest_id is invalid")
    _validate_uri(actor_ref, "actor.reference")
    _validate_uri(decision_ref, "authorization.decision_ref")
    manifest: dict[str, Any] = {
        "contract_version": "1",
        "manifest_id": manifest_id,
        "request": copy.deepcopy(request),
        "request_digest": request_digest(request),
        "actor": {
            "reference": actor_ref,
            "authentication_method": authentication_method,
        },
        "authorization": {
            "decision_ref": decision_ref,
            "outcome": "allow",
            "granted_constraints": copy.deepcopy(granted_constraints),
            "approval_refs": list(approval_refs or []),
            "evidence_requirements": {
                "before_execution": list(before_execution or []),
                "completion": list(completion or []),
            },
            "expires_at": expires_at,
        },
        "issued_at": issued_at,
    }
    if policy_ref is not None:
        manifest["authorization"]["policy_ref"] = policy_ref
    validate_manifest(manifest, now=issued_at)
    return manifest


def validate_manifest(manifest: Any, *, now: str) -> dict[str, Any]:
    if not isinstance(manifest, dict):
        raise ContractViolation("manifest_invalid", "manifest must be an object")
    try:
        _require_exact_keys(manifest, required=MANIFEST_REQUIRED, label="manifest")
        if manifest["contract_version"] != "1":
            raise ContractViolation("manifest_invalid", "unsupported manifest contract version")
        if not isinstance(manifest["manifest_id"], str) or not MANIFEST_ID_RE.fullmatch(manifest["manifest_id"]):
            raise ContractViolation("manifest_invalid", "manifest_id is invalid")
        request = validate_request(manifest["request"])
        _validate_digest(manifest["request_digest"], "request_digest")
        expected_digest = request_digest(request)
        if manifest["request_digest"] != expected_digest:
            raise ContractViolation(
                "manifest_invalid",
                "manifest request digest does not match embedded request",
            )

        actor = manifest["actor"]
        if not isinstance(actor, dict):
            raise ContractViolation("manifest_invalid", "actor must be an object")
        _require_exact_keys(
            actor,
            required={"reference", "authentication_method"},
            optional={"authentication_evidence"},
            label="actor",
        )
        _validate_uri(actor["reference"], "actor.reference")
        if not isinstance(actor["authentication_method"], str) or not KIND_RE.fullmatch(actor["authentication_method"]):
            raise ContractViolation(
                "manifest_invalid",
                "actor.authentication_method is invalid",
            )
        if "authentication_evidence" in actor:
            _validate_evidence(
                [actor["authentication_evidence"]],
                "actor.authentication_evidence",
            )

        authorization = manifest["authorization"]
        if not isinstance(authorization, dict):
            raise ContractViolation("manifest_invalid", "authorization must be an object")
        _require_exact_keys(
            authorization,
            required={
                "decision_ref",
                "outcome",
                "granted_constraints",
                "approval_refs",
                "evidence_requirements",
                "expires_at",
            },
            optional={"policy_ref"},
            label="authorization",
        )
        _validate_uri(authorization["decision_ref"], "authorization.decision_ref")
        if "policy_ref" in authorization:
            _validate_uri(authorization["policy_ref"], "authorization.policy_ref")
        if authorization["outcome"] != "allow":
            raise ContractViolation(
                "manifest_invalid",
                "only a final allow outcome is executable",
            )
        if not isinstance(authorization["granted_constraints"], dict):
            raise ContractViolation(
                "manifest_invalid",
                "granted_constraints must be an object",
            )
        validate_canonical_value(authorization["granted_constraints"])

        approval_refs = authorization["approval_refs"]
        if not isinstance(approval_refs, list) or len(approval_refs) > 16:
            raise ContractViolation(
                "manifest_invalid",
                "approval_refs must be a bounded array",
            )
        for index, item in enumerate(approval_refs):
            _validate_uri(item, f"approval_refs[{index}]")

        requirements = authorization["evidence_requirements"]
        if not isinstance(requirements, dict):
            raise ContractViolation(
                "manifest_invalid",
                "evidence_requirements must be an object",
            )
        _require_exact_keys(
            requirements,
            required={"before_execution", "completion"},
            label="evidence_requirements",
        )
        for name in ("before_execution", "completion"):
            items = requirements[name]
            if not isinstance(items, list) or len(items) > 16:
                raise ContractViolation(
                    "manifest_invalid",
                    f"{name} must be a bounded array",
                )
            for index, item in enumerate(items):
                _validate_uri(item, f"{name}[{index}]")

        issued_at = parse_timestamp(manifest["issued_at"], "issued_at")
        manifest_expires = parse_timestamp(
            authorization["expires_at"],
            "authorization.expires_at",
        )
        current = parse_timestamp(now, "now")
        if manifest_expires <= issued_at or manifest_expires <= current:
            raise ContractViolation(
                "manifest_expired",
                "manifest authorization has expired",
            )
        if "expires_at" in request:
            request_expires = parse_timestamp(
                request["expires_at"],
                "request.expires_at",
            )
            if manifest_expires > request_expires:
                raise ContractViolation(
                    "manifest_widening",
                    "manifest expiry widens request expiry",
                )

        capability = request["capability"]["name"]
        if capability == "example.echo":
            constraints = authorization["granted_constraints"]
            _require_exact_keys(
                constraints,
                required={"max_output_bytes"},
                label="example.echo granted_constraints",
            )
            granted = constraints["max_output_bytes"]
            requested = request["payload"]["max_output_bytes"]
            if (
                not isinstance(granted, int)
                or isinstance(granted, bool)
                or granted < 1
                or granted > requested
            ):
                raise ContractViolation(
                    "manifest_widening",
                    "example.echo granted max_output_bytes widens or invalidates the request",
                )
        return manifest
    except ContractViolation as exc:
        if exc.code.startswith("manifest_"):
            raise
        raise ContractViolation("manifest_invalid", exc.detail) from exc


def execute_echo(manifest: dict[str, Any], *, now: str) -> dict[str, Any]:
    validate_manifest(manifest, now=now)
    request = manifest["request"]
    if request["capability"] != {"name": "example.echo", "schema_version": "1"}:
        raise ContractViolation(
            "provider_failed",
            "reference provider supports only example.echo v1",
        )
    payload = request["payload"]
    messages = [payload["message"] for _ in range(payload["repeat"])]
    output_bytes = sum(len(message.encode("utf-8")) for message in messages)
    granted = manifest["authorization"]["granted_constraints"]["max_output_bytes"]
    if output_bytes > granted:
        raise ContractViolation(
            "provider_failed",
            "echo output exceeds granted constraint",
        )
    return {
        "messages": messages,
        "output_bytes": output_bytes,
        "request_digest": manifest["request_digest"],
    }


@dataclass
class StoredRequest:
    digest: str
    submission: dict[str, Any]
    status: dict[str, Any]
    dispatch_count: int


class InMemoryGateway:
    """Bounded no-effect demonstration, not a production gateway or policy engine."""

    def __init__(
        self,
        *,
        actor_ref: str,
        admitted_capabilities: set[str] | frozenset[str] = frozenset({"example.echo"}),
        max_requests: int = MAX_RETAINED_REQUESTS,
    ) -> None:
        _validate_uri(actor_ref, "actor_ref")
        if max_requests < 1 or max_requests > MAX_RETAINED_REQUESTS:
            raise ValueError(f"max_requests must be from 1 to {MAX_RETAINED_REQUESTS}")
        self.actor_ref = actor_ref
        self.admitted_capabilities = frozenset(admitted_capabilities)
        self.max_requests = max_requests
        self._requests: dict[str, StoredRequest] = {}

    def submit_and_execute(
        self,
        raw_request: bytes,
        *,
        now: str,
        decision_ref: str = "urn:anthesis:decision:synthetic-allow",
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        value = parse_json_bytes(raw_request)
        request = validate_request(value)
        digest = request_digest(request)
        request_id = request["request_id"]

        existing = self._requests.get(request_id)
        if existing is not None:
            if existing.digest != digest:
                raise ContractViolation(
                    "request_id_conflict",
                    "request_id is already bound to a different request digest",
                )
            return copy.deepcopy(existing.submission), copy.deepcopy(existing.status)

        if len(self._requests) >= self.max_requests:
            raise ContractViolation(
                "state_limit_exceeded",
                "reference gateway retained-state limit reached",
                retryable=True,
            )
        capability_name = request["capability"]["name"]
        if capability_name not in self.admitted_capabilities:
            raise ContractViolation(
                "capability_not_admitted",
                "transport profile does not admit the requested capability",
            )

        manifest = build_manifest(
            request,
            manifest_id=f"manifest_{request_id[4:]}",
            actor_ref=self.actor_ref,
            authentication_method="loopback-profile",
            decision_ref=decision_ref,
            issued_at=now,
            expires_at=request.get("expires_at", "2099-01-01T00:00:00Z"),
            granted_constraints={
                "max_output_bytes": request["payload"]["max_output_bytes"]
            },
        )
        result = execute_echo(manifest, now=now)
        operation_ref = f"urn:dubnium:operation:{request_id[4:]}"
        evidence = [
            {
                "kind": "conformance-result",
                "reference": f"urn:dubnium:evidence:{request_id[4:]}",
                "digest": "sha256:"
                + hashlib.sha256(canonical_bytes(result)).hexdigest(),
            }
        ]
        submission = {
            "contract_version": "1",
            "request_id": request_id,
            "outcome": "accepted",
            "request_digest": digest,
            "status_ref": f"urn:dubnium:capability-request:{request_id}",
            "submitted_at": now,
        }
        status = {
            "contract_version": "1",
            "request_id": request_id,
            "request_digest": digest,
            "gateway_state": "succeeded",
            "provider_operation": {
                "reference": operation_ref,
                "state": "succeeded",
            },
            "result": result,
            "evidence": evidence,
            "updated_at": now,
        }
        self._requests[request_id] = StoredRequest(
            digest=digest,
            submission=copy.deepcopy(submission),
            status=copy.deepcopy(status),
            dispatch_count=1,
        )
        return submission, status

    def status(self, request_id: str) -> dict[str, Any] | None:
        record = self._requests.get(request_id)
        return copy.deepcopy(record.status) if record is not None else None

    def dispatch_count(self, request_id: str) -> int:
        record = self._requests.get(request_id)
        return record.dispatch_count if record is not None else 0
