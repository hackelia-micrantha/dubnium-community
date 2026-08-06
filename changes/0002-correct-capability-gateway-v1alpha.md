# Correct Capability Gateway v1alpha standards and digest behavior

Status: v1alpha
Content: informative
Canonical source: this file
Generated: no
Compatibility: breaking
Contracts:

- `spec/capability-gateway-v1.md`
- `spec/capability-namespaces.md`
- `schemas/v1/common.schema.json`
- `api/capability-gateway/v1/openapi.json`
- `conformance/capability_gateway_v1.py`
- `conformance/gateway_envelopes_v1.py`

## Behavior

Corrects the first merged Capability Gateway draft while preserving its canonical envelope paths and field shapes.

- replaces custom recursive NFC normalization and Unicode code-point key sorting with RFC 8785 JCS;
- preserves caller strings and keys exactly and rejects lone surrogates;
- replaces undomained SHA-256 with fixed request and payload domain separation;
- makes portable error retryability explicit;
- adds a bounded request-ID idempotency/conflict reference;
- adds capability namespace governance and the synthetic `deployment.apply` fixture;
- adds an OpenAPI 3.1.2 HTTP message binding with RFC 9457 Problem Details;
- adds Unicode ordering, no-normalization, request-ID conflict, expiry, widening, and payload-substitution vectors.

## Compatibility

This is intentionally breaking within the experimental/pre-1.0 lifecycle.

Digests produced by the superseded NFC/raw-hash draft are invalid under corrected v1alpha. Implementations MUST recompute request and payload digests and MUST NOT treat the old values as aliases.

The request, submission, status, manifest, provider-operation, capability, target, constraint, and evidence field shapes remain stable unless directly affected by the correction above.

## Security and authority

- actor identity remains transport-derived and outside caller-controlled JSON;
- public schemas and names do not confer provider admission or authorization;
- manifests continue to bind exact request, actor, capability, target, payload, decision, constraints, evidence requirements, and expiry;
- unknown fields and unsupported versions fail closed;
- no silent Unicode normalization is permitted;
- request and payload hashes cannot be confused across object types because their digest domains differ;
- identical request ID and digest is idempotent; the same ID with a different digest fails closed;
- retryability never implies authorization;
- remote schema resolution and remote conformance remain disabled.

## Evidence

- fixed request and payload digest vectors;
- RFC 8785 Unicode ordering vector;
- explicit canonically equivalent but byte-distinct string test;
- positive manifest and envelope validation;
- corrected single-fault expiry, constraint-widening, and payload-substitution manifests;
- request-ID retry/conflict and bounded-state tests;
- synthetic non-executable `deployment.apply` request;
- OpenAPI/static-reference validation;
- aggregate Contract CI.

## Private boundary

This correction does not publish production Gateway services, sockets, actor mappings, persistent state, policy adapters, provider routing, Anthesis implementation, deployment constraints or providers, privileged workers, recovery behavior, Supervisor or memory intelligence, NixOS topology, credentials, incidents, logs, traces, benchmarks, operational evidence, private source, or private Git history.
