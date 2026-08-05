# Dubnium public-site publication boundary

Status: stable
Content: informative
Canonical source: this file
Generated: no

`site/docs/` contains generated output from a separately reviewed public-documentation source. It is a publication artifact, not canonical protocol or schema source.

## Ownership

- The private producer owns its curated documentation source and generation process.
- `dubnium-community` owns the reviewed artifact accepted into `site/docs/` and the independent validation applied before deployment.
- Files beneath `site/docs/` must not be edited manually.

The public artifact must not require access to its producer after publication.

## Publication contract

A publication must:

1. replace only an allowlisted generated path under `site/`;
2. include `site/docs/index.html`;
3. include `site/docs/publication.json` with a public publication identifier, content digest, generator identity, schema version, and generation timestamp;
4. avoid private repository coordinates, private commit identifiers, workflow identifiers, local paths, and production cadence unless an explicit disclosure decision permits them;
5. pass the destination repository's publication validator;
6. arrive through a pull request rather than a direct push to `main`.

The destination validates publications independently. Producer-side success does not imply that an artifact is safe to publish.

## Security boundary

Generated output must not contain:

- credentials, secret material, or secret-like assignments;
- private repository or edit links;
- internal documentation or filesystem paths;
- localhost, link-local, or private-network endpoints;
- hostnames, identities, topology, trusted allowlists, or operational policy;
- source maps or metadata that disclose private source structure;
- unexpected executable files, symlinks, devices, sockets, or path traversal;
- unreviewed active content.

Validation is static and resource-bounded. CI must not execute JavaScript or other generated content from publication branches.

## Disclosure and provenance

Publication is operationally irreversible. Reverting a commit can remove content from the current branch and deployment, but cannot restore confidentiality after clones, caches, forks, mirrors, or logs have captured it.

Private provenance may be represented by an opaque publication identifier, content digest, and signed attestation. Public consumers do not need the private source repository or source commit to verify the delivered artifact.

## Rollback

The deployed site can be rolled back by reverting the corresponding public publication commit. Rebuilding from the private producer is not required for operational rollback.
