# Release integrity

Status: v1alpha
Content: normative
Canonical source: this file
Generated: no

Issue #17 activates this policy after issue #10 creates a real distributable public contract bundle. The repository MUST NOT publish or attest empty scaffolding merely to exercise release automation.

## Release source

A release is built only from:

- a protected `main` commit or approved immutable release ref;
- a tree that passed the required aggregate Contract CI check;
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

When release activation is complete, tagged distributable releases MUST include:

- deterministic archive or package outputs where practical;
- a machine-readable release manifest;
- SHA-256 checksums;
- SPDX or CycloneDX SBOM for executable/package dependencies;
- GitHub artifact provenance/attestation for consumer-verifiable archives, packages, or binaries;
- exact monorepo version, contract versions, source commit, toolchain versions, and compatibility profile;
- release notes derived from reviewed change records.

An attestation establishes build provenance under its trust model. It does not establish security, correctness, endorsement, or production suitability.

## Consumer verification

A separate job downloads the published artifact as a consumer, verifies checksums and provenance, safely extracts the archive, validates the manifest, and runs the public validation or conformance entry point without private access.

Archive extraction rejects traversal, absolute paths, symlinks, devices, sockets, collisions, unsupported file types, and resource exhaustion.

## Reproducibility

Archive ordering, timestamps, ownership, permissions, compression settings, manifest serialization, and tool versions are fixed or recorded. A local reproduction command and expected checksums accompany the release process.

## Compromise and supersession

The release process documents:

- how a compromised release is marked and no longer recommended;
- how corrected artifacts receive a new immutable version rather than silent replacement;
- how consumers identify superseding versions;
- what evidence is retained privately and publicly;
- when keys, credentials, workflows, or trusted builders require rotation.

Tags and published artifacts are treated as immutable. Mutable aliases are not production contract identity.
