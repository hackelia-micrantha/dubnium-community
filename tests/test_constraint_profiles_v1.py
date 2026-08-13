from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import unittest

from conformance import capability_gateway_v1 as contract
from conformance.jcs_v1 import payload_digest

ROOT = Path(__file__).resolve().parents[1]


def _resource_requested(value):
    if set(value) != {"max_cpu", "max_seconds"}:
        raise contract.ContractError(
            "constraint.resource_fields",
            "synthetic resource profile has unsupported requested fields",
        )
    cpu = value["max_cpu"]
    seconds = value["max_seconds"]
    if not isinstance(cpu, int) or isinstance(cpu, bool) or not 1 <= cpu <= 16:
        raise contract.ContractError(
            "constraint.max_cpu",
            "max_cpu must be an integer from 1 through 16",
        )
    if not isinstance(seconds, int) or isinstance(seconds, bool) or not 1 <= seconds <= 3600:
        raise contract.ContractError(
            "constraint.max_seconds",
            "max_seconds must be an integer from 1 through 3600",
        )
    return {"max_cpu": cpu, "max_seconds": seconds}


def _resource_granted(value, requested):
    if set(value) != {"max_cpu", "max_seconds"}:
        raise contract.ContractError(
            "constraint.resource_fields",
            "synthetic resource profile has unsupported granted fields",
        )
    normalized = _resource_requested(value)
    if normalized["max_cpu"] > requested["max_cpu"]:
        raise contract.ContractError(
            "manifest.constraint_widening",
            "granted max_cpu widens requested authority",
        )
    if normalized["max_seconds"] > requested["max_seconds"]:
        raise contract.ContractError(
            "manifest.constraint_widening",
            "granted max_seconds widens requested authority",
        )
    return normalized


RESOURCE_PROFILE = contract.ConstraintProfile(
    normalize_requested=_resource_requested,
    normalize_granted=_resource_granted,
)
RESOURCE_KEY = ("example.resource-bounded", 1)


class ConstraintProfilesV1Tests(unittest.TestCase):
    def setUp(self):
        fixtures = ROOT / "conformance" / "fixtures" / "v1" / "positive"
        self.base_request = contract.load_json(fixtures / "request.json")
        self.base_manifest = contract.load_json(fixtures / "authorized-manifest.json")
        self.registry = contract.DEFAULT_CONSTRAINT_PROFILES.extend(
            {RESOURCE_KEY: RESOURCE_PROFILE}
        )

    def resource_request(self):
        request = deepcopy(self.base_request)
        request["request_id"] = "resource-profile-request-1"
        request["capability"] = {
            "name": RESOURCE_KEY[0],
            "schema_version": RESOURCE_KEY[1],
        }
        request["payload"] = {"operation": "synthetic"}
        request["requested_constraints"] = {
            "max_cpu": 4,
            "max_seconds": 600,
        }
        return request

    def resource_manifest(self, request, *, max_cpu=2, max_seconds=300):
        manifest = deepcopy(self.base_manifest)
        digest = contract.request_digest(
            request,
            constraint_profiles=self.registry,
        )
        manifest["request_id"] = request["request_id"]
        manifest["request_digest"] = digest
        manifest["capability"] = deepcopy(request["capability"])
        manifest["normalized_payload"] = deepcopy(request["payload"])
        manifest["normalized_payload_digest"] = payload_digest(request["payload"])
        manifest["decision"]["request_digest"] = digest
        manifest["granted_constraints"] = {
            "max_cpu": max_cpu,
            "max_seconds": max_seconds,
        }
        return manifest

    def test_default_registry_preserves_unknown_capability_rejection(self):
        with self.assertRaises(contract.ContractError) as caught:
            contract.normalize_request(self.resource_request())
        self.assertEqual(caught.exception.code, "constraint.unsupported")

    def test_explicit_profile_accepts_exact_capability_and_binds_digest(self):
        request = self.resource_request()
        normalized = contract.normalize_request(
            request,
            constraint_profiles=self.registry,
        )
        self.assertEqual(
            normalized["requested_constraints"],
            {"max_cpu": 4, "max_seconds": 600},
        )
        first = contract.request_digest(request, constraint_profiles=self.registry)
        changed = deepcopy(request)
        changed["requested_constraints"]["max_cpu"] = 3
        second = contract.request_digest(changed, constraint_profiles=self.registry)
        self.assertNotEqual(first, second)

    def test_narrowed_manifest_constraints_are_accepted(self):
        request = self.resource_request()
        manifest = self.resource_manifest(request)
        normalized = contract.validate_manifest(
            request,
            manifest,
            now=datetime(2030, 1, 1, tzinfo=timezone.utc),
            constraint_profiles=self.registry,
        )
        self.assertEqual(
            normalized["granted_constraints"],
            {"max_cpu": 2, "max_seconds": 300},
        )

    def test_equal_manifest_constraints_are_accepted(self):
        request = self.resource_request()
        manifest = self.resource_manifest(request, max_cpu=4, max_seconds=600)
        normalized = contract.validate_manifest(
            request,
            manifest,
            now=datetime(2030, 1, 1, tzinfo=timezone.utc),
            constraint_profiles=self.registry,
        )
        self.assertEqual(normalized["granted_constraints"], request["requested_constraints"])

    def test_widened_manifest_constraints_fail_closed(self):
        request = self.resource_request()
        manifest = self.resource_manifest(request, max_cpu=5, max_seconds=600)
        with self.assertRaises(contract.ContractError) as caught:
            contract.validate_manifest(
                request,
                manifest,
                now=datetime(2030, 1, 1, tzinfo=timezone.utc),
                constraint_profiles=self.registry,
            )
        self.assertEqual(caught.exception.code, "manifest.constraint_widening")

    def test_wrong_capability_does_not_reuse_registered_profile(self):
        request = self.resource_request()
        request["capability"] = {"name": "example.other", "schema_version": 1}
        with self.assertRaises(contract.ContractError) as caught:
            contract.normalize_request(
                request,
                constraint_profiles=self.registry,
            )
        self.assertEqual(caught.exception.code, "constraint.unsupported")

    def test_unknown_profile_fields_fail_closed(self):
        request = self.resource_request()
        request["requested_constraints"]["gpu"] = 1
        with self.assertRaises(contract.ContractError) as caught:
            contract.normalize_request(
                request,
                constraint_profiles=self.registry,
            )
        self.assertEqual(caught.exception.code, "constraint.resource_fields")

    def test_builtin_profile_cannot_be_overridden_by_extension(self):
        with self.assertRaises(ValueError):
            contract.DEFAULT_CONSTRAINT_PROFILES.extend(
                {("example.noop", 1): RESOURCE_PROFILE}
            )


if __name__ == "__main__":
    unittest.main()
