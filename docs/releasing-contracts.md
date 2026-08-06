# Verifiable contract releases

The Capability Gateway contract bundle is an experimental public artifact. Consumers must pin a release tag and verify the downloaded artifact; consuming the moving `main` branch is unsupported.

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

```sh
SOURCE_COMMIT=$(git rev-parse HEAD)
python3 scripts/build_contract_release.py --output dist --source-commit "$SOURCE_COMMIT"
python3 scripts/verify_contract_release.py dist
```

A reproducibility check builds twice from the same source commit and compares every output byte.

## Release procedure

1. Merge the reviewed release implementation and contract changes through protected `main`.
2. Confirm Repository Policy, Contract CI, and Contract Release CI pass on `main`.
3. Update `release/contract-bundle-version.txt` through a pull request when a new release is required.
4. Create an annotated or lightweight tag named `contract-v<version>` at the current `main` commit.
5. The release workflow verifies the tag/version match, rebuilds twice, runs conformance, generates attestations, and publishes a GitHub release.
6. A separate job downloads the published release, verifies the archive attestation, checks every checksum, extracts safely, verifies the embedded manifest, and reruns public conformance.

The first release must not be tagged until the protected-main rules tracked by issue #18 are active.

## Consumer policy

Consumers must pin all of:

- release tag;
- source commit recorded in the release manifest;
- archive SHA-256 from `SHA256SUMS`;
- successful GitHub artifact-attestation verification.

Private Dubnium must store these immutable values in reviewed source or lock metadata. It must not follow public `main`, a mutable branch, or an unverified download URL.

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
