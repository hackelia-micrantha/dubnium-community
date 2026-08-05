# Contract CI trust boundary

Status: stable
Content: normative
Canonical source: this file
Generated: no

## Aggregate check

The workflow `.github/workflows/contract-ci.yml` runs on every pull request and every push to `main`. Its stable aggregate job is:

```text
Contract CI / contract-gate
```

Repository protection should require this aggregate job rather than path-filtered implementation jobs.

## Public pull-request model

Pull-request content is untrusted. Required CI:

- uses GitHub-hosted runners only;
- uses top-level read-only permissions;
- has no OIDC, release, package-write, deployment, or repository-write permissions;
- never executes `pull_request_target` content;
- pins external actions by full immutable commit SHA;
- disables persisted checkout credentials;
- has explicit timeouts and per-ref concurrency cancellation;
- does not require private repositories, services, credentials, endpoints, or operator configuration;
- does not execute generated-site JavaScript or fixture-provided shell commands;
- does not target remote conformance endpoints by default.

The workflow-policy validator enforces the mechanically checkable parts of this model across every committed workflow.

## Jobs

### `classify`

Classifies changed paths as contract, implementation, site, policy, or build-system work. It always runs so path filtering cannot suppress the aggregate check.

### `policy-and-workflows`

Validates required repository policy, content markers, dependency boundaries, private-coordinate leakage, action pinning, runner selection, checkout credentials, permissions, and timeouts.

### `contract-static`

Validates the bundled contract tree without network access or third-party parsers. It checks JSON byte and structure bounds, duplicate keys, non-finite numbers, schema dialect and identifiers, local references, traversal, unresolved references, cycles, OpenAPI JSON version, normative markers, BCP 14 requirements, examples, and change records.

### `python-tests`

Runs all validator unit tests with bytecode output disabled.

### `contract-gate`

Fails unless all required jobs succeed. Optional future jobs may be accepted as `skipped` only when their documented event or language prerequisite does not apply.

## Dependency review

Pull requests run GitHub's dependency-review action at an immutable revision. Dependency update automation opens reviewable pull requests and never auto-merges.

New package ecosystems require:

- committed lockfiles where the ecosystem supports them;
- license and vulnerability review;
- third-party notice updates;
- exact dependency purpose and removal criteria;
- CodeQL or an equivalent source scanner when the added language and repository scale justify it.

## Local reproduction

```text
python3 scripts/classify_changes.py --stdin
python3 scripts/check_repository_policy.py
python3 scripts/check_workflow_security.py
python3 scripts/check_contract_tree.py
python3 -m unittest discover -s tests -v
```

For change-record enforcement, pipe the changed path list to:

```text
git diff --name-only BASE...HEAD | python3 scripts/check_contract_tree.py --changed-paths-stdin
```

## Diagnostics

CI output is bounded and avoids raw environment dumps, credentials, private paths, and unrestricted uploaded diagnostics. Failed checks should report repository-relative files and reproducible local commands.
