# Supervisor / LLM Gateway v1alpha

Status: experimental
Content: normative
Canonical source: this file
Generated: no

## 1. Scope

This specification defines the bounded OpenAI-compatible surface exposed by the packaged Dubnium supervisor gateway.

The packaged executable is `supervisor-gateway = dubnium_supervisor_gateway.lineage_app:main`. The public contract includes logical model declaration, capability negotiation, trusted execution identity, sanitized streaming, normalized errors, specialist metadata, and optional delegation lineage.

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

`GET /v1/models` returns the configured logical alias rather than a private provider or model path.

The declaration includes contract version `dubnium.llm-gateway.v1`, logical-alias status, and the current capability posture: chat completions and streaming enabled; tools, structured output, and deterministic seed disabled; sampling parameters `temperature` and `top_p`; supervisor-specialist topology; local-only privacy class; and resolved-execution evidence.

Private provider endpoints, credentials, and backend identifiers MUST NOT appear in the model declaration.

## 4. Chat requests and capability negotiation

`POST /v1/chat/completions` requires `model` and `messages`.

`model` MUST exactly match the configured logical alias. Unsupported contract versions and unavailable requested capabilities MUST be rejected before backend dispatch.

The request MAY contain `stream`, `temperature`, `top_p`, `max_tokens`, `stop`, and `dubnium`.

This profile MUST NOT accept `tools` or `response_format`.

## 5. Memory context

Supported memory modes are `off` and `read-only`.

When read-only memory is enabled, the gateway requires an actor plus a workspace or project scope. Retrieved memory is injected as untrusted evidence beneath gateway policy.

The response reports whether memory was disabled, unavailable, used, empty, or reduced.

## 6. Specialist requests

A specialist request requires a non-empty `kind` and `input.prompt`.

The current implementation truncates the selected prompt to 2,000 characters before delegation; it does not reject an otherwise valid longer prompt solely for length.

Unsupported or disabled specialists are rejected before model backend dispatch. Public specialist metadata MUST NOT expose private backend identifiers.

## 7. Trusted execution and lineage

Every successful completion includes gateway-authored execution identity with contract version, requested alias, resolved route identity, bounded sampling data, fallback chain, and execution steps.

Caller-supplied or backend-supplied execution metadata MUST be replaced or removed.

When a material specialist delegation is selected or completed, the gateway emits a lineage object linking request, supervisor execution, specialist invocation, and synthesis. When no specialist delegation occurs, lineage MAY be absent.

## 8. Streaming

For streaming requests, the first server-sent data event contains trusted Dubnium metadata and an empty choices array. Its JSON payload is described by the canonical `StreamMetadataEvent` schema.

Subsequent backend events have model names rewritten to the logical alias and backend-authored Dubnium metadata removed. A terminal `[DONE]` event is preserved when supplied by the backend.

## 9. Errors

Errors use the normalized envelope with code, message, type, contract version, and retryable status.

Invalid requests return `400`; oversized bodies `413`; unsupported media types `415`; unavailable required dependencies `503`.

Backend failures MUST NOT intentionally expose private backend response text, model paths, provider endpoints, or exception details.

## 10. Compatibility

This is an OpenAI-compatible subset, not compatibility with every OpenAI endpoint or parameter.

A change that expands supported authority, exposes private execution identity, accepts previously rejected capabilities, or changes alias negotiation is incompatible and requires a reviewed contract revision.

## 11. Threat assumptions

Implementers MUST account for alias confusion, capability smuggling, forged identity, prompt injection, backend metadata spoofing, specialist backend disclosure, lineage spoofing, private model-name leakage, and untrusted streaming chunks.

Conformance validates the public contract profile only and does not certify model safety, output quality, or deployment security.
