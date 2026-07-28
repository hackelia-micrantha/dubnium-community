# Dubnium public book publication boundary

`site/docs/` contains generated output from the curated public documentation source in `ryjen/dubnium`.

## Ownership

- `ryjen/dubnium` is authoritative for public documentation source under `docs/external/`.
- `hackelia-micrantha/dubnium-community` is authoritative for the generated artifact that is reviewed and deployed publicly.
- Files beneath `site/docs/` must not be edited manually.

## Publication contract

A publication must:

1. replace only `site/docs/`;
2. include `site/docs/index.html`;
3. include `site/docs/publication.json` with source commit and generator provenance;
4. pass the destination repository's publication validator;
5. arrive through a pull request rather than a direct push to `main`.

The destination repository validates publications independently from the private producer. Producer-side success does not imply that an artifact is safe to publish.

## Security boundary

Generated output must not contain:

- private repository or edit links;
- internal documentation paths;
- local filesystem paths;
- localhost or private-network endpoints;
- secret-like assignments;
- unexpected executable files or symlinks.

The validator performs static inspection only. CI must not execute JavaScript or other generated content from publication branches.

## Rollback

The published book can be rolled back by reverting the corresponding publication commit in this repository. Rebuilding from the private producer is not required for rollback.
