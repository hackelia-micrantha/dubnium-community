# Dubnium Community

**Public contracts, conformance assets, developer tooling, documentation, and safe reference implementations for the Dubnium capability ecosystem.**

Dubnium is a reproducible, observable, governed engineering environment for developer workstations, replaceable client environments, build and compute nodes, and AI-assisted automation. This repository is its public community and interoperability boundary. It is not a mirror of any private production runtime.

## What this repository owns

This monorepo is authoritative for public Dubnium-owned:

- specifications and machine-readable schemas;
- compatibility, canonicalization, and error semantics;
- synthetic conformance fixtures and tests;
- thin public clients, validators, and authoring libraries;
- minimal no-effect reference implementations;
- examples, architecture, threat models, and release documentation;
- the complete public website under `site/`;
- the bounded public roadmap.

Private or external implementations may consume these contracts, but public artifacts must build and validate without private source, private services, credentials, host configuration, operator data, or production policy.

## Public architecture

The public design treats Dubnium as an engineering-environment platform rather than one mandatory machine shape. Public concepts include replaceable clients, richer workstations, bounded build/compute capacity, remote managed environments for stronger trust requirements, reproducible project tooling, local-first observability, and governed automation.

AI is a capability of the environment, not an authority for it. Model-assisted work can propose intent, while deterministic validation, policy, bounded capabilities, durable state, resource controls, and evidence remain explicit system concerns.

These concepts are directional architecture, not a claim that every deployment form or capability is currently available.

## Website and documentation

This repository is the sole authority for the public web surface.

| Path / system | Ownership |
| --- | --- |
| `site/index.html` and adjacent assets | Hand-maintained public landing page |
| `site/docs/**` | Generated public mdBook artifact; changed only through the guarded publication path |
| `PUBLICATION_BOUNDARY.md` | Normative public disclosure and publication contract |
| `scripts/validate_publication.py` | Destination-side disclosure, metadata, size, and path guard |
| `wrangler.jsonc` | Cloudflare Workers Static Assets configuration |
| `.github/workflows/pages.yml` | GitHub-side publication validation and Wrangler dry run |
| Cloudflare Workers Builds Git integration | Preview and production deployment authority |

The GitHub workflow filename is retained for repository-policy compatibility; it does not deploy GitHub Pages. GitHub Actions validates the repository artifact while Cloudflare's connected Git integration performs deployments. Maintaining one deploy authority avoids duplicate production uploads and duplicated Cloudflare credentials.

Every site-related pull request runs publication tests, destination validation, and a Wrangler deployment dry run. Cloudflare independently creates branch previews and reports build status back to GitHub. See [docs/public-site-deployment.md](docs/public-site-deployment.md) for verification and rollback guidance.

The generated book is a curated conceptual overview. Its producer uses an explicit source-file allowlist; unlinked source pages are not a publication mechanism. Public output must not contain production topology, policy internals, prompts, memory behavior, privileged providers, host configuration, credentials, operational evidence, private repository coordinates, private commits, workflow identifiers, or private issue links.

See [PUBLICATION_BOUNDARY.md](PUBLICATION_BOUNDARY.md) for the complete ownership and metadata contract.

## Public/private product boundary

Public contracts can describe an integration boundary without publishing the production implementation behind it.

Private by default:

- supervisor planning, routing, prompts, retries, fallbacks, and specialist selection;
- production policy, approvals, risk thresholds, and trusted identities;
- memory ranking, consolidation, retention, trust scoring, and stored data;
- privileged capability providers, deployment workers, and recovery behavior;
- host or fleet topology, runner mappings, credentials, local paths, and runbooks;
- real logs, incidents, traces, evidence, and operational measurements.

Anthesis remains authoritative for governance decision and approval semantics where those contracts are referenced. Dubnium transports and enforces bounded decisions; it does not redefine Anthesis policy authority here.

The relationship between independently useful community assets and possible supported/commercial offerings is documented in [COMMUNITY_COMMERCIAL_BOUNDARY.md](COMMUNITY_COMMERCIAL_BOUNDARY.md).

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
| `site/` | Deployed public website and generated guide; never canonical specification source |

Dependency direction is intentionally one-way:

```text
specifications and schemas
  -> generated public types and API bindings
    -> validators, clients, conformance, and references
      -> external and private consumers
```

Public content must not depend on private Git repositories, private registries, absolute local paths, private runtime endpoints, production policy, or operator configuration.

## CI, conformance, and release posture

`Contract CI / contract-gate` runs on pull requests and `main` pushes. It validates change classification, repository policy, GitHub Actions trust boundaries, dependency changes, bounded contract parsing, change records, and the validator test suite.

`Contract Release CI / consume-release` builds the candidate bundle twice, requires byte-for-byte reproducibility, uploads it as a workflow artifact, and verifies it from a separate consumer job. Public-site validation independently checks the complete `site/` artifact and Wrangler packaging; Cloudflare Workers Builds independently reports preview and production build status.

Repository settings are expected to require the aggregate checks, but committed workflow and policy files do not prove that GitHub protection is active. Verify active settings with `scripts/apply_repository_policy.py check` before creating a release tag. See [docs/ci-security.md](docs/ci-security.md) and [docs/branch-protection.md](docs/branch-protection.md).

## Status and compatibility

The repository is **incubating**. Experimental capability-boundary contracts, conformance fixtures, deterministic release tooling, publication validation, and the public website are present; stabilization and adopter integration remain active work.

No `contract-v*` release is currently an accepted consumer baseline. Until the first protected release is accepted, `main` is development source rather than immutable contract identity.

Content is explicitly marked `experimental`, `v1alpha`, `v1beta`, or `stable`. Unmarked content is not a compatibility commitment. Compatibility and deprecation rules are defined in [COMPATIBILITY.md](COMPATIBILITY.md).

The current experimental slice defines a narrow Capability Gateway envelope with canonicalization, synthetic adversarial fixtures, conformance checks, and a no-effect reference. It does not include a production gateway, privileged providers, deployment implementation, supervisor, memory implementation, or host configuration.

## Community, security, and governance

- [ROADMAP.md](ROADMAP.md) — bounded public roadmap.
- [COMMUNITY_ENGAGEMENT.md](COMMUNITY_ENGAGEMENT.md) — community and outreach guidance.
- [DESIGN_PARTNER_GUIDE.md](DESIGN_PARTNER_GUIDE.md) — safe design-partner intake and feedback boundaries.
- [PUBLICATION_REVIEW_CHECKLIST.md](PUBLICATION_REVIEW_CHECKLIST.md) — disclosure and provenance review.
- [CONTRIBUTING.md](CONTRIBUTING.md) — contribution and contract-change requirements.
- [SECURITY.md](SECURITY.md) — private vulnerability reporting.
- [GOVERNANCE.md](GOVERNANCE.md) — maintainership and decision authority.

Every private-to-public import requires an irreversible-publication review covering ownership, patent and trade-secret posture, third-party provenance, secrets, operational disclosure, synthetic fixtures, generated metadata, and Git history.

## Licensing and marks

Code, specifications, schemas, documentation, and generated public artifacts are licensed under Apache License 2.0 unless a path contains an explicit, reviewed exception. See [LICENSING.md](LICENSING.md) and [NOTICE](NOTICE).

The source license does not grant rights to imply endorsement, certification, or official compatibility. See [TRADEMARKS.md](TRADEMARKS.md).
