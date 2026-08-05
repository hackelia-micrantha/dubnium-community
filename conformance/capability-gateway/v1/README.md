# Capability Gateway v1 conformance

Status: experimental
Content: informative
Canonical source: this file
Generated: no

This directory contains language-neutral vectors and a zero-dependency Python conformance runner for the experimental Capability Gateway v1 contract.

Run from the repository root:

```text
python3 conformance/capability-gateway/v1/run.py
```

The runner validates:

- strict UTF-8 and pre-parse body limits;
- duplicate object member rejection;
- unknown-field and actor-spoof rejection;
- exact timestamp, identifier, capability, and payload rules;
- RFC 8785 canonical bytes within the restricted v1 value domain;
- the domain-separated SHA-256 request digest;
- immutable manifest digest, expiry, and narrowing checks;
- request-ID idempotency and conflict behavior;
- deterministic `example.echo` execution;
- bounded retained mock state.

The runner uses no network, credentials, Anthesis service, systemd, NixOS, private repository, remote endpoint, or privileged effect. Remote conformance targets are intentionally unsupported in v1.

Fixtures beneath `positive/`, `negative/`, and `synthetic/` are public, fictional test data. The `deployment.apply` fixture demonstrates capability naming and typed request shape only; it is not a production deployment contract or provider.

A passing result is specific to the bundled experimental contract and vectors. It does not imply security review, production suitability, endorsement, or certification.
