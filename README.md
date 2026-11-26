# Dubnium Community

**Open contracts and conformance for reproducible, local-first, governed engineering.**

Dubnium explores how reproducible development environments, self-hosted infrastructure and local-first AI can support secure, accountable automation. This repository is its public community and interoperability boundary. It is not a mirror of any private production runtime.

**For engineers, collaborators and independent implementers:** see [Start here](#start-here) and [How to help Dubnium](#how-to-help-dubnium).

## Start here

- [Project website](https://dubnium.micrantha.com/) — product direction, engineering progress and collaboration.
- [Research foundations](https://dubnium.micrantha.com/docs/research.html) — ranked public literature and research themes.
- [Technical Overview](https://dubnium.micrantha.com/docs/) — architecture, component responsibilities and design trade-offs.
- [Download the experimental Capability Gateway alpha bundle](https://github.com/hackelia-micrantha/dubnium-community/releases/tag/contract-v0.1.0-alpha.1) — contracts, manifest, checksums and SBOM.
- [Conformance](conformance/README.md) and [no-effect reference](reference/README.md) — evaluate the public contracts without private infrastructure or credentials.

From a checkout of this repository, run the enrolled HTTP contract suites with Python 3:

```sh
python3 -m conformance.contract_bundle conformance/service-bundles.json
```

A passing suite is evidence for the selected contract/profile, not certification or production qualification. The experimental release is not a generally available workstation distribution.

## Public architecture

The public design treats Dubnium as an engineering-environment platform rather than one mandatory machine shape. Public concepts include replaceable clients, richer workstations, bounded build/compute capacity, remote managed environments for stronger trust requirements, reproducible project tooling, local-first observability, and governed automation.

AI is a capability of the environment, not an authority for it. Model-assisted work can propose intent, while deterministic validation, policy, bounded capabilities, durable state, resource controls, and evidence remain explicit system concerns.

These concepts are directional architecture, not a claim that every deployment form or capability is currently available.

## Platform capabilities

Dubnium's architectural scope extends beyond a workstation and AI runtime:

- [**Governed execution and cryptographic identity**](https://dubnium.micrantha.com/docs/governance.html) — bound requests, decisions, identity and effects; experimental Capability Gateway conformance.
- [**Operator experience**](https://dubnium.micrantha.com/docs/operator-tooling.html) — composable CLI tools, experimental operator authentication, and mobile/web operator direction.
- [**Intelligence and automation**](https://dubnium.micrantha.com/docs/ai-and-automation.html) — local-first inference, model selection, memory, scheduling and advisory classification/prediction; multi-GPU and token-efficiency work remains under evaluation.
- [**Reproducible infrastructure and adaptive CI**](https://dubnium.micrantha.com/docs/runner-controller.html) — project-local Nix environments, trusted cache reuse, short-lived workers, resource-aware admission and developing dynamic CI planning.
- [**Supervisor-mediated ad hoc execution**](https://dubnium.micrantha.com/docs/runner-controller.html#supervisor-mediated-ad-hoc-runners) — planned bounded on-demand workloads independent of conventional CI assignment.
- [**Safe, staged AI-assisted self-healing**](https://dubnium.micrantha.com/docs/ai-and-automation.html#safe-staged-ai-assisted-self-healing) — research direction for isolated candidate validation, authorized recovery and independent verification.
- [**System lifecycle and recovery**](https://dubnium.micrantha.com/docs/reproducibility.html#system-lifecycle-and-verified-recovery) — developing reviewed updates, encrypted backup and tested restoration.
- [**Multi-user and external account direction**](https://dubnium.micrantha.com/docs/governance.html#multi-user-and-external-account-direction) — planned scoped user and workspace access.
- [**Runtime and deployment**](https://dubnium.micrantha.com/docs/vision.html) — operating modes, layered isolation, authenticated private connectivity and experimental virtual-appliance direction.
- [**Observability and data sovereignty**](https://dubnium.micrantha.com/docs/observability.html) — local-first operational evidence, purpose-limited telemetry, bounded remote access and operator-owned data.

The [status and direction](https://dubnium.micrantha.com/docs/status.html) page distinguishes publicly published contracts, evolving implementation and unqualified deployment or integration goals. These are not commitments to a stable distribution or managed service.

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

## Documentation and publication

The Community repository owns the public website, curated Technical Overview source and generated artifact. See [PUBLICATION_BOUNDARY.md](PUBLICATION_BOUNDARY.md) for disclosure and ownership rules and [public-site deployment](docs/public-site-deployment.md) for the sole Cloudflare deployment path, validation and rollback. Generated book changes must pass source-to-artifact parity and the independent publication guards.

## Governed-agent integration reference

The [public governed-agent integration reference](docs/governed-agent-integration.md) explains the Anthesis decision boundary, Dubnium's execution-side responsibility, the checks needed to assess bypass resistance, and the separate [public executable Anthesis trial](https://github.com/hackelia-micrantha/anthesis-community/blob/main/docs/product/try-anthesis.md). It is an implementation-safe overview, not an executable public Dubnium distribution or a copy of private operational runbooks.

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

The first [Capability Gateway contract bundle, `contract-v0.1.0-alpha.1`](https://github.com/hackelia-micrantha/dubnium-community/releases/tag/contract-v0.1.0-alpha.1), is published and independently verifiable. It is an experimental release, not a stable or accepted downstream compatibility baseline. Publication, downstream acceptance, and production qualification are separate gates; `main` remains development source rather than immutable contract identity.

Content is explicitly marked `experimental`, `v1alpha`, `v1beta`, or `stable`. Unmarked content is not a compatibility commitment. Compatibility and deprecation rules are defined in [COMPATIBILITY.md](COMPATIBILITY.md).

The current experimental slice defines a narrow Capability Gateway envelope with canonicalization, synthetic adversarial fixtures, conformance checks, and a no-effect reference. It does not include a production gateway, privileged providers, deployment implementation, supervisor, memory implementation, or host configuration.

## How to help Dubnium

Dubnium welcomes contributions and design feedback on reproducible development, secure AI and interoperability. Engineering teams can examine the architecture and conformance evidence; partners can help validate practical use cases. See the [community and commercial boundary](COMMUNITY_COMMERCIAL_BOUNDARY.md) for possible supported offerings and the limits of current maturity.

- **Contract and conformance contributors** — review specifications, validators, compatibility rules, synthetic fixtures, adversarial cases, and public reference implementations.
- **Platform, NixOS, security, and DevEx contributors** — improve reproducibility guidance, threat models, operator ergonomics, documentation, and portable integration patterns within the public boundary.
- **Design partners and adopters** — bring local/private AI, self-hosted CI, governed automation, workstation reproducibility, or bounded-execution requirements that can challenge the current architecture.
- **Hardware and infrastructure support** — GPU-capable systems, accelerators, storage, networking equipment, hosted CI/compute, or other resources useful for exercising local AI, runner isolation, builds, recovery, and conformance at broader scale.
- **Strategic collaboration** — help explore distribution, sustainability, integrations, independent implementations, and practical deployment models without turning public participation into a procurement requirement.

The public community repository is not a contribution path into private production topology, credentials, prompts, policy, operational evidence, or privileged implementation. Use [CONTRIBUTING.md](CONTRIBUTING.md) for public work and [DESIGN_PARTNER_GUIDE.md](DESIGN_PARTNER_GUIDE.md) for deeper validation conversations. Micrantha-wide partnership and co-founder interests are described in the [organization collaboration overview](https://github.com/hackelia-micrantha/.github/blob/main/profile/README.md#looking-for-collaborators).

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
