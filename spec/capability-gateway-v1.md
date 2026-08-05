# Capability Gateway contract v1

Status: experimental
Content: normative
Canonical source: this file
Generated: no

## 1. Scope

This specification defines the portable, implementation-neutral contract between a Capability Gateway caller, the Gateway, and a capability provider for the first experimental Dubnium Capability Gateway profile.

V1 defines:

- one typed capability request;
- submission acceptance or rejection;
- gateway-level status inspection;
- one immutable authorized capability manifest;
- a stable error envelope;
- canonical request bytes and a domain-separated request digest;
- a no-effect `example.echo` reference capability.

V1 does **not** define production transport authentication, actor mappings, persistent state, policy evaluation, approval workflows, privileged providers, deployment execution, cancellation, request listing, event streaming, retries across providers, remote transport, systemd, NixOS, credentials, host policy, Supervisor behavior, memory behavior, or operational evidence retention.

## 2. Authority and ownership

The public contract is descriptive interoperability material. A public schema or capability name MUST NOT be interpreted as proof that a provider is installed, trusted, authenticated, admitted, authorized, or safe for production.

The effective actor MUST be established by the runtime transport or listener profile. Caller JSON MUST NOT establish authenticated actor identity.

Anthesis, when used, remains authoritative for policy, approval, granted-constraint, expiry, and evidence-requirement semantics. This contract carries opaque governance references and an executable authorized manifest; it MUST NOT redefine Anthesis decision authority.

A provider MUST receive an immutable authorized manifest rather than the original raw caller bytes or an unbound policy response.

## 3. Contract and schema versions

All v1 documents defined here contain:

```json
{"contract_version":"1"}
```

The contract version is independent of the monorepo release version. Implementations MUST fail closed for an unsupported contract version or capability schema version.

The initial release is experimental and pre-1.0. It carries no stable compatibility promise beyond the exact released schemas and fixtures.

## 4. Capability names and namespaces

Capability names identify governed effects, not transport operations.

The initial deployment effect name is:

```text
deployment.apply
```

`deployment.request` MUST NOT be used as a capability name because request submission is already represented by the Gateway API.

Names consist of lowercase dot-separated segments. Each segment begins with a lowercase ASCII letter and may continue with lowercase ASCII letters, digits, or hyphens.

Namespace rules are defined in [capability-namespaces.md](capability-namespaces.md). `example.*` is reserved for synthetic, no-effect public examples. Public declaration does not confer runtime admission or authority.

V1 defines no extension point. An `x-*` field or undeclared `extensions` field MUST be rejected as an unknown field. A future version that introduces extensions MUST use an explicit namespaced `extensions` object and MUST define authorization, canonicalization, and unknown-extension behavior.

## 5. Canonical request model

A `CapabilityRequest` contains exactly:

- `contract_version`;
- caller-selected `request_id`;
- `capability` name and capability schema version;
- typed `target` reference;
- typed `payload`;
- bounded `evidence` references;
- `requested_at`;
- optional `expires_at`.

The request schema contains no actor field. Any caller-provided actor, authentication, authorization, policy, approval, manifest, provider, operation, or status field MUST be rejected as unknown.

Optional fields are either absent or contain their declared non-null value. V1 MUST NOT treat absent and `null` as equivalent.

No defaults are inserted before hashing. The normalized request is the validated request value exactly as represented by the v1 data model.

## 6. Canonical JSON value domain

Every digest-bearing value MUST satisfy the following restricted I-JSON domain:

- UTF-8 encoded JSON;
- no byte-order mark;
- no duplicate object member names;
- no lone UTF-16 surrogate code points;
- strings are preserved exactly and MUST NOT be silently Unicode-normalized;
- integers are limited to `[-9007199254740991, 9007199254740991]`;
- floating-point numbers, decimal literals, exponent notation, `NaN`, positive infinity, and negative infinity are prohibited;
- arrays and objects are bounded by the released schemas and parser limits;
- unknown fields are rejected unless a future version explicitly permits them.

