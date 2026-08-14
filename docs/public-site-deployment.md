# Public site deployment

Status: experimental
Audience: maintainers

The public Dubnium website is owned by this repository and deployed from `site/**` to Cloudflare Workers Static Assets.

## Source-of-truth boundaries

| Concern | Authority |
| --- | --- |
| Landing page and public assets | `site/**` |
| Generated public guide | `site/docs/**` |
| Publication disclosure rules | `PUBLICATION_BOUNDARY.md` and `scripts/validate_publication.py` |
| Cloudflare project configuration | `wrangler.jsonc` |
| CI validation and production deployment | `.github/workflows/pages.yml` |

The workflow filename is retained for repository-policy compatibility. It no longer deploys GitHub Pages.

## Pull-request validation

Site-related pull requests run all of the following before they are eligible to merge:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/validate_publication.py
npx --yes wrangler@4.114.0 deploy --dry-run
```

The dry run validates that the checked-in Wrangler configuration can package the complete `site/**` artifact without contacting the production deployment path.

Generated-book pull requests remain more restrictive: automated publication changes must be confined to `site/docs/**`.

## Production deployment

A trusted push to `main` that changes the site or deployment inputs runs the same validation and then deploys with the pinned Cloudflare Wrangler GitHub Action.

The repository must provide these GitHub Actions secrets:

- `CLOUDFLARE_ACCOUNT_ID`
- `CLOUDFLARE_API_TOKEN`

The API token should be scoped to the Cloudflare account and Worker needed for this site. Do not use a global API key or commit credentials to the repository.

Production deployment fails closed when validation fails, credentials are absent, Wrangler deployment fails, or the action does not return a deployment URL.

## Verification

For a deployment change, verify in this order:

1. pull-request publication validation is green;
2. Wrangler dry-run is green;
3. merge to `main` completes the `Deploy public site` workflow successfully;
4. the workflow reports a Cloudflare deployment URL;
5. `/` serves the landing page;
6. `/docs/` serves the generated public guide; and
7. representative static assets and an unknown route behave according to `wrangler.jsonc`.

The deployment URL is evidence that Cloudflare accepted the deployment; it is not a substitute for checking the public routes.

## Rollback

Rollback is source-driven. Revert the offending `site/**`, validator, workflow, or Wrangler configuration change on `main` and allow the normal deployment workflow to publish the reverted state.

Do not bypass destination validation by manually uploading a different artifact. Emergency Cloudflare-side rollback may restore availability, but the repository must subsequently be reconciled so that declared source and deployed content agree.

## Security properties

- The deployment job has GitHub `contents: read` permission only.
- Cloudflare credentials are supplied only to the trusted production deployment job, not pull-request validation.
- Third-party GitHub Actions are pinned to immutable commit SHAs.
- The public deployment consumes only `site/**`; it does not fetch private implementation source.
- Private-to-public generated documentation is independently validated again in this repository before deployment.
