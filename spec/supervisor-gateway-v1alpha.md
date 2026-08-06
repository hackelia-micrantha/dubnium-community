# Supervisor / LLM Gateway v1alpha

Status: experimental
Content: normative
Canonical source: this file
Generated: no

## 1. Scope

This specification defines the bounded OpenAI-compatible surface exposed by the packaged Dubnium supervisor gateway.

The packaged executable is `supervisor-gateway = dubnium_supervisor_gateway.lineage_app:main`. The public contract therefore includes logical model declaration, capability negotiation, trusted execution identity, sanitized streaming, normalized errors, specialist metadata, and optional supervisor-specialist lineage.

The canonical machine-readable artifacts are:

- `schemas/v1alpha/supervisor-gateway.schema.json`;
- `api/supervisor-gateway/v1alpha/openapi.json`;
- examples under `examples/supervisor-gateway-v1alpha/`;
- the bundle entry in `conformance/service-bundles.json`.

## 2. Deployment boundary

The current service does not enforce inbound authentication. A deployment MUST bind it to a trusted local boundary or place it behind authenticated ingress.

Caller metadata MUST NOT be treated as trusted identity unless deployment policy explicitly enables that behavior.

Model and specialist output is proposal-only. A consumer MUST NOT infer tool, deployment, memory-write, host-control, or policy authority from a successful completion.

## 3. Logical model declaration

`GET /v1/models` MUST return the configured logical alias rather than a private provider or model path.

The model declaration MUST include:

- contract version `dubnium.llm-gateway.v1`;
- `logical_alias: true`;
- declared capabilities;
- `tools: false`;
- `structured_output: false`;
- `deterministic_seed: false`;
- sampling parameters `temperature` and `top_p`;
- topology `supervisor-specialist`;
- privacy class `local-only`;
- evidence level `resolved-execution`.

Private model artifacts, provider endpoints, credentials, and backend identifiers MUST NOT appear in the model declaration.

## 4. Chat requests

`POST /v1/chat/completions` MUST require `model` and `messages`.

`model` MUST be a canonical logical alias and MUST exactly match the configured alias. Unknown aliases MUST be rejected before backend dispatch.

The request MAY contain `stream`, `temperature`, `top_p`, `max_tokens`, `stop`, and `dubnium`.

The request MUST NOT advertise or accept `tools` or `response_format` in this profile. Their presence MUST produce a capability mismatch or other bounded `400` error before backend dispatch.

## 5. Contract and capability negotiation

`dubnium.contract_version`, when omitted, defaults to `dubnium.llm-gateway.v1`. Any unsupported version MUST be rejected.

`dubnium.capabilities` MAY request a subset of the declared alias capabilities. A request MUST be rejected when it requires an undeclared capability or a different posture.

Capability negotiation MUST occur before model backend dispatch.

## 6. Memory context

Supported memory modes are `off` and `read-only`.

When read-only memory is enabled, the gateway MUST require an actor plus a workspace or project scope. The gateway MUST NOT accept model output as a memory scope or identity decision.

Retrieved memory MUST be injected as untrusted evidence beneath immutable gateway policy. Memory content MUST NOT grant authority or override system, developer, supervisor, or governance policy.

The response MUST describe whether memory was disabled, unavailable, used, empty, or reduced.

## 7. Specialist requests

A specialist request MUST contain a non-empty `kind` and `input.prompt`.

The gateway MUST resolve specialist kind through a deterministic catalog. Unsupported or disabled specialists MUST be rejected before model backend dispatch.

Public specialist metadata MUST NOT expose private backend identifiers. Specialist results remain evidence for supervisor synthesis, not authority.

## 8. Trusted execution identity

Every successful completion MUST include gateway-authored execution identity containing:

- contract version;
- requested logical alias;
- resolved provider class, route, model artifact identity, runtime, and topology;
- bounded sampling parameters;
- fallback chain;
- execution lineage steps when present.

Caller-supplied or backend-supplied execution metadata MUST be removed or replaced. The gateway MUST NOT echo untrusted backend `dubnium` metadata as authoritative.

## 9. Delegation lineage

When a material specialist delegation is selected or completed, the gateway MUST emit a lineage object linking:

- request;
- supervisor execution;
- specialist invocation;
- supervisor synthesis.

Identifiers MUST be gateway-authored UUIDs. Parent-child relationships MUST be internally consistent.

When no specialist delegation occurs, lineage MAY be absent.

## 10. Streaming

For streaming requests, the first server-sent event MUST contain trusted Dubnium metadata and an empty choices array.

Subsequent backend events MAY be proxied, but the gateway MUST rewrite private model names to the logical alias and MUST remove backend-authored Dubnium metadata.

The stream MUST preserve the terminal `[DONE]` event when supplied by the backend.

## 11. Errors

Errors MUST use the normalized error envelope with code, message, type, contract version, and retryable status.

Backend failures MUST NOT expose private backend response text, model paths, provider endpoints, or exception detail.

Invalid requests MUST return `400`; oversized bodies `413`; unsupported media types `415`; unavailable required dependencies `503`.

## 12. Compatibility

This is an OpenAI-compatible subset, not compatibility with every OpenAI endpoint or parameter.

A change that expands supported authority, exposes private execution identity, accepts previously rejected capabilities, or changes alias negotiation is incompatible and requires a reviewed contract revision.

Additive response fields MAY appear where schemas permit them. Consumers MUST ignore unknown additive fields.

## 13. Threat assumptions

Implementers MUST account for alias confusion, capability smuggling, forged identity, prompt injection, backend metadata spoofing, specialist backend disclosure, lineage spoofing, private model-name leakage, and untrusted streaming chunks.

Conformance validates the public contract profile only and does not certify model safety, output quality, or deployment security.
