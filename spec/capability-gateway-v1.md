Status: v1alpha
Content: normative
Canonical source: spec/capability-gateway-v1.md
Generated: no

# Capability Gateway portable contracts v1

## Scope

This specification defines the implementation-neutral request, submission, status, authorized-manifest, error, canonicalization, and no-effect conformance contracts for a local capability gateway.

It does not define transport authentication, operational storage, policy evaluation, approval workflows, provider registration, system services, credentials, or privileged effects. A runtime MAY implement those concerns, but it MUST preserve the portable identities and narrowing rules defined here.

## Contract set

The v1alpha bundle consists of:

- `CapabilityRequest`: caller-controlled typed intent;
- `CapabilitySubmission`: accepted or rejected request identity;
- `CapabilityStatus`: gateway-level lifecycle and bounded terminal summary;
- `AuthorizedCapabilityManifest`: immutable runtime-produced provider input;
- `CapabilityError`: stable machine-readable failure envelope;
- `example.noop`: deterministic no-effect capability and result.

All contract documents use `contract_version: "1.0"`. Unsupported versions MUST fail closed.

## Caller and actor boundary

A `CapabilityRequest` MUST NOT establish authenticated actor identity. The effective actor is transport-derived runtime context and appears only in an `AuthorizedCapabilityManifest` produced after governance mediation.

A runtime MUST reject caller-controlled fields that attempt to assert an actor, policy decision, provider operation, authorization, or execution result. Unknown fields are errors in v1.

Admission to submit a capability request does not authorize the effect. A provider MUST receive only an exact, unexpired, final authorized manifest.

## Request normalization

Before digesting or applying idempotency, an implementation MUST:

1. enforce a 65,536-byte raw input limit before JSON parsing;
2. decode strict UTF-8;
3. reject duplicate object keys before constructing a map;
4. normalize every string and object key to Unicode NFC;
5. reject object-key collisions introduced by NFC normalization;
6. reject `null`, floating-point numbers, non-finite numbers, and integers outside the signed interoperable 53-bit range;
7. reject unknown fields and unsupported contract or capability schema versions;
8. validate identifiers, references, timestamps, payload, and constraints;
9. materialize omitted `requested_constraints` as `{}` and omitted `evidence_refs` as `[]`;
10. omit `$schema` metadata from the normalized request.

Optional fields are absent or present; `null` is not equivalent to absence.

## Canonical JSON

Canonical bytes are UTF-8 JSON with:

- NFC-normalized strings and keys;
- object keys sorted by Unicode code point;
- arrays kept in their original order;
- no insignificant whitespace;
- `,` between array/object members and `:` between names and values;
- lowercase JSON literals;
- no trailing newline.

The request digest is:

```text
sha256:<lowercase hexadecimal SHA-256 of canonical normalized request bytes>
```

Every normalized request field participates in the digest. `$schema` metadata and transport-derived actor identity do not.

## Timestamp profile

Timestamps MUST use exactly `YYYY-MM-DDTHH:MM:SSZ` and represent a valid UTC time. Offsets, fractional seconds, leap-second spelling, and local time are unsupported in v1alpha.

When present, `expires_at` MUST be later than `requested_at`.

## Idempotency

A gateway MUST treat `request_id` plus canonical request digest as the idempotency identity.

- Repeating the same `request_id` and digest MUST return the existing logical request.
- Reusing a `request_id` with a different digest MUST fail closed.
- Restart or retry MUST NOT create a second provider dispatch for the same authorized logical request.

Operational persistence and dispatch mechanics remain runtime-specific.

## Submission envelope

An accepted `CapabilitySubmission` MUST contain the normalized request ID and digest and MUST NOT contain an error.

A rejection produced after request normalization SHOULD contain the same request ID and digest. A rejection produced before a trustworthy identity can be computed, such as invalid UTF-8, duplicate keys, oversized input, or malformed JSON, MAY omit both fields. It MUST NOT include only one of the two identity fields.

A rejected submission MUST contain a stable error. Rejection is not a durable request state unless the runtime successfully established and persisted the request identity.

## Gateway state

Portable gateway status uses only:

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

Every `CapabilityStatus` MUST contain the exact normalized request ID and digest. Provider-specific phases are not mirrored into this state machine. A status MAY include a stable provider operation reference and evidence references.

`denied`, `failed`, and `indeterminate` statuses MUST contain an error. Other statuses MUST NOT contain an error. A bounded `terminal_result` MAY appear only for `succeeded` or `failed`; the v1 conformance profile limits its canonical representation to 4,096 bytes.

## Authorized manifest

An `AuthorizedCapabilityManifest` is immutable provider input created by the runtime. It MUST bind:

- exact request ID and digest;
- authenticated actor reference;
- exact capability name and schema version;
- exact target reference;
- exact normalized payload and payload digest;
- one final governance decision reference and policy reference;
- granted constraints that narrow or equal requested constraints;
- decision and manifest expiry;
- an issuance time strictly earlier than manifest expiry;
- a manifest expiry no later than either the decision expiry or caller-requested expiry;
- required pre-execution and completion evidence references.

The manifest MUST NOT widen capability, target, payload, constraints, expiry, or evidence authority. The decision digest MUST equal the request digest. Only a final `allow` outcome is executable. Approval-required, denied, expired, unsupported, malformed, unavailable, or indeterminate outcomes are not authority.

A provider MUST independently verify the manifest before effect execution. Provider results and completion evidence MUST NOT authorize a later invocation.

## Constraint narrowing

Constraint semantics are capability-specific. A provider MUST reject unknown granted constraints and any grant broader than the normalized request.

For `example.noop` v1:

- the request asks for `max_result_bytes` from 64 through 4096;
- the manifest grants a positive `max_result_bytes` no greater than requested;
- the reference provider rejects a deterministic result larger than the granted bound.

## No-effect reference capability

`example.noop` v1 accepts:

```json
{"message":"hello","repeat":2}
```

The reference provider returns the message exactly `repeat` times. It performs no filesystem, network, process, repository, service, credential, or host mutation. It MUST be deterministic for the same validated request and manifest.

The reference implementation is a conformance example, not a production gateway or policy engine.

## Errors

Errors use a stable dotted `code` and bounded human-readable `message`. Implementations MAY include a bounded `field` path. They MUST NOT expose credentials, private runtime topology, raw policy documents, or unbounded payloads.

The conformance implementation defines representative codes for duplicate keys, unsupported versions, unknown fields, digest mismatch, expiry, payload substitution, and constraint widening.

## Compatibility

This contract is `v1alpha`.

- Adding an optional field is incompatible until the version explicitly permits it because v1 rejects unknown fields.
- Changing canonicalization, digest participation, required fields, identifier grammar, state meaning, or narrowing semantics requires a new contract version.
- New capability payload schemas may be added without changing the envelope version when their stable capability name and schema version are distinct.
- A consumer MUST reject unsupported versions rather than guess or silently downgrade.

## Conformance

The offline suites are run with:

```text
python3 conformance/capability_gateway_v1.py run-fixtures conformance/fixtures/v1
python3 conformance/gateway_envelopes_v1.py run-fixtures conformance/fixtures/v1
```

A conforming implementation SHOULD consume the same canonical bytes, digest vectors, positive manifests and envelopes, and negative fixtures. The suites require no network, credentials, private source, policy service, system service manager, or privileged access.
