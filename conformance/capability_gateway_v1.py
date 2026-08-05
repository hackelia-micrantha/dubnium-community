#!/usr/bin/env python3
"""Canonical public entrypoint for Capability Gateway v1alpha conformance."""

from __future__ import annotations

from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from conformance.contract_primitives_v1 import ContractError
from conformance.fixture_suite_v1 import main, run_fixture_suite
from conformance.jcs_v1 import (
    PAYLOAD_DIGEST_DOMAIN,
    REQUEST_DIGEST_DOMAIN,
    canonical_json_bytes,
    digest_value,
    load_json,
    normalize_json,
    parse_json_bytes,
)
from conformance.manifest_contract_v1 import validate_manifest
from conformance.reference_runtime_v1 import BoundedRequestRegistry, execute_no_effect
from conformance.request_contract_v1 import normalize_request, request_digest

__all__ = [
    "BoundedRequestRegistry",
    "ContractError",
    "PAYLOAD_DIGEST_DOMAIN",
    "REQUEST_DIGEST_DOMAIN",
    "canonical_json_bytes",
    "digest_value",
    "execute_no_effect",
    "load_json",
    "main",
    "normalize_json",
    "normalize_request",
    "parse_json_bytes",
    "request_digest",
    "run_fixture_suite",
    "validate_manifest",
]

if __name__ == "__main__":
    raise SystemExit(main())
