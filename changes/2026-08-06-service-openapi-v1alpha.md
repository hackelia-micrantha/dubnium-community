# Publish Experimental Service OpenAPI Bindings

Date: 2026-08-06

## Summary

Publish implementation-derived OpenAPI 3.1.2 bindings for the current Dubnium memory service, supervisor/LLM gateway, and scheduler API.

## Scope

- Added `api/memory-service/v1alpha/openapi.json` for authenticated memory storage and retrieval, expiry, retrieval-event inspection, and bounded health.
- Added `api/supervisor-gateway/v1alpha/openapi.json` for the packaged `supervisor-gateway` executable and its bounded OpenAI-compatible `/v1/models` and `/v1/chat/completions` surface.
- Documented logical model alias declaration, `dubnium.llm-gateway.v1` negotiation, capability requirements, read-only memory metadata, specialist requests, proposal-only authority metadata, trusted execution identity, normalized contract errors, sanitized SSE behavior, and optional supervisor-specialist lineage.
- Explicitly omitted `tools` and `response_format` from the request schema because the current alias declaration rejects those capabilities.
- Added `api/scheduler/v1alpha/openapi.json` for schedule listing and inspection, journal history, and systemd-backed trigger, pause, and resume controls.
- Added explicit operator visibility markers and deployment-boundary warnings where services do not enforce inbound authorization themselves.
- Recorded the reviewed private implementation commit, packaged console entry point, and source paths in each applicable binding.
- Added offline regression coverage for bundled references, unique operation IDs, the supervisor console entry point, capability declaration, trusted execution metadata, lineage, and contract-attributed errors.
- Updated the API catalog and boundary guidance.

## Compatibility

These are additive experimental bindings. They do not promote the underlying services to stable public contracts.

The bindings intentionally do not standardize:

- memory storage layout, embedding implementation, ranking weights, token interpretation, or retention policy;
- scheduler persistence, systemd unit generation, concurrency, retry, or policy semantics;
- a complete OpenAI API surface;
- private model identifiers, runtime topology, specialist backend identifiers, or routing configuration;
- deployment authority, listener exposure, or private authentication configuration.

Operator operations remain suitable only for trusted administrative boundaries and may change incompatibly while the release line remains experimental.

## Provenance

The bindings were reviewed against `ryjen/dubnium` commit `cfc0af808b3cac9e1098f630a187ab9497a80a70`. The supervisor binding follows the packaged console script `supervisor-gateway = dubnium_supervisor_gateway.lineage_app:main`, including inherited behavior from the contract and legacy gateway layers.

Related: #11
