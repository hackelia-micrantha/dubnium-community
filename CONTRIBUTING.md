# Contributing

Status: stable
Content: normative
Canonical source: this file
Generated: no

Contributions are welcome when they preserve the public-contract/private-runtime boundary and can be reviewed without private dependencies or undisclosed provenance.

## Before opening a change

Use an issue for changes that introduce or alter:

- a normative contract, schema, lifecycle, error code, canonicalization rule, or compatibility promise;
- a public package or reference implementation;
- licensing, governance, security, publication, or trademark policy;
- generated public material from a private producer.

Small documentation corrections may proceed directly to a pull request.

## Contribution requirements

Every contribution MUST:

- be independently buildable and reviewable from this public repository;
- avoid private Git repositories, private registries, local paths, private endpoints, credentials, production policy, operator configuration, and real operational evidence;
- use synthetic examples, identifiers, fixtures, timestamps, and data;
- identify canonical source and generated outputs;
- include tests or deterministic validation for behavioral changes;
- preserve the dependency direction documented in `docs/repository-layout.md`;
- follow `LICENSING.md`, `SECURITY.md`, `COMPATIBILITY.md`, and `TRADEMARKS.md`.

## Provenance and rights

Every merged contribution MUST include a sign-off in the final commit retained on `main`:

```text
Signed-off-by: Your Name <you@example.com>
```

When commits are squash-merged, the squash commit sign-off satisfies this requirement. Repositories that later enable per-commit DCO enforcement may require every submitted commit to be signed off as well.

The sign-off certifies that you created the contribution or otherwise have the right to submit it under the applicable repository license.

The pull request MUST disclose when material is:

- copied, adapted, translated, or generated from another source;
- subject to employer, client, school, or contract ownership;
- based on private Dubnium work;
- materially produced with an AI system;
- governed by a third-party license, notice, dataset, model, or media right.

Do not submit material when ownership or redistribution rights are uncertain.

## Contract changes

A normative contract change MUST include:

- the affected contract and stability level;
- compatibility classification;
- security and threat-model impact;
- schema and example changes;
- positive, negative, and adversarial fixtures;
- migration or deprecation notes when applicable;
- generated-artifact synchronization evidence;
- an explicit statement of what remains private.

Normative specifications use BCP 14 terms (`MUST`, `SHOULD`, `MAY`) and the metadata described in `docs/content-markers.md`.

## Contract bundles and tooling

An HTTP contract contribution SHOULD enroll its specification, OpenAPI binding, canonical schema, and examples in `conformance/service-bundles.json`.

Contract-specific paths, components, and invariants SHOULD be represented as catalog data and declarative assertions. Contributors MUST NOT add a per-API script merely to discover files, resolve references, validate examples, or report fixture results.

Reusable validation belongs in `conformance/` or a public package. A contract-specific executable requires an explicit explanation of why the behavior cannot be represented by the generic bundle runner or an existing shared primitive.

## Publication imports

Material derived from a private producer MUST use the publication-review template and satisfy `docs/publication-review.md`. Do not preserve private Git history by default. Import only a clean, allowlisted, human-reviewable artifact.

## Pull requests

Pull requests should be narrowly scoped and include:

- purpose and user impact;
- files and contracts affected;
- compatibility and security classification;
- provenance and licensing statement;
- validation performed;
- follow-up work intentionally excluded.

Maintainers may require changes, split a proposal, downgrade its stability, or defer it until a real consumer and conformance evidence exist.
