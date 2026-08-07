# Conformance

Status: experimental
Content: informative
Canonical source: this file
Generated: no

`conformance/` contains implementation-neutral suites, canonical vectors, and synthetic positive, negative, and adversarial fixtures.

Conformance targets are explicit. Remote targets are disabled by default, execution is resource-bounded, and suites MUST be capable of testing implementations other than bundled references.

A passing result is version- and profile-specific and does not imply security review, production suitability, endorsement, or certification.

## HTTP contract bundles

`service-bundles.json` is the data-only catalog for HTTP contracts. Each entry declares:

- normative specification;
- OpenAPI binding;
- canonical schema bundle;
- positive and negative examples;
- exact operation-to-example coverage;
- required canonical definitions;
- schema-to-OpenAPI structural bindings;
- declarative OpenAPI assertions.

Run all enrolled bundles with:

```text
python3 -m conformance.contract_bundle conformance/service-bundles.json
```

`contract_bundle.py` is intentionally generic and fails closed on unknown catalog keys, unsupported schema keywords, remote references, repository escapes, incomplete operation coverage, and canonical/OpenAPI drift.

A new HTTP API SHOULD add data and artifacts, not a per-API script. Contract-specific executable conformance remains appropriate only for behavior that cannot be expressed through schemas, examples, and shared declarative primitives.