Implementations MUST enforce the raw request byte limit before ordinary JSON parsing. Duplicate object member names MUST be rejected while parsing; JSON Schema validation alone is insufficient.

## 7. Canonicalization and request digest

The validated request MUST be serialized using RFC 8785 JSON Canonicalization Scheme within the restricted value domain above.

Object member names MUST be sorted according to RFC 8785 UTF-16 code-unit ordering. Strings MUST use RFC 8785 escaping. No insignificant whitespace is emitted.

The request digest is:

```text
SHA-256(
  UTF-8("dubnium.capability-request.v1") ||
  0x00 ||
  canonical_request_bytes
)
```

The external digest representation is lowercase hexadecimal with an explicit algorithm prefix:

```text
sha256:<64 lowercase hexadecimal characters>
```

SHA-256 is fixed for v1. V1 MUST NOT negotiate or accept another digest algorithm.

The following request fields participate in the digest:

- `contract_version`;
- `request_id`;
- `capability`;
- `target`;
- `payload`;
- `evidence`;
- `requested_at`;
- `expires_at`, when present.

Transport-derived actor identity does not participate in caller-controlled request bytes. The effective actor is bound separately in the authorized manifest and, when applicable, in the governance decision.

## 8. Timestamp normalization

V1 timestamps MUST use exactly whole-second UTC RFC 3339 form:

```text
YYYY-MM-DDTHH:MM:SSZ
```

Offsets other than `Z`, fractional seconds, leap-second text, missing seconds, and non-canonical case MUST be rejected.

When `expires_at` is present it MUST be later than `requested_at`. A runtime MAY apply a stricter private maximum lifetime, but that threshold is not part of the public v1 contract.

## 9. Request identifiers and idempotency

A request identifier is caller-selected and follows the released schema pattern. It is not an authorization token.

Within one Gateway identity and state domain:

- reuse of `request_id` with the same canonical request digest MUST return the existing logical request and MUST NOT dispatch the effect again;
- reuse of `request_id` with a different digest MUST fail with `request_id_conflict`;
- restart, retry, replay, prior success, status, receipts, logs, or evidence MUST NOT mint new authority or duplicate an effect.

The public reference retains bounded in-memory state only to demonstrate these semantics. Production persistence remains private.

## 10. Submission

A valid submission response contains the caller request ID, submission outcome, timestamp, and—when available—the canonical request digest.

`accepted` means the Gateway accepted the logical request for processing. It does not mean policy authorization, provider dispatch, success, or certification.

`rejected` contains the stable error envelope. Malformed raw bytes that do not expose a trustworthy request ID may instead be returned solely as RFC 9457 Problem Details by a transport binding.

## 11. Gateway status

V1 gateway states are:

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

The Gateway state is distinct from provider operation state. A status MAY carry one opaque provider operation reference and bounded provider state text, but MUST NOT mirror private provider phases into the public gateway lifecycle.

V1 defines no cancellation, listing, streaming, or resumption contract.

Terminal status rules:

- `succeeded` carries a bounded result;
- `denied`, `failed`, and `indeterminate` carry a stable error;
- terminal evidence references are attributable but MUST NOT authorize a later request.

## 12. Authorized capability manifest

An `AuthorizedCapabilityManifest` contains:

- the complete validated request;
- its exact request digest;
- runtime-derived actor reference and authentication method;
- one final executable authorization record;
- granted constraints;
- approval and evidence requirement references where applicable;
- issue and expiry timestamps.

A manifest MUST be rejected before dispatch when:

- its request digest does not match the embedded request;
- its contract or capability schema version is unsupported;
- actor, capability, target, payload, or request ID differs from the authorized request or decision binding;
- its authorization is absent, indeterminate, denied, approval-only, expired, or substituted;
- granted constraints widen the request;
- required pre-execution evidence is unavailable;
- unknown fields or unsupported references are present.

The v1 manifest authorization outcome is exactly `allow`. `require_approval` is not executable authority; a final exact decision is required before a manifest can be dispatched.

