# Conformance

Status: experimental
Content: informative
Canonical source: this file
Generated: no

`conformance/` contains implementation-neutral suites, canonical vectors, and synthetic positive, negative, and adversarial fixtures.

Conformance targets are explicit. Remote targets are disabled by default, test execution is resource-bounded, and the suite MUST be capable of testing implementations other than the bundled reference.

A passing result is version- and profile-specific and does not imply security review, production suitability, endorsement, or certification.

## Contract bundle architecture

`service-bundles.json` declares each service contract's:

- normative specification;
- OpenAPI binding;
- canonical schema bundle;
- positive and negative examples;
- required OpenAPI paths and components;
- declarative JSON-pointer assertions.

Run all enrolled service bundles with:

```text
python3 -m conformance.contract_bundle conformance/service-bundles.json
```

`contract_bundle.py` is intentionally generic. Catalog entries cannot name Python hooks or runners. A new HTTP API SHOULD be added with data and contract artifacts, not a new script.

Contract-specific executable conformance remains appropriate only for behavior that cannot be represented through schemas, examples, and declarative assertions, such as RFC canonicalization or state-machine semantics. Shared behavior MUST be implemented once and reused by multiple contracts.
