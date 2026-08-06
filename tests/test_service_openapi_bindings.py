from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).parents[1]
SERVICE_SPECS = (
    ROOT / "api" / "memory-service" / "v1alpha" / "openapi.json",
    ROOT / "api" / "supervisor-gateway" / "v1alpha" / "openapi.json",
    ROOT / "api" / "scheduler" / "v1alpha" / "openapi.json",
)


def load(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(document, dict)
    return document


def iter_refs(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        ref = value.get("$ref")
        if isinstance(ref, str):
            yield ref
        for child in value.values():
            yield from iter_refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_refs(child)


def resolve_pointer(document: Any, pointer: str) -> Any:
    if pointer == "#":
        return document
    if not pointer.startswith("#/"):
        raise AssertionError(f"expected bundled JSON pointer, got {pointer}")
    value = document
    for raw_token in pointer[2:].split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if not isinstance(value, dict) or token not in value:
            raise AssertionError(f"unresolved JSON pointer: {pointer}")
        value = value[token]
    return value


class ServiceOpenApiBindingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.supervisor = load(SERVICE_SPECS[1])

    def test_all_service_refs_resolve_and_operation_ids_are_unique(self) -> None:
        for path in SERVICE_SPECS:
            document = load(path)
            for ref in iter_refs(document):
                resolve_pointer(document, ref)
            operation_ids: list[str] = []
            for path_item in document["paths"].values():
                for method, operation in path_item.items():
                    if method.lower() not in {
                        "get",
                        "put",
                        "post",
                        "delete",
                        "options",
                        "head",
                        "patch",
                        "trace",
                    }:
                        continue
                    operation_ids.append(operation["operationId"])
            self.assertEqual(
                len(operation_ids),
                len(set(operation_ids)),
                f"duplicate operationId in {path}",
            )

    def test_supervisor_binding_resolves_packaged_console_entry_point(self) -> None:
        source = self.supervisor["x-dubnium-canonical-source"]
        self.assertEqual("ryjen/dubnium", source["repository"])
        self.assertRegex(source["commit"], r"^[0-9a-f]{40}$")
        self.assertEqual("supervisor-gateway", source["console_script"])
        self.assertEqual(
            "dubnium_supervisor_gateway.lineage_app:main",
            source["entry_point"],
        )
        module, function = source["entry_point"].split(":", 1)
        self.assertEqual("main", function)
        module_suffix = "src/" + module.replace(".", "/") + ".py"
        self.assertTrue(
            any(path.endswith(module_suffix) for path in source["paths"]),
            f"entry-point module is absent from canonical paths: {module_suffix}",
        )
        self.assertTrue(
            {
                "pkgs/supervisor-gateway/pyproject.toml",
                "pkgs/supervisor-gateway/src/dubnium_supervisor_gateway/app.py",
                "pkgs/supervisor-gateway/src/dubnium_supervisor_gateway/contract.py",
                "pkgs/supervisor-gateway/src/dubnium_supervisor_gateway/contract_app.py",
                "pkgs/supervisor-gateway/src/dubnium_supervisor_gateway/lineage.py",
                "pkgs/supervisor-gateway/src/dubnium_supervisor_gateway/lineage_app.py",
            }.issubset(set(source["paths"]))
        )

    def test_supervisor_models_publish_contract_capabilities(self) -> None:
        model = self.supervisor["components"]["schemas"]["Model"]
        self.assertIn("dubnium", model["required"])
        capabilities = self.supervisor["components"]["schemas"]["AliasCapabilities"]
        properties = capabilities["properties"]
        self.assertTrue(properties["chat_completions"]["const"])
        self.assertTrue(properties["streaming"]["const"])
        self.assertFalse(properties["tools"]["const"])
        self.assertFalse(properties["structured_output"]["const"])
        self.assertEqual(
            ["temperature", "top_p"],
            properties["sampling_parameters"]["const"],
        )
        self.assertEqual(
            "dubnium.llm-gateway.v1",
            self.supervisor["x-dubnium-contract-version"],
        )

    def test_supervisor_request_requires_alias_and_omits_rejected_fields(self) -> None:
        request = self.supervisor["components"]["schemas"]["ChatCompletionRequest"]
        self.assertEqual(["model", "messages"], request["required"])
        self.assertNotIn("tools", request["properties"])
        self.assertNotIn("response_format", request["properties"])
        metadata = self.supervisor["components"]["schemas"]["DubniumRequestMetadata"]
        self.assertIn("contract_version", metadata["properties"])
        self.assertIn("capabilities", metadata["properties"])
        self.assertIn("specialist", metadata["properties"])

    def test_supervisor_response_records_trusted_execution_and_lineage(self) -> None:
        metadata = self.supervisor["components"]["schemas"]["DubniumResponseMetadata"]
        self.assertEqual(
            ["memory", "specialist", "authority", "execution"],
            metadata["required"],
        )
        self.assertIn("lineage", metadata["properties"])
        execution = self.supervisor["components"]["schemas"]["ExecutionIdentity"]
        self.assertIn("resolved", execution["required"])
        self.assertIn("fallback_chain", execution["required"])
        lineage = self.supervisor["components"]["schemas"]["DelegationLineage"]
        self.assertEqual(
            ["request_id", "supervisor", "specialist", "synthesis"],
            lineage["required"],
        )

    def test_supervisor_errors_include_contract_attribution(self) -> None:
        error = self.supervisor["components"]["schemas"]["Error"]["properties"]["error"]
        self.assertIn("dubnium", error["required"])
        attribution = self.supervisor["components"]["schemas"]["ErrorDubnium"]
        self.assertEqual(
            "dubnium.llm-gateway.v1",
            attribution["properties"]["contract_version"]["const"],
        )
        self.assertIn("retryable", attribution["required"])


if __name__ == "__main__":
    unittest.main()
