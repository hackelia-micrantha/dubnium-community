# Public roadmap

Status: experimental
Content: informative
Canonical source: this file
Generated: no
Reviewed: 2026-08-12

This roadmap describes intended public work. It is not a compatibility promise, a private implementation plan, or a commitment to publish production internals.

## Current state

The public foundation includes:

- public/private product and publication boundaries;
- Apache-2.0 licensing and contribution provenance;
- governance, security, compatibility, trademark, and disclosure policies;
- repository-policy, contract, release, and Pages CI;
- the authoritative public landing page and generated-book deployment under `site/**`;
- public-safe publication metadata and destination validation;
- experimental capability-boundary contracts;
- canonicalization, error, fixture, conformance, and no-effect reference assets;
- deterministic contract archive, manifest, checksum, software-bill-of-materials, attestation, and consumer-verification tooling.

The repository remains incubating. Presence does not imply a stable compatibility commitment.

## Public architecture direction

Dubnium's public architecture now describes a broader engineering-environment model:

- replaceable client environments alongside richer workstations and bounded build/compute capacity;
- reproducible project tooling with supply-chain trust treated separately from reproducibility;
- local-first diagnostics and observable runtime behavior;
- bounded organizational posture without requiring indiscriminate workstation log collection;
- personal reports and journaling as a separate user-owned observability plane;
- AI and automation that propose work without inheriting ambient effect authority;
- recovery based on declared configuration plus explicitly classified mutable state.

These are directional concepts. They do not imply a production fleet service, endpoint enrollment system, or publication of private implementation.

## Now — publication and contract integrity

- maintain the public-book source as an explicit reviewed file allowlist rather than relying on navigation alone;
- verify regenerated `site/docs/**` replaces stale generated pages and remains independently validated before deployment;
- keep generated changes confined to `site/docs/**`;
- maintain repository and release protection appropriate to contract maturity;
- resolve compatibility questions through public contract issues and change records;
- preserve reproducible release, checksum, provenance, extraction, and conformance verification.

## Next — adopter integration and release maturity

- improve contract integration documentation and synthetic examples;
- consume immutable public releases with verified digests and attestations;
- exercise public conformance against independent and private consumers at the contract boundary;
- refine compatibility, deprecation, and migration guidance from actual consumer feedback;
- expand public threat models without disclosing production policy or topology;
- document additional public API families only when interoperability value and disclosure review justify them.

## Later — evidence-driven expansion

After real consumer and maintenance evidence exists, maintainers may consider:

- thin public validation or conformance commands;
- additional adapters or language bindings justified by real consumers;
- stabilized compatibility profiles for model-independent or endpoint-independent interfaces;
- public fleet or endpoint contracts where they can remain useful without exposing topology, identity, or policy;
- repository splits only when independent ownership or release cadence makes the monorepo harmful.

## Deferred by default

The following are not part of the public roadmap unless a separate disclosure review establishes a concrete interoperability need:

- supervisor or orchestration implementation;
- production prompts, routing, retries, and fallback behavior;
- production policy, approvals, thresholds, and trusted identities;
- private data implementation, ranking, retention, or stored content;
- scheduler implementation and exact private state;
- deployment providers and privileged workers;
- host or fleet topology, runner configuration, credentials, and runbooks;
- real operational evidence or measurements;
- broad multi-language SDK matrices.

## Roadmap governance

Public direction belongs in this file and public issues. Private project planning, internal issue identifiers, private repository coordinates, and operational delivery sequencing are intentionally out of scope.
