# Publish the experimental Capability Gateway v1 contract

Status: experimental
Content: informative
Canonical source: this file
Generated: no
Compatibility: breaking
Contracts:

- `spec/capability-gateway-v1.md`
- `spec/capability-namespaces.md`
- `schemas/capability-gateway/v1/`
- `api/capability-gateway/v1/openapi.json`

## Behavior

Introduces the first public Capability Gateway contract:

- typed capability request, submission, Gateway-level status, immutable authorized manifest, and stable error documents;
- exact v1 lifecycle without cancellation, listing, streaming, or remote transport;
- RFC 8785 canonical request bytes over a restricted I-JSON value domain;
- fixed domain-separated SHA-256 request digests;
- strict whole-second UTC timestamps;
- request-ID idempotency and conflict semantics;
- capability namespace ownership and the `deployment.apply` naming rule;
- a deterministic no-effect `example.echo` reference capability.

This is classified as breaking because it establishes the initial public contract and all future implementations must bind to its exact names, versions, canonicalization, digest, lifecycle, and fail-closed behavior.

## Security and authority

- Caller JSON does not establish authenticated actor identity.
- Unknown fields, unsupported versions, duplicate keys, floating-point values, malformed Unicode, oversized bodies, remote references, and traversal fail closed.
- Public capability declarations do not prove installation, trust, admission, authorization, or production suitability.
- Providers receive immutable authorized manifests rather than raw caller bytes or unbound policy responses.
- Manifests reject digest mismatch, expiry, unsupported versions, substituted identity, and constraint widening.
- Anthesis remains authoritative for policy, approval, expiry, granted constraints, and evidence-requirement meaning; the public contract carries opaque references and exact bindings.
- The only executable reference effect is `example.echo`; the deployment fixture is synthetic and non-executable.

## Migration

There is no prior public Capability Gateway contract to migrate. Private or experimental implementations must:

- consume the released public schemas and vectors rather than maintain a second editable source;
- match canonical bytes and request digests exactly;
- keep runtime actor mappings, policy, persistent state, transport, privileged providers, and host configuration private;
- fail closed when a contract, capability schema version, digest, or manifest does not match.

Release activation, checksums, SBOM, attestations, and separate consumer verification remain under issue #17. Private pinned consumption and publication-manifest automation remain under the private Dubnium publication gate.

## Evidence

- canonical request bytes and fixed digest vector;
- positive request, manifest, result, and idempotency fixtures;
- negative duplicate-key, actor-spoof, unknown-field, malformed identifier, timestamp, Unicode, oversized-body, conflicting-ID, digest-substitution, expiry, and widening fixtures;
- deterministic no-effect reference implementation;
- property-style key-order and digest tests;
- bounded contract-tree, schema-reference, workflow-security, publication, and repository-policy CI;
- synthetic `deployment.apply` naming fixture.

## Private boundary

This change does not publish:

- production Gateway services, sockets, listener profiles, actor mappings, SQLite state, credentials, policy adapters, or provider routing;
- Anthesis policy or approval implementation;
- deployment schemas, constraints, providers, root workers, recovery, real repositories, revisions, targets, or evidence;
- Supervisor planning, prompts, memory, model routing, host topology, runners, incidents, logs, traces, or operational thresholds;
- private Git history or private producer coordinates.
