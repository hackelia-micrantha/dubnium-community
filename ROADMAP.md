# Public roadmap

Status: experimental
Content: informative
Canonical source: this file
Generated: no
Reviewed: 2026-08-12

This roadmap describes intended public work. It is not a compatibility promise, a private implementation plan, or a commitment to publish production internals.

## Current state

The public foundation is in place:

- public/private product and publication boundaries;
- Apache-2.0 licensing and contribution provenance;
- governance, security, compatibility, trademark, and disclosure policies;
- repository-policy, contract, release, and Pages CI;
- the authoritative public landing page and generated-book deployment under `site/**`;
- schema-version-2 public-safe publication metadata with an opaque publication identifier and content digest;
- an experimental Capability Gateway contract slice;
- canonicalization, error, fixture, conformance, and no-effect reference assets;
- deterministic contract archive, manifest, checksum, SPDX, attestation, and consumer-verification tooling;
- a repository-owned tool for applying and checking `main` branch protection and merge policy;
- downstream v1alpha consumption feedback tracked through public contract issues.

The repository remains incubating. Presence does not imply a stable compatibility commitment. No protected `contract-v*` release has yet been accepted as consumer identity.

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

## Now — complete activation and publication gates

- maintain the public-book source as an explicit reviewed file allowlist rather than relying on navigation alone;
- verify regenerated `site/docs/**` replaces stale generated pages and remains independently validated before deployment;
- verify publication no-op behavior and keep generated changes confined to `site/docs/**`;
- apply and read back the committed `main` protection and squash-only merge policy;
- establish immutable `contract-v*` tag protection or an equivalent audited administrative control;
- resolve or explicitly classify the v1alpha status-read `503` question in #29;
- resolve or explicitly classify the pre-dispatch `indeterminate` attribution question in #31;
- publish the tag named by `release/contract-bundle-version.txt` only from the current protected `main` commit;
- require the post-publication consumer job to verify checksums, provenance, safe extraction, the embedded manifest, and public conformance;
- record release and protection evidence on the public tracking issues.

## Next — adopter integration and release maturity

- improve contract integration documentation and synthetic examples;
- pin the immutable release tag, source commit, archive digest, and verified attestation in each consumer;
- exercise public conformance against independent and private consumers at the contract boundary;
- add positive fixtures for pre-dispatch and post-dispatch uncertainty once #31 selects a compatible model;
- keep transport error documentation and OpenAPI response sets aligned as #29 is resolved;
- refine compatibility, deprecation, and migration guidance from actual consumer feedback;
- expand public threat models without disclosing production policy or topology;
- document additional public API families only when interoperability value and disclosure review justify them;
- complete one supersession or maintenance exercise without replacing published artifacts.

## Later — evidence-driven expansion

After at least one real release and maintenance cycle, maintainers may consider:

- thin public validation or conformance commands;
- additional adapters or language bindings justified by real consumers;
- a stabilized model-gateway compatibility profile when interoperability evidence supports it;
- public fleet or endpoint contracts where they can remain useful without exposing topology, identity, or policy;
- additional contract slices with clear ownership and disclosure value;
- repository splits only when independent ownership or release cadence makes the monorepo harmful.

## Deferred by default

The following are not part of the public roadmap unless a separate disclosure review establishes a concrete interoperability need:

- supervisor or orchestration implementation;
- production prompts, routing, retries, and fallback behavior;
- production policy, approvals, thresholds, and trusted identities;
- memory implementation, ranking, retention, or stored data;
- scheduler ownership and exact state;
- deployment providers and privileged workers;
- host or fleet topology, runner configuration, credentials, and runbooks;
- real operational evidence or measurements;
- broad multi-language SDK matrices.

## Roadmap governance

Public direction belongs in this file and public issues. Private project planning, internal issue identifiers, private repository coordinates, and operational delivery sequencing are intentionally out of scope.
