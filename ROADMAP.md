# Public roadmap

Status: experimental
Content: informative
Canonical source: this file
Generated: no
Reviewed: 2026-11-17

This roadmap describes intended public work. It is not a compatibility promise, a private implementation plan, or a commitment to publish production internals.

## Product outcomes

- **Now — qualify reproducible, bounded execution.** Complete acceptance of the first experimental contract bundle and gather repeatable integration evidence; do not imply a stable distribution.
- **Next — make independent integration practical.** Improve public examples, conformance and interoperability with governed AI and self-hosted engineering workflows.
- **Later — validate adoption and supported deployment opportunities.** Use feedback from developers and design partners to determine where reproducible endpoints, private AI and supported integrations justify further investment.

These are directional outcomes, not dates, sales commitments, or claims of production qualification.

## Current state

The public foundation is in place:

- public/private product and publication boundaries;
- Apache-2.0 licensing and contribution provenance;
- governance, security, compatibility, trademark, and disclosure policies;
- repository-policy, contract, release, and public-site validation CI;
- the authoritative public landing page and generated-book deployment under `site/**`;
- schema-version-2 public-safe publication metadata with an opaque publication identifier and content digest;
- an experimental Capability Gateway contract slice;
- canonicalization, error, fixture, conformance, and no-effect reference assets;
- deterministic contract archive, manifest, checksum, SPDX, attestation, and consumer-verification tooling;
- a repository-owned tool for applying and checking `main` branch protection and merge policy;
- downstream v1alpha consumption feedback tracked through public contract issues;
- an active CloudEvents Event Contract v1 workstream (#54);
- an active Resource Budget v1 contract/conformance workstream (#57);
- public operator CLI architecture work that now includes Unix-pipe composability and man-page expectations (#15).

The repository remains incubating. The first [experimental Capability Gateway contract bundle](https://github.com/hackelia-micrantha/dubnium-community/releases/tag/contract-v0.1.0-alpha.1) has been published and independently verified. The status-read and pre-dispatch uncertainty corrections (#29 and #31) are merged. Release acceptance, provenance review, and downstream qualification remain open; publication is not a stable compatibility commitment.

## Public architecture direction

Dubnium's public architecture now describes a broader engineering-environment model:

- replaceable client environments alongside richer workstations and bounded build/compute capacity;
- reproducible project tooling with supply-chain trust treated separately from reproducibility;
- local-first diagnostics and observable runtime behavior;
- bounded organizational posture without requiring indiscriminate workstation log collection;
- personal reports and journaling as a separate user-owned observability plane;
- AI and automation that propose work without inheriting ambient effect authority;
- recovery based on declared configuration plus explicitly classified mutable state;
- public contracts that separate capability/effect authority, event observation, resource budgets, authentication/sender binding, routing, and governance rather than collapsing them into one generic control plane;
- independently owned CLI tools that remain composable through stable process I/O contracts without requiring a shared implementation framework.

These are directional concepts. They do not imply a production fleet service, endpoint enrollment system, or publication of private implementation.

## Now — complete release acceptance and publication gates

- maintain the public-book source as an explicit reviewed file allowlist rather than relying on navigation alone;
- verify regenerated `site/docs/**` replaces stale generated pages and remains independently validated before deployment;
- maintain paired public source and generated-artifact parity; keep artifact-only changes confined to `site/docs/**`;
- maintain and verify protected-main and immutable-release controls;
- resolve the remaining release metadata and provenance acceptance questions under #17 without rewriting immutable artifacts;
- verify downstream consumption of an immutable release identity and digest, including attestation and conformance;
- retain independent post-publication checks for future release candidates.

## Next — adopter integration and active contract expansion

- improve contract integration documentation and synthetic examples;
- pin the immutable release tag, source commit, archive digest, and verified attestation in each consumer;
- exercise public conformance against independent and private consumers at the contract boundary;
- maintain the merged status-read and uncertainty conformance corrections as contracts evolve;
- develop the bounded synthetic runner/gateway walkthrough (#86) only after the required integration qualification;
- refine compatibility, deprecation, and migration guidance from actual consumer feedback;
- expand public threat models without disclosing production policy or topology;
- complete the CloudEvents Event Contract v1 profile, schemas, and conformance fixtures under #54;
- define Resource Budget v1 grant/usage/reservation semantics under #57, including CAD integer monetary accounting, parent/child narrowing, restart-safe consumed authority, and fail-closed unknown-cost handling;
- publish operator CLI/process conventions under #15 covering stdin/stdout/stderr separation, stable exit codes, deterministic machine output, pipe safety, SIGPIPE/closed-pipe behavior where relevant, and reproducible man pages;
- keep the standalone ownership of Micrantha tools explicit: Dubnium may compose them, but this repository does not become the canonical implementation or package owner for unrelated projects;
- document additional public API families only when interoperability value and disclosure review justify them;
- complete one supersession or maintenance exercise without replacing published artifacts.

## Later — evidence-driven expansion

After at least one real release and maintenance cycle, maintainers may consider:

- thin public validation or conformance commands;
- additional adapters or language bindings justified by real consumers;
- a stabilized provider-neutral model-gateway compatibility profile when interoperability evidence supports it;
- scheduler contracts when ownership, state, and retry semantics can be expressed without exposing private scheduling policy;
- memory API/result contracts where public semantics are useful without publishing ranking, retention, or stored user data;
- public fleet or endpoint contracts where they can remain useful without exposing topology, identity, or policy;
- additional contract slices with clear ownership and disclosure value;
- repository splits only when independent ownership or release cadence makes the monorepo harmful.

## Deferred by default

The following are not part of the public roadmap unless a separate disclosure review establishes a concrete interoperability need:

- supervisor or orchestration implementation;
- production prompts, routing, retries, and fallback behavior;
- provider credentials, private provider endpoints, live pricing feeds, and operational route-selection policy;
- production policy, approvals, thresholds, and trusted identities;
- memory implementation, ranking, retention, or stored data;
- scheduler ownership and exact state;
- deployment providers and privileged workers;
- host or fleet topology, runner configuration, credentials, and runbooks;
- real operational evidence or measurements;
- broad multi-language SDK matrices;
- canonical package/build ownership for independently maintained Micrantha tools.

## Roadmap governance

Public direction belongs in this file and public issues. Private project planning, internal issue identifiers, private repository coordinates, and operational delivery sequencing are intentionally out of scope.
