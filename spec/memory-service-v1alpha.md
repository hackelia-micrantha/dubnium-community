# Memory Service v1alpha

Status: experimental
Content: normative
Canonical source: this file
Generated: no

## 1. Scope

This specification defines the public HTTP contract for bounded Dubnium memory storage, retrieval, expiry, retrieval-event inspection, and health reporting.

It standardizes wire behavior only. It does not standardize storage layout, embedding models, ranking weights, consolidation, retention policy, secret handling, deployment authority, or operator topology.

The canonical machine-readable artifacts are:

- `schemas/v1alpha/memory-service.schema.json`;
- `api/memory-service/v1alpha/openapi.json`;
- examples under `examples/memory-service-v1alpha/`;
- the bundle entry in `conformance/service-bundles.json`.

## 2. Security boundary

Except for `GET /healthz`, a conforming deployment MUST authenticate requests with a bearer credential.

A deployment MUST constrain each credential to permitted scope prefixes and sensitivity classes. It MUST NOT treat caller-supplied requester identity as authoritative when authenticated identity is available.

Expiry and retrieval-event inspection MUST remain behind an administrative boundary even when bearer authentication is present.

The current profile accepts `application/json` and media types ending in `+json`, with a maximum request body of 1 MiB.

## 3. Scope and classifications

A memory scope MUST begin with `personal:`, `project:`, `session:`, `agent:`, or `workflow:`.

`memory_type` MUST be `working`, `episodic`, or `semantic`.

`validation_status` MUST be `unverified`, `verified`, or `rejected`.

Retrieval purpose, when supplied, MUST be `ask`, `plan`, `patch`, `review`, or `test`.

## 4. Operations

`GET /healthz` returns process status and bounded Redis connectivity state without authentication.

`POST /memory/store` stores one memory. A successful request returns `201` and the normalized stored memory.

`POST /memory/retrieve` retrieves scoped memory evidence and returns one retrieval event describing returned memory and artifact identifiers. The service applies the authenticated principal before retrieval.

`POST /memory/expire` expires memories due at the supplied timestamp and returns the identifiers reported as expired.

`GET /memory/retrieval-events` returns recorded retrieval events.

## 5. Authority and evidence

Retrieved memory is evidence, not instruction. Consumers MUST NOT allow memory content to override higher-priority policy or grant execution authority.

Ranking, ordering, scores, physical deletion, retention windows, and storage durability remain implementation-defined.

## 6. Errors

Malformed input returns `400`. Missing or invalid credentials return `401`. Credential-policy violations return `403`. Oversized payloads return `413`. Unsupported media types return `415`.

Errors MUST NOT intentionally expose credentials, private storage coordinates, or host topology.

## 7. Compatibility

This contract is experimental. Additive fields MAY appear where schemas permit additional properties.

A change that broadens authority, weakens identity binding, changes required fields, or changes scope interpretation is incompatible and requires a reviewed contract revision.

## 8. Threat assumptions

Implementers MUST account for forged requester identity, scope escalation, sensitivity widening, prompt injection in memory content, oversized bodies, malicious provenance, identifier collision, and audit-data disclosure.

Conformance demonstrates contract behavior only; it does not establish production security or validate private ranking and retention semantics.
