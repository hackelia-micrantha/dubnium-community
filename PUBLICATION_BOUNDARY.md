# Public Website and Book Publication Boundary

Status: experimental
Content: normative
Canonical source: this file
Generated: no
Reviewed: 2026-08-13

## Authority

This repository is authoritative for the complete Dubnium public website.

- `site/index.html` and adjacent assets are maintained directly here.
- `site/docs/**` is a generated public mdBook artifact.
- `.github/workflows/pages.yml` is the only supported repository-driven public deployment path.
- `wrangler.jsonc` defines the Cloudflare Workers Static Assets deployment for `site/**`.
- `scripts/validate_publication.py` independently validates the deployed artifact before any production deployment runs.

The workflow filename is retained for repository-policy compatibility, but the deployment target is Cloudflare Workers, not GitHub Pages. GitHub Pages is not part of the supported publication architecture.

No private implementation repository is a public website host or public documentation authority.

## Deployment contract

Every pull request that changes the public site, publication validator, Wrangler configuration, or deployment workflow must pass:

1. the publication-validator unit tests;
2. destination-side publication validation; and
3. a Wrangler `deploy --dry-run` against the checked-in static-assets configuration.

Production deployment runs only for trusted `main` pushes or an explicit workflow dispatch. It uses the repository secrets `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN`. Those credentials must be scoped to the Cloudflare account and Worker required for this public site and must never be committed to the repository or copied into generated documentation.

A successful deployment must return a Cloudflare deployment URL. Missing credentials, invalid configuration, failed publication validation, or a missing deployment result fails closed.

Cloudflare receives only the already-reviewed contents of `site/**`; the deployment workflow does not read from or fetch any private implementation repository.

## Generated-book contract

A generated-book pull request may change only `site/docs/**`. It must pass repository tests and destination-side publication validation before merge or deployment.

The producer must construct the book from an explicit reviewed source-file allowlist. Book navigation alone is not an acceptable disclosure boundary because a documentation generator may emit source pages that are not linked from its table of contents. Unlinked or otherwise unreviewed source files must fail closed before generation.

The book is an overview. It may describe:

- project purpose, principles, and directional deployment forms;
- conceptual components, source-of-truth boundaries, and trust boundaries;
- reproducible-development and supply-chain concepts;
- local, organizational, and personal observability at a conceptual level;
- AI and automation boundaries without private routing or prompt behavior;
- observable public contracts and compatibility rules;
- governance and safety posture;
- bounded public status and roadmap themes;
- community contribution and release processes.

It must not disclose:

- production topology, services, hosts, networks, ports, or resource assignments;
- prompts, routing heuristics, retry or fallback behavior;
- policy thresholds, operational allowlists, approvals, or trusted identities;
- private data schemas, ranking, retention, retrieval, or stored content;
- privileged providers, deployment workers, recovery procedures, or credentials;
- real logs, incidents, traces, evidence, or operational measurements;
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

The source-side publisher and this destination repository both validate the artifact. Destination validation is authoritative for deployment and must not trust source-side checks alone.

The landing page and generated book have separate update paths:

- hand-authored website changes may modify `site/index.html` and site assets through normal review;
- generated-book publication changes are confined to `site/docs/**`;
- a generated-book publication cannot modify the landing page, workflow, validator, Wrangler configuration, or repository policy in the same automated change.

A regenerated book replaces the complete `site/docs/**` artifact. Stale generated content must not survive merely because a source page was removed.

## Failure posture

Publication fails closed on unexpected paths, file types, symlinks, excessive size, malformed metadata, private metadata fields, private repository references, internal paths, private addresses, absolute home paths, secret-like assignments, executable links to local endpoints, invalid Cloudflare deployment configuration, or missing deployment credentials.

Uncertainty about ownership, licensing, patents, trade secrets, security exposure, or provenance is resolved by keeping material private until review is complete.
