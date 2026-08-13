#!/usr/bin/env python3
"""Synthetic capability-specific constraint profile example.

This demonstrates trusted local profile registration only. It does not register a
provider, allocate a public capability name, or authorize an effect.
"""

from __future__ import annotations

from conformance import capability_gateway_v1 as contract


def normalize_requested(value):
    if set(value) != {"max_units"}:
        raise contract.ContractError(
            "constraint.synthetic_fields",
            "synthetic profile accepts only max_units",
        )
    maximum = value["max_units"]
    if not isinstance(maximum, int) or isinstance(maximum, bool) or not 1 <= maximum <= 8:
        raise contract.ContractError(
            "constraint.max_units",
            "max_units must be an integer from 1 through 8",
        )
    return {"max_units": maximum}


def normalize_granted(value, requested):
    granted = normalize_requested(value)
    if granted["max_units"] > requested["max_units"]:
        raise contract.ContractError(
            "manifest.constraint_widening",
            "granted max_units widens requested authority",
        )
    return granted


registry = contract.DEFAULT_CONSTRAINT_PROFILES.extend(
    {
        ("example.resource-bounded", 1): contract.ConstraintProfile(
            normalize_requested=normalize_requested,
            normalize_granted=normalize_granted,
        )
    }
)

request = {
    "contract_version": "1.0",
    "request_id": "synthetic-resource-request-1",
    "capability": {"name": "example.resource-bounded", "schema_version": 1},
    "target_ref": "resource:synthetic",
    "payload": {"operation": "demonstrate-profile"},
    "requested_constraints": {"max_units": 4},
    "evidence_refs": [],
    "requested_at": "2030-01-01T00:00:00Z",
}

normalized = contract.normalize_request(request, constraint_profiles=registry)
print(contract.canonical_json_bytes(normalized).decode("utf-8"))
print(contract.request_digest(request, constraint_profiles=registry))
