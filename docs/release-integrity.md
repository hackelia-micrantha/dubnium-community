# Release integrity

Status: v1alpha
Content: normative
Canonical source: this file
Generated: no

The first real Capability Gateway contract bundle was released as [`contract-v0.1.0-alpha.1`](https://github.com/hackelia-micrantha/dubnium-community/releases/tag/contract-v0.1.0-alpha.1) from protected `main@e6eeec4df704679d1b728701db87f6410272f046`. Immutable tag controls, reproducible release generation, attestations, published-artifact checksums and the independent GitHub consumer job were verified by [release workflow #38492311515](https://github.com/hackelia-micrantha/dubnium-community/actions/runs/38492311515). Issue #17 remains open for the private-source provenance disclosure decision and private Dubnium's exact released-asset/digest consumption qualification, not because publication is missing.

The repository MUST NOT publish or attest empty scaffolding merely to exercise release automation. The presence of release scripts and green pull-request CI does not establish an active consumer release.

## Activation state

The repository currently provides:

- deterministic archive, manifest, checksum, and SPDX generation;
- bounded artifact verification and safe extraction;
- byte-for-byte reproducibility checks;
- a separate workflow-artifact consumer job;
- a tag-triggered publication, attestation, and post-publication verification workflow;
- a repository-owned tool for applying and checking `main` branch protection.

Before **each new** release tag is created, maintainers MUST verify that:

- `scripts/apply_repository_policy.py check` succeeds against active GitHub settings;
- only squash merges are enabled and required checks protect `main`;
- force pushes and branch deletion are disabled;
- creation, update, and deletion of `contract-v*` tags are restricted by a GitHub tag ruleset or an equivalent audited administrative control;
- the release tag points at the current protected `main` commit and matches `release/contract-bundle-version.txt`.

## Release source

A release is built only from:

- a protected `main` commit or approved immutable release ref;
- a tree that passed the required aggregate Contract CI and Contract Release CI checks;
- reviewed release workflow and manifest changes;
- canonical public source with no private repository dependency.

Pull-request jobs have no release, package-write, deployment, or OIDC permissions.

## Release bundle

The selected bundle contains only reviewed public assets that consumers verify, such as:

- normative specifications;
- canonical schemas and API bindings;
- conformance fixtures and entry points;
- justified public packages or no-effect references;
- license, notice, compatibility, and release metadata.

It excludes the production Gateway, supervisor, memory implementation, policy, privileged providers, deployment workers, host configuration, private provenance, and operator data.

## Required artifacts

Tagged distributable releases MUST include:

- deterministic archive or package outputs where practical;
- a machine-readable release manifest;
- SHA-256 checksums;
- SPDX or CycloneDX SBOM for executable/package dependencies;
- GitHub artifact provenance/attestation for consumer-verifiable archives, packages, or binaries;
- exact monorepo version, contract versions, source commit, toolchain versions, and compatibility profile;
- release notes derived from reviewed change records.

The first public release provides evidence of these outputs. Each subsequent version requires its own exact-tag build, published attestation and downloaded-artifact consumer verification. Version identifiers containing a SemVer prerelease component (such as `-alpha.1`) must also be classified as GitHub prereleases; stable version identifiers must not be classified as prereleases.

An attestation establishes build provenance under its trust model. It does not establish security, correctness, endorsement, or production suitability.

## Consumer verification

A separate job downloads the published artifact as a consumer, verifies checksums and provenance, safely extracts the archive, validates the manifest, and runs the public validation or conformance entry point without private access.

Archive extraction rejects traversal, absolute paths, symlinks, devices, sockets, collisions, unsupported file types, and resource exhaustion.

Consumers MUST NOT treat public `main`, a workflow artifact, or an unverified release asset as production contract identity.

## Reproducibility

Archive ordering, timestamps, ownership, permissions, compression settings, manifest serialization, and tool versions are fixed or recorded. The local reproduction and verification commands are documented in [releasing-contracts.md](releasing-contracts.md).

## Compromise and supersession

The release process documents:

- how a compromised release is marked and no longer recommended;
- how corrected artifacts receive a new immutable version rather than silent replacement;
- how consumers identify superseding versions;
- what evidence is retained privately and publicly;
- when keys, credentials, workflows, or trusted builders require rotation.

Tags and published artifacts are treated as immutable. Mutable aliases are not production contract identity.
