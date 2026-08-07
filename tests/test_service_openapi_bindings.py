from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from conformance.contract_bundle import (
    check_example,
    lint_schema_node,
    validate_catalog,
)


ROOT = Path(__file__).parents[1]
CATALOG = ROOT / "conformance" / "service-bundles.json"


class ContractBundleTests(unittest.TestCase):
    def test_all_catalogued_service_bundles_pass(self) -> None:
        self.assertEqual([], validate_catalog(CATALOG))

    def test_catalog_contains_complete_service_api_set(self) -> None:
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        self.assertEqual(
            {
                "memory-service-v1alpha",
                "supervisor-gateway-v1alpha",
                "scheduler-v1alpha",
            },
            {bundle["id"] for bundle in catalog["bundles"]},
        )
        for bundle in catalog["bundles"]:
            self.assertTrue(bundle["spec"].startswith("spec/"))
            self.assertTrue(bundle["openapi"].startswith("api/"))
            self.assertTrue(bundle["schemas"])
            self.assertTrue(bundle["examples"]["positive"])
            self.assertTrue(bundle["examples"]["negative"])
            self.assertTrue(bundle["operations"])
            self.assertTrue(bundle["schema_bindings"])
            self.assertTrue(bundle["required_schema_defs"])
            self.assertNotIn("script", bundle)
            self.assertNotIn("runner", bundle)
            self.assertNotIn("hook", bundle)

    def test_every_openapi_operation_has_positive_examples(self) -> None:
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        for bundle in catalog["bundles"]:
            document = json.loads((ROOT / bundle["openapi"]).read_text(encoding="utf-8"))
            operation_ids = {
                operation["operationId"]
                for path_item in document["paths"].values()
                for method, operation in path_item.items()
                if method.lower()
                in {"get", "put", "post", "delete", "options", "head", "patch", "trace"}
            }
            self.assertEqual(operation_ids, set(bundle["operations"]))
            positive = set(bundle["examples"]["positive"])
            for paths in bundle["operations"].values():
                self.assertTrue(paths)
                self.assertTrue(set(paths).issubset(positive))

    def test_negative_examples_fail_when_treated_as_positive(self) -> None:
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        for bundle in catalog["bundles"]:
            schemas = {(ROOT / item).resolve() for item in bundle["schemas"]}
            for relative in bundle["examples"]["negative"]:
                errors = check_example(
                    ROOT / relative,
                    valid=True,
                    schemas=schemas,
                    root=ROOT,
                )
                self.assertTrue(errors, relative)

    def test_catalog_rejects_contract_specific_code_hooks(self) -> None:
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        catalog["bundles"][0]["runner"] = "memory_service.py"
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory) / "conformance"
            copied.mkdir(parents=True)
            candidate = copied / "service-bundles.json"
            candidate.write_text(json.dumps(catalog), encoding="utf-8")
            errors = validate_catalog(candidate)
        self.assertTrue(
            any("code hooks" in error and "prohibited" in error for error in errors)
        )

    def test_schema_keyword_validation_fails_closed(self) -> None:
        errors = lint_schema_node(
            {
                "type": "string",
                "maxBytez": 32,
            }
        )
        self.assertTrue(any("unsupported schema keywords" in error for error in errors))

    def test_supervisor_prompt_schema_matches_truncation_behavior(self) -> None:
        schema = json.loads(
            (
                ROOT / "schemas/v1alpha/supervisor-gateway.schema.json"
            ).read_text(encoding="utf-8")
        )
        prompt = schema["$defs"]["SpecialistRequest"]["properties"]["input"][
            "properties"
        ]["prompt"]
        self.assertNotIn("maxLength", prompt)
        self.assertIn("truncates", prompt["description"])

    def test_scheduler_history_is_bounded_and_classified(self) -> None:
        schema = json.loads(
            (ROOT / "schemas/v1alpha/scheduler.schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            20,
            schema["$defs"]["HistoryResponse"]["properties"]["history"]["maxItems"],
        )
        specification = (ROOT / "spec/scheduler-v1alpha.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("does not redact", specification)
        self.assertIn("does not attest", specification)

    def test_new_service_bundles_add_no_per_api_python_entrypoints(self) -> None:
        prohibited_prefixes = (
            "memory_service",
            "supervisor_gateway",
            "scheduler_api",
            "scheduler_v1alpha",
        )
        python_files = [path.name for path in (ROOT / "conformance").glob("*.py")]
        self.assertFalse(
            [name for name in python_files if name.startswith(prohibited_prefixes)],
            python_files,
        )


if __name__ == "__main__":
    unittest.main()