A Gateway or provider MAY narrow or reject authority. It MUST NOT widen authority.

## 13. Example echo constraint semantics

The `example.echo` capability is the only executable public reference capability in v1.

Its request payload includes `max_output_bytes`. An authorized manifest MAY grant an equal or smaller `max_output_bytes`; a larger value is widening and MUST be rejected.

The provider:

- performs no network, filesystem, process, repository, service, credential, or host mutation;
- returns the requested string a bounded number of times;
- computes UTF-8 output size before returning;
- rejects output larger than the granted bound;
- returns deterministic result content for the same manifest.

The synthetic `deployment.apply` fixture demonstrates naming and typing only. It MUST NOT be interpreted as a production deployment schema or implementation.

## 14. Evidence references

Evidence references are opaque, typed, digest-bound references. The contract does not define evidence storage, retrieval, truth, policy meaning, or retention.

Evidence references MUST NOT contain credentials or inline production evidence. An evidence reference or completion receipt MUST NOT independently authorize an invocation.

## 15. Error model

The stable error envelope is aligned with RFC 9457 Problem Details and adds:

- stable `code`;
- boolean `retryable`;
- optional request ID and request digest.

A transport SHOULD use the HTTP status in the error document where applicable. Private diagnostics MAY contain more detail, but public errors and logs MUST remain bounded and MUST NOT expose credentials, policy, topology, payloads, private paths, or operational evidence.

Unknown error codes in a stable contract fail closed. Experimental consumers MAY surface an unsupported code as `indeterminate` but MUST NOT convert it to authorization or success.

## 16. HTTP binding

The optional HTTP binding defines only:

```text
POST /v1/capability-requests
GET  /v1/capability-requests/{request_id}
GET  /healthz
```

The public OpenAPI document describes message shapes and response classes. It does not define TCP exposure, authentication, Unix socket paths, listener actor profiles, credentials, or production health internals.

Private Dubnium v1 uses HTTP over dedicated Unix domain sockets and no TCP exposure, but that transport deployment is not part of this public contract.

## 17. Conformance

The bundled conformance command MUST run without network access, credentials, Anthesis, systemd, NixOS, private repositories, or privileged effects.

Remote conformance targets are disabled. A future remote target mode MUST require explicit opt-in, destination allowlisting, and SSRF protections.

Conformance covers:

- duplicate-key and pre-parse size rejection;
- exact schema and unknown-field behavior;
- Unicode, integer, timestamp, absent/null, and ordering behavior;
- canonical bytes and domain-separated SHA-256 vectors;
- request-ID idempotency and conflict;
- actor spoof rejection;
- digest mismatch and manifest substitution;
- expiry and constraint widening;
- deterministic no-effect execution;
- bounded parser and mock-state behavior.

Passing conformance does not establish security review, production suitability, endorsement, or certification.

## 18. Compatibility

For the experimental v1 contract:

- adding an optional field is breaking unless the existing schema and semantics explicitly allow it;
- adding an enum value is breaking for fail-closed consumers;
- changing canonicalization, digest inputs, timestamp form, identifier form, authority binding, unknown-field behavior, or constraint semantics is breaking;
- an unsupported contract or capability schema version MUST fail closed;
- private extensions MUST remain behind adapters and MUST NOT claim public v1 conformance.

General project compatibility and deprecation policy remains in `COMPATIBILITY.md`.

## 19. Security and IP boundary

This contract intentionally publishes integration vocabulary and security invariants needed for interoperable implementations.

It does not publish:

- trusted actor mappings;
- listener/socket configuration;
- production policies, approvals, thresholds, exceptions, or escalation rules;
- real deployment targets, repositories, revisions, or constraints;
- privileged provider code or recovery behavior;
- production prompts, memory, model routing, Supervisor logic, incidents, logs, traces, benchmarks, or operational evidence;
- private repository provenance or host topology.

Fixtures MUST use synthetic identities, targets, revisions, decisions, evidence, timestamps, and payloads.
