# Public roadmap

Status: experimental
Content: informative
Canonical source: this file
Generated: no
Reviewed: 2026-08-06

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
- a repository-owned tool for applying and checking `main` branch protection and merge policy.

The repository remains incubating. Presence does not imply a stable compatibility commitment. No protected `contract-v*` release has yet been accepted as consumer identity.

## Now — complete activation gates

- complete the first generated `site/docs/**` publication pull request and verify Pages deployment at `/docs/`;
- verify publication no-op behavior and keep generated changes confined to `site/docs/**`;
- apply and read back the committed `main` protection and squash-only merge policy;
- establish immutable `contract-v*` tag protection or an equivalent audited administrative control;
- publish the tag named by `release/contract-bundle-version.txt` only from the current protected `main` commit;
- require the post-publication consumer job to verify checksums, provenance, safe extraction, the embedded manifest, and public conformance;
- record release and protection evidence on the public tracking issues.

## Next — adopter integration and release maturity

- improve contract integration documentation and synthetic examples;
- pin the immutable release tag, source commit, archive digest, and verified attestation in each consumer;
- exercise public conformance against independent and private consumers at the contract boundary;
- refine compatibility, deprecation, and migration guidance from actual consumer feedback;
- expand public threat models without disclosing production policy or topology;
- complete one supersession or maintenance exercise without replacing published artifacts.

## Later — evidence-driven expansion

After at least one real release and maintenance cycle, maintainers may consider:

- thin public validation or conformance commands;
- additional adapters or language bindings justified by real consumers;
- a stabilized model-gateway compatibility profile when interoperability evidence supports it;
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
- host topology, runner configuration, credentials, and runbooks;
- real operational evidence or measurements;
- broad multi-language SDK matrices.

## Roadmap governance

Public direction belongs in this file and public issues. Private project planning, internal issue identifiers, private repository coordinates, and operational delivery sequencing are intentionally out of scope.
