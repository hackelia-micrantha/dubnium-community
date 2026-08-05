# Governance

Status: stable
Content: normative
Canonical source: this file
Generated: no

## Project model

Dubnium Community is a maintainer-led public interoperability project. It is not a standards organization and does not govern private Dubnium product implementation.

## Authority

Maintainers are responsible for:

- repository administration and releases;
- accepting, rejecting, or revising public contracts;
- stability and compatibility classification;
- security and publication decisions;
- licensing, provenance, trademark, and attribution review;
- defining canonical source and generated-artifact relationships.

Anthesis maintainers retain authority over Anthesis-owned governance decision and approval semantics. Dubnium contracts may reference those semantics but cannot redefine them unilaterally.

Private Dubnium maintainers retain authority over production runtime, policy, memory, privileged providers, deployment, host configuration, and operational data. Public maintainers decide only what this repository publishes and claims.

## Decision process

Routine maintenance uses pull-request review. A change requires an issue and explicit maintainer decision when it:

- creates or changes a normative contract;
- changes stability, compatibility, licensing, security, publication, or trademark policy;
- introduces a package, executable reference, release artifact, or external dependency;
- imports material from private or third-party sources;
- claims official compatibility or certification.

Maintainers should prefer narrow, reversible repository changes and experimental contract status until conformance evidence and real consumers justify stronger commitments.

## Conflicts and recusal

Reviewers should disclose material employment, financial, contractual, authorship, or competitive interests. A maintainer should recuse from the final decision when a conflict could reasonably undermine trust and another qualified maintainer is available.

## Appeals

A contributor may request reconsideration with new technical, compatibility, security, provenance, or licensing evidence. Repetition without new evidence does not require reopening a decision.

## Maintainer changes

Maintainers may be added after sustained, trustworthy contribution and demonstrated understanding of the public/private, IP, security, and compatibility boundaries. Access may be removed for inactivity, compromised credentials, repeated policy violations, or loss of organizational authorization.

## Releases

The monorepo uses one coordinated version initially. A release requires passing repository policy checks, required contract/conformance checks, review of generated artifacts, and a maintainer-approved release record. Independent package versioning requires a separate governance decision based on demonstrated consumer or cadence need.
