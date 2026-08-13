# Dubnium Community

**Public contracts, conformance assets, developer tooling, documentation, and safe reference implementations for the Dubnium capability ecosystem.**

Dubnium is a reproducible, observable, governed engineering environment for developer workstations, smaller client environments, build and compute nodes, and AI-assisted automation. This repository is its public community and interoperability boundary. It is not a mirror of any private production runtime.

## Repository role

This monorepo is authoritative for public Dubnium-owned:

- specifications and machine-readable schemas;
- compatibility, canonicalization, and error semantics;
- synthetic conformance fixtures and tests;
- thin public clients, validators, and authoring libraries;
- minimal no-effect reference implementations;
- examples, architecture, threat models, and release documentation;
- the complete deployed public website under `site/`;
- the bounded public roadmap.

Private or external implementations may consume these contracts, but public artifacts must build and validate without private source, private services, credentials, host configuration, operator data, or production policy.

## Public architecture direction

The public design treats Dubnium as an engineering-environment platform rather than one mandatory machine shape. Public concepts include replaceable client environments, richer workstations, bounded build/compute capacity, remote managed environments for stronger trust requirements, reproducible project tooling, local-first observability, and governed automation.

These concepts are directional architecture, not a claim that every deployment form or fleet capability is currently available. The public guide intentionally describes responsibilities and trust boundaries without revealing production topology or implementation policy.

## Public website ownership

This repository is the sole authority for the public web surface:

| Path | Ownership |
| --- | --- |
| `site/index.html` and site assets | Hand-maintained public landing page |
| `site/docs/**` | Generated public mdBook artifact; changed only through the guarded publication path |
| `.github/workflows/pages.yml` | Independent validation and GitHub Pages deployment |
| `scripts/validate_publication.py` | Destination-side disclosure, metadata, size, and path guard |

The generated book is a curated conceptual overview. Its producer uses an explicit source-file allowlist; unlinked source pages are not a publication mechanism. The generated artifact must not contain production topology, policy internals, prompts, private data behavior, privileged providers, host configuration, credentials, operational evidence, private repository coordinates, private commits, workflow identifiers, or private issue links.

See [PUBLICATION_BOUNDARY.md](PUBLICATION_BOUNDARY.md) for the complete ownership and metadata contract.

## Explicit product boundary

Public contracts can describe an integration boundary without publishing the production implementation behind it.

Private by default:

- supervisor planning, routing, prompts, retries, fallbacks, and specialist selection;
- production policy, approvals, risk thresholds, and trusted identities;
- private data ranking, consolidation, retention, trust scoring, and stored data;
- privileged capability providers, deployment workers, and recovery behavior;
- host or fleet topology, runner mappings, credentials, local paths, and runbooks;
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
| `release/` | Deterministic release tooling and public release evidence |
| `docs/` | Architecture, process, threat-model, and publication documentation |
| `site/` | Public website and generated documentation artifacts; never canonical specification source |

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

`Contract CI / contract-gate` runs on every pull request and `main` push. It validates change classification, public repository policy, GitHub Actions trust boundaries, dependency changes, bounded contract parsing, change records, and the full validator test suite.

`Contract Release CI / consume-release` builds the candidate bundle twice, requires byte-for-byte reproducibility, uploads it as a workflow artifact, and verifies it from a separate consumer job. The Pages workflow independently validates the entire `site/` artifact before deployment.

Repository settings are expected to require the aggregate checks, but committed workflow and policy files do not prove that GitHub protection is active. The active settings must be verified with `scripts/apply_repository_policy.py check` before any release tag is created. See [docs/ci-security.md](docs/ci-security.md) and [docs/branch-protection.md](docs/branch-protection.md).

## Status and compatibility

The repository is **incubating**. Experimental capability-boundary contracts, conformance fixtures, deterministic release tooling, publication validation, and the public website are present; stabilization and adopter integration remain active work.

Content is explicitly marked `experimental`, `v1alpha`, `v1beta`, or `stable`. Unmarked content is not a compatibility commitment. The monorepo uses one coordinated release version initially. Compatibility and deprecation rules are defined in [COMPATIBILITY.md](COMPATIBILITY.md).

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

## Current public contract slice

The current experimental contract work includes a narrow capability-boundary envelope with canonicalization, synthetic adversarial fixtures, conformance checks, and a no-effect reference. It does not include a production gateway, privileged providers, deployment implementation, supervisor implementation, private data implementation, or host configuration.

Consumers should pin reviewed immutable release identities when available, run the conformance suites, and avoid treating experimental source as a stable compatibility promise.
