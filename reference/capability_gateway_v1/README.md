# Capability Gateway v1 no-effect reference

Status: experimental
Content: informative
Canonical source: this file
Generated: no

This directory contains a zero-dependency Python reference for the public Capability Gateway v1 contract.

It demonstrates:

- raw-byte limits before JSON parsing;
- duplicate-key rejection;
- restricted RFC 8785 JCS canonicalization;
- domain-separated request digests;
- exact request and timestamp validation;
- transport-supplied actor identity;
- immutable manifest verification;
- `example.echo` constraint narrowing;
- request-ID idempotency and conflict behavior;
- bounded in-memory state.

It deliberately provides no HTTP listener, Unix socket, authentication, policy engine, approval workflow, persistent state, dynamic provider loading, filesystem access, network access, process execution, repository access, host control, credentials, or privileged effect.

Run the bundled language-neutral fixtures through:

```text
python3 conformance/capability-gateway/v1/run.py
```

Passing the reference conformance suite does not imply production suitability, security review, endorsement, or certification.
