# Public site deployment

Status: experimental
Audience: maintainers

The public Dubnium website is owned by this repository and deployed from `site/**` to Cloudflare Workers Static Assets through Cloudflare Workers Builds Git integration.

## Source-of-truth boundaries

| Concern | Authority |
| --- | --- |
| Landing page and public assets | `site/**` |
| Generated public guide | `site/docs/**` |
| Publication disclosure rules | `PUBLICATION_BOUNDARY.md` and `scripts/validate_publication.py` |
| Cloudflare project configuration | `wrangler.jsonc` |
| GitHub-side validation | `.github/workflows/pages.yml` |
| Preview and production deployment | Cloudflare Workers Builds Git integration |

The GitHub workflow filename is retained for repository-policy compatibility. It validates the public artifact but does not deploy GitHub Pages or perform a second Cloudflare production upload.

## Pull-request validation

Site-related pull requests run all of the following before they are eligible to merge:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/validate_publication.py
npx --yes wrangler@4.114.0 deploy --dry-run
```

The dry run validates that the checked-in Wrangler configuration can package the complete `site/**` artifact without contacting the production deployment path.

Generated-book pull requests remain more restrictive: automated publication changes must be confined to `site/docs/**`.

Cloudflare independently builds non-production branches and reports deployment status and preview URLs back to GitHub. A preview proves that the connected Cloudflare project can build the branch, but it does not replace the repository publication guard.

## Production deployment

Cloudflare Workers Builds is the sole deployment authority. The connected Worker is named `dubnium`, matching `wrangler.jsonc`, and the production branch is expected to be `main`.

Cloudflare's build configuration should use the repository root and the checked-in Wrangler configuration. For this static site, no separate application build step is required; the deploy command can use the Workers Builds default `npx wrangler deploy` behavior.

Do not add a second `wrangler deploy` step to GitHub Actions while Workers Builds is connected. Two deploy authorities create ordering races, duplicate credentials, and ambiguous rollback/evidence semantics.

## Verification

For a site or deployment change, verify in this order:

1. GitHub publication validation is green;
2. Wrangler dry-run is green;
3. the Cloudflare PR comment/check reports a successful preview deployment;
4. the preview root serves the refreshed landing page;
5. the preview `/docs/` route serves the generated public guide;
6. merge to `main` produces a successful Cloudflare production build/deployment; and
7. the production `/` and `/docs/` routes serve the merged revision.

A successful preview demonstrates branch deployment health. Production remains separately verified after merge because branch previews are uploaded without replacing the active production deployment.

## Rollback

Rollback is source-driven. Revert the offending `site/**`, validator, workflow, or Wrangler configuration change on `main` and allow Workers Builds to publish the reverted revision.

Cloudflare version rollback may restore availability faster during an incident, but the repository must subsequently be reconciled so that declared source and the active deployment agree.

Do not bypass destination validation by manually uploading a different long-lived artifact.

## Security properties

- GitHub site validation runs with `contents: read` permission only.
- GitHub Actions does not require Cloudflare deployment credentials for this site.
- Cloudflare deployment authority is scoped to its connected Git repository and Worker build configuration.
- Third-party GitHub Actions remain pinned to immutable commit SHAs.
- The public deployment consumes only the public repository; it does not fetch private implementation source.
- Private-to-public generated documentation is independently validated again in this repository before deployment.
