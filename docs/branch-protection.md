# Protected-main policy

Status: stable
Content: normative
Canonical source: this file
Generated: no

GitHub repository settings, not committed workflow files, enforce branch protection. Issue #18 tracks applying this desired policy.

## Required `main` controls

- changes enter through pull requests;
- `Contract CI / contract-gate` is required and current;
- force pushes and branch deletion are disabled;
- squash merge is the selected default history policy;
- conversations are resolved before merge;
- approvals are dismissed after material updates to normative contracts, schemas, security, licensing, release workflows, or publication infrastructure;
- CODEOWNERS review is required when another qualified maintainer is available;
- workflow-file and ruleset changes receive explicit maintainer review;
- administrator bypass is limited, intentional, and auditable.

## Current single-maintainer compensation

The repository must not require an impossible second approval while only one qualified active maintainer exists. Until a second maintainer is available, a merge records:

- green required CI;
- a signed-off squash commit;
- explicit compatibility and security classification;
- provenance and licensing confirmation;
- publication/IP review where applicable;
- a documented self-review of the complete diff.

This is a temporary governance constraint, not equivalent to independent review.

## Verification

After repository settings are applied, maintainers compare the active ruleset or branch-protection response against this file and record material differences in issue #18.

Committed policy does not imply that GitHub settings are active. The repository currently requires explicit administrative application and verification.
