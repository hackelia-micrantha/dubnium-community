# Compatibility policy

Status: stable
Content: normative
Canonical source: this file
Generated: no

## Stability levels

| Level | Intended use | Compatibility commitment |
| --- | --- | --- |
| `experimental` | exploration and design validation | none; changes may occur without migration support |
| `v1alpha` | early external evaluation | breaking changes allowed and documented in release notes |
| `v1beta` | feature-complete candidate | breaking changes require migration notes and at least 30 days or one coordinated release of notice, whichever is longer |
| `stable` | supported interoperability contract | breaking wire or API changes require a new major version; removals require at least 180 days and one minor release of deprecation notice |

A repository or product maturity label such as “incubating” does not replace the stability level of an individual contract.

## Versioning

The monorepo uses Semantic Versioning 2.0.0 for coordinated releases. All public packages and release artifacts use the same repository release version initially.

Wire contracts also carry an explicit contract version when package version alone cannot determine compatibility. Generated types record both the repository release and canonical schema version or digest.

Independent package versions require a governance decision based on a demonstrated consumer, ownership, or release-cadence need.

## Compatible changes

A change may be backward compatible only when the affected contract explicitly permits the behavior. Examples may include:

- adding an optional field whose absence preserves prior semantics;
- adding a new endpoint that does not change existing behavior;
- clarifying informative text without altering a normative requirement;
- adding a fixture or error detail without changing stable machine behavior.

## Breaking changes

Breaking changes include:

- removing or renaming a field, endpoint, enum value, error code, or required behavior;
- changing field type, units, precision, canonicalization, digest input, identity source, or default meaning;
- making an optional field required;
- widening authority, effects, constraints, accepted input, or trust assumptions;
- changing unknown-field or unknown-enum handling;
- changing generated output without updating its canonical schema relationship.

Security fixes may intentionally break unsafe behavior. They still require explicit release notes, impact analysis, and migration guidance when feasible.

## Unknown data

Unknown fields, enum values, versions, extensions, and media types fail closed unless the specific contract explicitly defines a safe forward-compatible rule.

Ignoring unknown authorization, identity, effect, constraint, canonicalization, or digest-bearing data is prohibited.

## Extensions

Extensions use a documented namespace and cannot weaken public requirements or claim public conformance for behavior outside the public contract. Private extensions remain behind adapters and are not added to canonical public schemas solely to accommodate a private implementation.

## Deprecation

A deprecation notice identifies:

- the affected contract and versions;
- replacement or migration path;
- earliest removal release and date;
- security or operational implications;
- conformance changes.

Experimental and alpha content may be removed without a formal window, but release notes should explain the change.

## Conformance

Conformance is version-specific and profile-specific. A claim must identify the contract version, conformance suite version, stability level, extensions, deviations, and test environment.

Passing conformance tests does not establish security, performance, production suitability, endorsement, or certification.
