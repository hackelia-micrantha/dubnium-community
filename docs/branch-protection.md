# Protected-main policy

Status: stable
Content: normative
Canonical source: this file
Generated: no

GitHub repository settings, not committed workflow files, enforce branch protection. Issue #18 tracks applying and verifying this desired policy.

## Required `main` controls

- changes enter through pull requests;
- `Contract CI / contract-gate`, `Contract Release CI / consume-release`, and `Repository Policy` are required and current;
- force pushes and branch deletion are disabled;
- strict status checks require branches to be current before merge;
- squash merge is the only enabled merge method;
- linear history and conversation resolution are required;
- stale approvals are dismissed after updates;
- CODEOWNERS review becomes required when another qualified maintainer is available;
- workflow-file and policy changes receive explicit maintainer review;
- administrators are subject to the same protected-main controls.

## Current single-maintainer compensation

The repository must not require an impossible approval while only one qualified active maintainer exists. The configured approving-review count is therefore zero until another maintainer is available. A merge still records:

- green required CI;
- a signed-off squash commit;
- explicit compatibility and security classification;
- provenance and licensing confirmation;
- publication/IP review where applicable;
- a documented self-review of the complete diff.

This is a temporary governance constraint, not equivalent to independent review.

## Administrative application

The repository-owned tool emits, applies, and verifies the exact REST policy:

```bash
python3 scripts/apply_repository_policy.py plan
GH_TOKEN="$(gh auth token)" python3 scripts/apply_repository_policy.py apply
GH_TOKEN="$(gh auth token)" python3 scripts/apply_repository_policy.py check
```

The token requires repository administration permission. The tool is idempotent, uses the GitHub REST API directly, and fails when active settings differ from this policy.

The application sequence updates repository merge methods first, then replaces `main` branch protection, then reads both resources back and compares their normalized active state with the expected policy. Do not create a contract release tag until `check` succeeds.

## Verification record

After application, record the successful `check` result and the active branch response on issue #18. Committed policy and passing unit tests do not imply that GitHub settings are active.
