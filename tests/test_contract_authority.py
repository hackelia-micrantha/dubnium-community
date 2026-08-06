from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SUPERSEDED_REQUEST_DIGEST = "sha256:0b5acd7911285ce29fba5d3bded3e3fb370bba5c956c6086c27e3e4cc39898bf"
SUPERSEDED_PAYLOAD_DIGEST = "sha256:516d7c32a0bda4cef508a98712c5e7bc7d58863638b8e704b0559a9ceaa4bc67"
ALLOWED_NEGATIVE_DIGEST_FIXTURES = {
    Path("conformance/fixtures/v1/negative/manifest-digest-mismatch.json"),
}


class ContractAuthorityTests(unittest.TestCase):
    def test_normative_spec_uses_corrected_semantics(self) -> None:
        text = (ROOT / "spec" / "capability-gateway-v1.md").read_text(encoding="utf-8")
        self.assertIn("RFC 8785", text)
        self.assertIn("dubnium.capability-request.v1\\0", text)
        self.assertIn("dubnium.capability-payload.v1\\0", text)
        self.assertIn("Unicode normalization is prohibited", text)
        self.assertNotIn("normalize every string and object key to Unicode NFC", text)

    def test_public_entrypoint_delegates_to_corrected_modules(self) -> None:
        text = (ROOT / "conformance" / "capability_gateway_v1.py").read_text(encoding="utf-8")
        self.assertIn("from conformance.jcs_v1 import", text)
        self.assertIn("from conformance.request_contract_v1 import", text)
        self.assertNotIn("import unicodedata", text)
        self.assertNotIn("def canonical_json_bytes", text)
        self.assertNotIn("def normalize_request", text)

    def test_envelope_cli_uses_repository_owned_fixture_root(self) -> None:
        text = (ROOT / "conformance" / "gateway_envelopes_v1.py").read_text(encoding="utf-8")
        self.assertIn('CANONICAL_FIXTURE_ROOT = Path(__file__).resolve().parent / "envelopes" / "v1"', text)
        self.assertIn("run_fixture_suite(CANONICAL_FIXTURE_ROOT)", text)
        self.assertNotIn("else args.root", text)

    def test_public_contract_tree_contains_no_superseded_digest(self) -> None:
        roots = ("api", "conformance", "examples", "schemas", "spec")
        offenders: list[str] = []
        for name in roots:
            for path in (ROOT / name).rglob("*"):
                if not path.is_file() or path.suffix not in {".json", ".md", ".py", ".txt"}:
                    continue
                relative = path.relative_to(ROOT)
                if relative in ALLOWED_NEGATIVE_DIGEST_FIXTURES:
                    continue
                text = path.read_text(encoding="utf-8")
                if SUPERSEDED_REQUEST_DIGEST in text or SUPERSEDED_PAYLOAD_DIGEST in text:
                    offenders.append(relative.as_posix())
        self.assertEqual([], offenders)


if __name__ == "__main__":
    unittest.main()
