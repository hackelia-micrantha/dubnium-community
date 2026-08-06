#!/usr/bin/env python3
"""Canonical CLI and compatibility entrypoint for Gateway v1alpha envelopes."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from conformance import capability_gateway_v1 as core
from conformance.gateway_envelope_core_v1 import (
    normalize_error,
    normalize_provider_operation,
    normalize_status,
    normalize_submission,
    run_envelope_fixture_suite,
    validate_status_transition,
)

CANONICAL_FIXTURE_ROOT = Path(__file__).resolve().parent / "envelopes" / "v1"

validate_submission = normalize_submission
validate_status = normalize_status
run_fixture_suite = run_envelope_fixture_suite


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("run-fixtures",))
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        help="Deprecated compatibility argument; canonical fixtures are repository-owned.",
    )
    parser.parse_args(argv)
    errors = run_fixture_suite(CANONICAL_FIXTURE_ROOT)
    if errors:
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Capability Gateway v1 envelope fixtures passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
