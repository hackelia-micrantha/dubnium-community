from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


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


if __name__ == "__main__":
    unittest.main()
