"""No-effect provider and bounded request-id registry for v1alpha conformance."""

from __future__ import annotations

from typing import Any

from .constraint_profiles_v1 import DEFAULT_CONSTRAINT_PROFILES, ConstraintProfileRegistry
from .jcs_v1 import ContractError, canonical_json_bytes
from .manifest_contract_v1 import validate_manifest
from .request_contract_v1 import normalize_request, request_digest

MAX_RETAINED_REQUESTS = 128


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
        "request_digest": request_digest(request),
        "status": "succeeded",
        "output": output,
    }


class BoundedRequestRegistry:
    """Bounded in-memory idempotency model; not production persistence."""

    def __init__(
        self,
        *,
        max_entries: int = MAX_RETAINED_REQUESTS,
        constraint_profiles: ConstraintProfileRegistry = DEFAULT_CONSTRAINT_PROFILES,
    ):
        if max_entries < 1 or max_entries > MAX_RETAINED_REQUESTS:
            raise ValueError(f"max_entries must be from 1 through {MAX_RETAINED_REQUESTS}")
        if not isinstance(constraint_profiles, ConstraintProfileRegistry):
            raise TypeError("constraint_profiles must be a ConstraintProfileRegistry")
        self.max_entries = max_entries
        self.constraint_profiles = constraint_profiles
        self._digests: dict[str, str] = {}
        self._dispatch_counts: dict[str, int] = {}

    def bind(self, request_document: Any) -> str:
        request = normalize_request(
            request_document,
            constraint_profiles=self.constraint_profiles,
        )
        request_id = request["request_id"]
        digest = request_digest(
            request,
            constraint_profiles=self.constraint_profiles,
        )
        existing = self._digests.get(request_id)
        if existing is not None:
            if existing != digest:
                raise ContractError(
                    "request.id_conflict",
                    "request_id is already bound to a different normalized request digest",
                )
            return "existing"
        if len(self._digests) >= self.max_entries:
            raise ContractError(
                "state.limit_exceeded",
                "bounded reference request registry is full",
                retryable=True,
            )
        self._digests[request_id] = digest
        self._dispatch_counts[request_id] = 0
        return "new"

    def mark_dispatched(self, request_id: str) -> None:
        if request_id not in self._digests:
            raise ContractError("request.not_found", "request_id is not retained")
        if self._dispatch_counts[request_id] == 0:
            self._dispatch_counts[request_id] = 1

    def dispatch_count(self, request_id: str) -> int:
        return self._dispatch_counts.get(request_id, 0)
