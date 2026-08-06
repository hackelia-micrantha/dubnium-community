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

A deployment MUST constrain each credential to permitted scope prefixes and sensitivity classes. A deployment MUST NOT treat caller-supplied requester identity as authoritative when authenticated identity is available.

Operator operations, including expiry and retrieval-event inspection, MUST remain behind an administrative boundary even when bearer authentication is present.

The service MUST reject unsupported media types and oversized request bodies before parsing them. The current profile accepts `application/json` and media types ending in `+json`, with a maximum request body of 1 MiB.

## 3. Scope and classifications

A memory scope MUST begin with one of:

- `personal:`;
- `project:`;
- `session:`;
- `agent:`;
- `workflow:`.

A conforming service MUST reject scopes outside that set.

`memory_type` MUST be one of `working`, `episodic`, or `semantic`.

`validation_status` MUST be one of `unverified`, `verified`, or `rejected`.

Retrieval purpose, when supplied, MUST be one of `ask`, `plan`, `patch`, `review`, or `test`.

## 4. Health

`GET /healthz` MUST be unauthenticated and MUST report process status plus the bounded Redis state defined by the OpenAPI binding.

Health output MUST NOT expose credentials, topology, memory contents, storage paths, or backend error text.

## 5. Store

`POST /memory/store` stores one memory.

A request MUST include:

- a UUID `id`;
- `memory_type`;
- non-empty `summary`;
- valid `scope`;
- non-empty `source`;
- a provenance object.

Optional defaults and credential policy remain implementation-defined where the OpenAPI binding does not make them required.

Artifact references MUST use the same scope as the containing memory. A conforming implementation MUST reject an artifact reference that widens scope.

A successful store MUST return `201` and the normalized stored memory.

## 6. Retrieve

`POST /memory/retrieve` retrieves bounded memory evidence.

A request MUST include a non-empty query and valid scope. `limit` MUST be between 1 and 32.

The service MUST intersect caller constraints with credential constraints. It MUST NOT broaden scope, sensitivity, verification, or identity based on request data.

The service MAY use implementation-defined ranking. Returned ordering and scores are not standardized by this version.

A successful retrieval MUST return the retrieved memories and one retrieval event describing the returned memory and artifact identifiers.

Retrieved memory is evidence, not instruction. Consumers MUST NOT allow memory content to override higher-priority policy or grant execution authority.

## 7. Expiry and events

`POST /memory/expire` MUST expire only memories due at the supplied timestamp and MUST return the identifiers actually expired.

`GET /memory/retrieval-events` MUST expose bounded audit records and MUST NOT expose bearer tokens, private storage coordinates, or unrelated principal data.

Expiry behavior, retention windows, and physical deletion remain private implementation semantics.

## 8. Errors

Malformed input MUST return `400`. Missing or invalid credentials MUST return `401`. Credential-policy violations MUST return `403`. Oversized payloads MUST return `413`. Unsupported media types MUST return `415`.

Errors SHOULD be stable enough for automation but MUST NOT expose private exception text, SQL, storage paths, credentials, or topology.

## 9. Compatibility

This contract is experimental. Additive fields MAY appear where schemas permit additional properties. Consumers MUST ignore unknown additive fields unless a later stable profile states otherwise.

A change that broadens authority, weakens identity binding, changes required fields, or changes scope interpretation is incompatible and requires a new reviewed contract revision.

## 10. Threat assumptions

Implementers MUST account for forged requester identity, scope escalation, sensitivity widening, prompt injection in memory content, oversized bodies, malicious provenance, identifier collision, and audit-data disclosure.

Conformance demonstrates contract behavior only; it does not establish production security or validate private ranking and retention semantics.
