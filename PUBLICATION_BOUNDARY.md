# Public Website and Technical Overview Publication Boundary

Status: experimental
Content: normative
Canonical source: this file
Generated: no
Reviewed: 2026-08-13

## Authority

This repository is authoritative for the complete Dubnium public website.

- `site/index.html` and adjacent assets are maintained directly here.
- `site/docs/**` is the generated Dubnium Technical Overview artifact.
- `scripts/validate_publication.py` independently validates the public artifact.
- `.github/workflows/pages.yml` validates site changes in GitHub Actions, including a Wrangler deployment dry run.
- `wrangler.jsonc` defines the Cloudflare Workers Static Assets project and `site/**` asset root.
- Cloudflare Workers Builds Git integration is the sole production and preview deployment authority.

The workflow filename is retained for repository-policy compatibility. It no longer deploys GitHub Pages, and GitHub Actions does not hold a second set of Cloudflare deployment credentials.

No private implementation repository is a public website host or public documentation authority.

Reader-facing documentation uses **Technical Overview** rather than “Public Guide.” “Public” remains a repository-visibility and publication-boundary term.

## Deployment contract

Every pull request that changes the public site, publication validator, Wrangler configuration, or site-validation workflow must pass:

1. the publication-validator unit tests;
2. destination-side publication validation; and
3. a Wrangler `deploy --dry-run` against the checked-in static-assets configuration.

Cloudflare's Git integration independently builds repository branches and reports deployment status back to GitHub. Non-production branches receive preview deployments; the configured production branch deploys the merged site. A Cloudflare preview is useful review evidence, but it does not replace the destination-side publication guard.

There is exactly one deployment authority. GitHub Actions validates; Cloudflare Workers Builds deploys. Do not add a second `wrangler deploy` path to GitHub Actions while the Git integration is active.

Cloudflare receives only the already-reviewed public repository content. It does not read from or fetch any private implementation repository.

## Landing page versus Technical Overview

The two surfaces have different jobs:

| Surface | Purpose | Detail level |
| --- | --- | --- |
| Landing page | Define the product, show component maturity, and route readers to evidence | Concise; no runbook-like command blocks or detailed state flows |
| Technical Overview | Explain components, operator-tool boundaries, stable runtime semantics, configuration ownership, architecture, and published contracts | More detailed, but implementation-safe |
| Contracts / conformance | Specify deliberately published interoperable behavior exactly | Exact where intentionally published |

The landing page must not grow into a substitute for technical documentation. Stable explanatory depth belongs in the generated Technical Overview when it passes disclosure review.

## Generated Technical Overview contract

A generated-documentation pull request may change only `site/docs/**`. It must pass repository tests and destination-side publication validation before merge or deployment.

The producer must construct the Technical Overview from an explicit reviewed source-file allowlist. Book navigation alone is not an acceptable disclosure boundary because a documentation generator may emit source pages that are not linked from its table of contents. Unlinked or otherwise unreviewed source files must fail closed before generation.

The governing rule is:

> Publish what the system promises and what an integrator or operator can observe; keep private how a particular deployment enforces it.

The Technical Overview may describe:

- project purpose, principles, and directional deployment forms;
- stable component names, responsibilities, maturity, and intentional boundaries;
- stable operator-tool names, responsibilities, and representative command families;
- stable runtime-mode identifiers and human-facing semantics;
- conceptual desired/observed state models, reconciliation loops, and invariants;
- conceptual transition-guard categories without exact identifiers or thresholds;
- conceptual writable-configuration ownership layers and lifecycle;
- reproducible-development and supply-chain concepts;
- local, organizational, and personal observability at a conceptual level;
- AI and automation boundaries without private routing or prompt behavior;
- observable contracts and compatibility rules;
- governance and safety posture;
- bounded status and roadmap themes;
- community contribution and release processes.

It must not disclose:

- real production topology, services, hosts, networks, ports/endpoints, service-unit wiring, or resource assignments;
- exact transition thresholds, guard names, implementation allowlists, bypass mechanics, or machine-specific exceptions;
- prompts, model/provider routing heuristics, retry or fallback behavior;
- production policy internals, operational approvals, or trusted identities;
- private data schemas, ranking, retention, retrieval, consolidation, or stored content unless separately published as a reviewed contract;
- privileged providers, deployment workers, recovery/migration procedures, or credentials;
- private scheduler state, runner mappings, fleet authorization internals, or privileged worker mechanics;
- real logs, incidents, traces, evidence, operational measurements, secrets, or operator/customer data;
- private repository names, source commits, branches, paths, issues, pull requests, workflow runs, jobs, or runner identities.

## Public provenance schema

`site/docs/publication.json` uses schema version 2 and contains only:

```json
{
  "schema_version": 2,
  "publication_id": "opaque-publication-id",
  "content_digest": "sha256:<digest>",
  "generator": "mdbook <version>; mdbook-mermaid <version>",
  "generated_at": "<UTC RFC 3339 timestamp>"
}
```

The publication identifier is opaque and derived from public content. The digest covers the generated public artifact, excluding `publication.json` itself.

Private provenance may exist in private evidence storage, but it must not appear in public files, commits, pull-request text, deployment metadata, or links.

## Source and destination separation

The source-side publisher and this destination repository both validate the artifact. Destination validation is authoritative for publication and must not trust source-side checks alone.

The landing page and generated Technical Overview have separate update paths:

- hand-authored website changes may modify `site/index.html` and site assets through normal review;
- generated documentation changes are confined to `site/docs/**`;
- a generated publication cannot modify the landing page, workflow, validator, Wrangler configuration, or repository policy in the same automated change.

A regenerated Technical Overview replaces the complete `site/docs/**` artifact. Stale generated content must not survive merely because a source page was removed.

## Failure posture

Publication fails closed on unexpected paths, file types, symlinks, excessive size, malformed metadata, private metadata fields, private repository references, internal paths, private addresses, absolute home paths, secret-like assignments, executable links to local endpoints, or invalid Cloudflare deployment configuration.

Deployment health is tracked separately: a failed Cloudflare preview or production build is a deployment failure even when repository validation is green. A successful Cloudflare build is not permission to weaken the publication guard.

Uncertainty about ownership, licensing, patents, trade secrets, security exposure, or provenance is resolved by keeping material private until review is complete.
