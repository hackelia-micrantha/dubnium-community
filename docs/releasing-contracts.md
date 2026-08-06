# Verifiable contract releases

The Capability Gateway contract bundle is an experimental public artifact. Consumers must pin a published release tag and verify the downloaded artifact; consuming the moving `main` branch is unsupported.

## Current activation status

The bundle builder, verifier, release CI, tag-triggered publication workflow, and repository-policy application tool are implemented. No `contract-v*` tag is yet an accepted consumer baseline.

Issue #17 remains open until:

1. active `main` protection and squash-only merge settings are verified;
2. immutable `contract-v*` tag controls are established;
3. the first tag is published from the current protected `main` commit;
4. the published checksums and GitHub artifact attestations verify;
5. the post-publication consumer job completes successfully.

Do not infer release readiness from the presence of scripts, green pull-request CI, or a version file alone.

## Bundle contents

The deterministic archive contains reviewed public assets from:

- `api/`
- `changes/`
- `conformance/`
- `examples/`
- `schemas/`
- `spec/`
- repository license, notice, and security policy files when present

It deliberately excludes the generated website, repository automation, private runtime code, production configuration, credentials, operator data, logs, incidents, benchmarks, and private source coordinates.

Each release includes:

- a deterministic `.tar.gz` contract archive;
- a machine-readable release manifest with source commit and per-file SHA-256 digests;
- an SPDX 2.3 SBOM;
- `SHA256SUMS`;
- GitHub artifact attestations for the published files.

Attestations establish build provenance. They do not certify security, correctness, compatibility, or authorization.

## Build and verify locally

Run from the root of `hackelia-micrantha/dubnium-community`:

```sh
SOURCE_COMMIT=$(git rev-parse HEAD)
python3 scripts/build_contract_release.py --output dist --source-commit "$SOURCE_COMMIT"
python3 scripts/verify_contract_release.py dist
```

A reproducibility check builds twice from the same source commit and compares every output byte.

## Verify repository controls

The repository-owned policy tool is `scripts/apply_repository_policy.py`. It manages repository merge methods and `main` branch protection; it does not create tag rulesets.

```sh
python3 scripts/apply_repository_policy.py plan
GH_TOKEN="$(gh auth token)" python3 scripts/apply_repository_policy.py apply
GH_TOKEN="$(gh auth token)" python3 scripts/apply_repository_policy.py check
```

If the script is missing locally, confirm that the checkout is this repository, switch to `main`, and pull the latest changes before proceeding.

Before tagging, an administrator must also apply and verify immutable tag protection for `contract-v*` through GitHub repository rulesets or an equivalent audited control. The release process must not rely on a tag that can be silently moved or deleted.

## Release procedure

1. Merge reviewed release implementation and contract changes through protected `main`.
2. Confirm Repository Policy, Contract CI, and Contract Release CI pass on `main`.
3. Run `scripts/apply_repository_policy.py check` and retain the successful read-back evidence.
4. Confirm the `contract-v*` tag ruleset prevents unauthorized creation, update, and deletion.
5. Update `release/contract-bundle-version.txt` through a pull request when a new release is required.
6. Create an annotated or lightweight tag named `contract-v<version>` at the current `main` commit.
7. The release workflow verifies the tag/version match, rebuilds twice, runs conformance, generates attestations, and publishes a GitHub release.
8. A separate job downloads the published release, verifies the archive attestation, checks every checksum, extracts safely, verifies the embedded manifest, and reruns public conformance.
9. Record the release URL, source commit, artifact digests, attestation result, and consumer-job result on issue #17.

The first planned version is read from `release/contract-bundle-version.txt`; documentation must not override that file as the release authority.

## Consumer policy

Consumers must pin all of:

- release tag;
- source commit recorded in the release manifest;
- archive SHA-256 from `SHA256SUMS`;
- successful GitHub artifact-attestation verification.

Private or external consumers must store these immutable values in reviewed source or lock metadata. They must not follow public `main`, a mutable branch, a workflow artifact, or an unverified download URL.

## Supersession and revocation

A published artifact is immutable. Never replace assets attached to an existing tag.

For an ordinary correction:

1. publish a new version;
2. mark the earlier release as superseded in its release notes;
3. update consumer pins through normal review.

For a compromised release:

1. stop new consumption immediately;
2. record the affected tag, artifact digest, reason, and detection time in a public security advisory when disclosure is safe;
3. revoke or invalidate consumer policy for the affected digest;
4. publish a corrected version from reviewed source;
5. preserve the original release record unless removal is required to prevent active harm;
6. rotate any exposed credential outside this repository—credentials must never be present in the bundle.

Deletion or a changed release note cannot restore secrecy after publication.
