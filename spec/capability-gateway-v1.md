Status: v1alpha
Content: normative
Canonical source: spec/capability-gateway-v1.md
Generated: no

# Capability Gateway portable contracts v1alpha

## Scope

This specification defines the implementation-neutral request, submission, status, authorized-manifest, error, canonicalization, digest, and no-effect conformance contracts for a local capability gateway.

It does not define production transport authentication, operational storage, policy evaluation, approval workflows, provider registration, system services, credentials, host topology, or privileged effects. A runtime MAY implement those concerns, but it MUST preserve the portable identities and narrowing rules defined here.

## Contract set

The v1alpha bundle consists of `CapabilityRequest`, `CapabilitySubmission`, `CapabilityStatus`, `AuthorizedCapabilityManifest`, `CapabilityError`, and the deterministic `example.noop` reference capability. All contract documents use `contract_version: "1.0"`. Unsupported versions MUST fail closed.

The capability namespace registry in `spec/capability-namespaces.md` is normative for public names. `deployment.apply` appears only as a synthetic typed fixture; this repository does not define production deployment behavior.

## Caller and actor boundary

A `CapabilityRequest` MUST NOT establish authenticated actor identity. The effective actor is transport-derived runtime context and appears only in an `AuthorizedCapabilityManifest` produced after governance mediation.

A runtime MUST reject caller-controlled fields that attempt to assert an actor, policy decision, provider operation, authorization, or execution result. Unknown fields are errors in v1alpha. Admission to submit a request does not authorize an effect. A provider MUST receive only an exact, unexpired, final authorized manifest.

## Input and value profile

Before digesting or applying idempotency, an implementation MUST:

1. enforce a 65,536-byte raw input limit before JSON parsing;
2. decode strict UTF-8;
3. reject duplicate object keys before constructing a map;
4. preserve every caller string and object key exactly; Unicode normalization is prohibited;
5. reject lone UTF-16 surrogates;
6. reject `null`, floating-point values, non-finite numbers, and integers outside the interoperable signed 53-bit range;
7. reject unknown fields and unsupported contract or capability schema versions;
8. validate identifiers, references, timestamps, payload, and constraints;
9. materialize omitted `requested_constraints` as `{}` and omitted `evidence_refs` as `[]`;
10. omit `$schema` metadata from the normalized request.

Optional fields are absent or present; `null` is not equivalent to absence.

## Canonical JSON

Canonical bytes MUST follow RFC 8785 JSON Canonicalization Scheme within the restricted value profile above:

- object keys are ordered by UTF-16 code units;
- strings and keys are not Unicode-normalized;
- arrays retain their original order;
- no insignificant whitespace is emitted;
- no trailing newline is included in canonical bytes.

The fixed v1alpha digest domains are:

```text
request: dubnium.capability-request.v1\0
payload: dubnium.capability-payload.v1\0
```

The request digest is:

```text
sha256:<lowercase SHA-256(domain || canonical normalized request bytes)>
```

The normalized-payload digest uses the payload domain and canonical normalized payload bytes. Every normalized request field participates in the request digest. `$schema` metadata and transport-derived actor identity do not.

The earlier experimental NFC/code-point/raw-hash draft is superseded. Digests produced by that draft are invalid and MUST NOT be accepted as aliases.

## Timestamp profile

Timestamps MUST use exactly `YYYY-MM-DDTHH:MM:SSZ` and represent a valid UTC time. Offsets, fractional seconds, leap-second spelling, and local time are unsupported. When present, `expires_at` MUST be later than `requested_at`.

## Idempotency

A gateway MUST treat `request_id` plus the canonical request digest as the logical identity.

- Repeating the same `request_id` and digest MUST return the existing logical request.
- Reusing a `request_id` with a different digest MUST fail closed with a stable conflict error.
- Retry or restart MUST NOT create a second provider dispatch for the same authorized logical request.
- Implementations MUST bound in-memory idempotency state; durable storage remains runtime-specific.

## Submission and error envelopes

An accepted `CapabilitySubmission` MUST contain request identity and a status reference and MUST NOT contain an error. A rejected submission MUST contain a stable error and MUST NOT contain a status reference.

Portable errors contain a stable lowercase `code`, bounded `message`, explicit boolean `retryable`, and optional bounded `field`. HTTP bindings use RFC 9457 Problem Details while preserving the same code and retryability semantics.

Errors MUST NOT expose credentials, private runtime topology, raw policy documents, or unbounded payloads.

## Gateway status

Portable gateway states are:

```text
received
validated
policy-pending
denied
authorized
dispatched
succeeded
failed
indeterminate
```

Every status MUST bind the exact request ID and digest. Provider operation identity becomes available only after dispatch and MUST NOT change. Terminal statuses are immutable. `succeeded` MUST contain a result and no error; `denied`, `failed`, and `indeterminate` MUST contain an error and no result; nonterminal states MUST contain neither.

## Authorized manifest

An `AuthorizedCapabilityManifest` is immutable provider input produced by the runtime. It MUST bind the exact request identity, authenticated actor reference, capability and schema version, target, normalized payload and domain-separated payload digest, final governance decision and policy references, narrowed constraints, bounded expiry, and required evidence references.

The manifest MUST NOT widen capability, target, payload, constraints, expiry, or evidence authority. Its decision digest MUST equal the request digest. Only a final `allow` outcome is executable. A provider MUST independently verify the manifest before execution.

## No-effect reference

`example.noop` v1 accepts a small message/repeat payload and returns a deterministic bounded result. It performs no filesystem, network, process, repository, service, credential, or host mutation. The reference implementation is a conformance example, not a production gateway or policy engine.

## HTTP binding

`api/capability-gateway/v1/openapi.json` is the portable OpenAPI 3.1.2 message binding. It defines submission, status inspection, health, and RFC 9457 errors only. Authentication, listener profiles, sockets, policy adapters, provider routing, and deployment remain private runtime concerns.

## Compatibility

This contract is experimental v1alpha.

- Unknown fields fail closed.
- Changing canonicalization, digest domains or participation, required fields, identifier grammar, state meaning, or narrowing semantics requires a new contract version.
- New capability payload schemas MAY be added when their namespace and schema version are distinct.
- Consumers MUST reject unsupported versions rather than guess or silently downgrade.

## Conformance

The single canonical command is:

```text
python3 -m conformance.capability_gateway_v1 run-fixtures conformance/fixtures/v1
```

The fixture suite includes fixed canonical bytes and request/payload digests, Unicode ordering and no-normalization vectors, request-ID conflicts, expiry and constraint narrowing, payload substitution, bounded state, portable envelopes, and synthetic `deployment.apply` data. It requires no network, credentials, private source, policy service, system service manager, NixOS, or privileged access.
