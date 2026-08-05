# Public roadmap

Status: experimental
Content: informative
Canonical source: this file
Generated: no

This roadmap describes intended public work. It is not a compatibility promise or commitment to publish private implementation.

## Phase 0 — repository foundation

- public/private product boundary;
- Apache-2.0 licensing and contribution provenance;
- governance, security, compatibility, trademark, and publication policies;
- initial monorepo layout and dependency rules;
- lightweight repository-policy CI.

Tracked by issue #12.

## Phase 1 — CI and release integrity

- isolated specification and conformance CI;
- action pinning and minimal permissions;
- schema/example/generated-output synchronization;
- parser resource and adversarial tests;
- release checksums, SBOMs, and attestations;
- branch protection or repository rulesets.

Tracked by issue #14.

## Phase 2 — first experimental contract slice

- Capability Gateway request, submission, status, authorized-manifest, and error contracts;
- canonical JSON and domain-separated digest vectors;
- positive, negative, and adversarial fixtures;
- implementation-neutral conformance tests;
- no-effect client/provider reference.

Tracked by issue #10.

## Phase 3 — private consumer integration

- immutable public release consumption;
- artifact digest and provenance verification;
- private adapters without editable schema copies;
- public conformance exercised against a private implementation boundary.

Tracked in the private Dubnium repository.

## Reassessment after one release cycle

After real maintenance and consumer evidence exists, maintainers may consider:

- thin public validation or conformance commands from `dubctl`;
- a stabilized LLM gateway compatibility profile;
- additional language bindings justified by actual consumers.

The following remain deferred by default:

- supervisor or orchestration implementation;
- production policy and approvals;
- memory implementation or stored data;
- scheduler ownership and exact state;
- deployment providers and privileged workers;
- NixOS host topology and runner configuration;
- broad multi-language SDK matrices;
- splitting this monorepo into multiple repositories.
