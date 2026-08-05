# Dubnium Community

**Public contracts, conformance assets, developer tooling, and safe reference implementations for the Dubnium capability ecosystem.**

Dubnium is a reproducible, local-first agentic development and operations environment. This repository is its public community and interoperability boundary. It is not a mirror of the private production runtime.

## Repository role

This monorepo is authoritative for public Dubnium-owned:

- specifications and machine-readable schemas;
- compatibility, canonicalization, and error semantics;
- synthetic conformance fixtures and tests;
- thin public clients, validators, and authoring libraries;
- minimal no-effect reference implementations;
- examples, architecture, threat models, and release documentation;
- the generated public site under `site/`.

The private Dubnium system may implement these contracts, but public artifacts must build and validate without private source, private services, credentials, host configuration, or operator data.

## Explicit boundary

Public contracts can describe an integration boundary without publishing the production implementation behind it.

Private by default:

- supervisor planning, routing, prompts, retries, fallbacks, and specialist selection;
- production policy, approvals, risk thresholds, and trusted identities;
- memory ranking, consolidation, retention, trust scoring, and stored data;
- privileged capability providers, deployment workers, and recovery behavior;
- NixOS host topology, runner mappings, credentials, local paths, and runbooks;
- real logs, incidents, traces, evidence, and operational measurements.

Anthesis remains authoritative for governance decision and approval semantics where those contracts are referenced. Dubnium transports and enforces bounded decisions; it does not redefine Anthesis policy authority here.

## Monorepo layout

| Path | Purpose |
| --- | --- |
| `spec/` | Normative Dubnium-owned protocol specifications |
| `schemas/` | Canonical machine-readable schemas |
| `api/` | Transport bindings such as OpenAPI descriptions |
| `changes/` | Reviewed compatibility, security, migration, and evidence records |
| `packages/` | Thin public libraries and validators |
| `conformance/` | Implementation-neutral test suites and fixtures |
| `reference/` | Deliberately non-production, no-effect implementations |
| `examples/` | Synthetic usage examples |
| `policy-examples/` | Synthetic, non-authoritative policy illustrations |
| `release/` | Inactive deterministic release tooling pending a real contract bundle |
| `docs/` | Architecture, process, threat-model, and publication documentation |
| `site/` | Generated public-site artifacts; never canonical specification source |

Each directory contains its own ownership and dependency rules. Empty areas are placeholders for reviewed work, not commitments to publish private implementation.

## Dependency direction

```text
specifications and schemas
  -> generated public types and API bindings
    -> public validators, clients, conformance, and references
      -> external and private consumers
```

Public content must not depend on private Git repositories, private registries, absolute local paths, private runtime endpoints, production policy, or operator configuration.

## CI and protection

`Contract CI / contract-gate` runs on every pull request and protected-branch push. It validates change classification, public repository policy, GitHub Actions trust boundaries, dependency changes, bounded contract parsing, change records, and the full validator test suite.

Repository settings must require the aggregate gate. See [docs/ci-security.md](docs/ci-security.md) and [docs/branch-protection.md](docs/branch-protection.md).

## Status and compatibility

The repository is **incubating**. Content is explicitly marked `experimental`, `v1alpha`, `v1beta`, or `stable`. Unmarked content is not a compatibility commitment.

The monorepo uses one coordinated release version initially. Compatibility and deprecation rules are defined in [COMPATIBILITY.md](COMPATIBILITY.md).

## Licensing and marks

Code, specifications, schemas, documentation, and generated public artifacts are licensed under Apache License 2.0 unless a path contains an explicit, reviewed exception. See [LICENSING.md](LICENSING.md) and [NOTICE](NOTICE).

The source license does not grant rights to imply endorsement, certification, or official compatibility. See [TRADEMARKS.md](TRADEMARKS.md).

## Contributing and security

- [CONTRIBUTING.md](CONTRIBUTING.md) — contribution, provenance, contract-change, and sign-off requirements.
- [SECURITY.md](SECURITY.md) — private vulnerability reporting and disclosure expectations.
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) — participation standards.
- [GOVERNANCE.md](GOVERNANCE.md) — maintainership and decision authority.
- [ROADMAP.md](ROADMAP.md) — bounded public roadmap.

Every private-to-public import requires an irreversible-publication review covering ownership, patent and trade-secret posture, third-party provenance, secrets, operational disclosure, synthetic fixtures, generated metadata, and Git history.

## Current first slice

The first planned contract slice is a narrow, experimental Capability Gateway envelope with canonicalization, synthetic adversarial fixtures, conformance checks, and a no-effect reference. It does not include the production gateway, privileged providers, deployment implementation, supervisor, memory implementation, or host configuration.
