# Publish Experimental Service OpenAPI Bindings

Date: 2026-08-06

## Summary

Publish implementation-derived OpenAPI 3.1.2 bindings for the current Dubnium memory service, supervisor/LLM gateway, and scheduler API.

## Scope

- Added `api/memory-service/v1alpha/openapi.json` for authenticated memory storage and retrieval, expiry, retrieval-event inspection, and bounded health.
- Added `api/supervisor-gateway/v1alpha/openapi.json` for the bounded OpenAI-compatible `/v1/models` and `/v1/chat/completions` surface, including SSE streaming, read-only memory metadata, specialist requests, and explicit proposal-only authority metadata.
- Added `api/scheduler/v1alpha/openapi.json` for schedule listing and inspection, journal history, and systemd-backed trigger, pause, and resume controls.
- Added explicit operator visibility markers and deployment-boundary warnings where services do not enforce inbound authorization themselves.
- Recorded the reviewed private implementation commit and source paths in each binding.
- Updated the API catalog and boundary guidance.

## Compatibility

These are additive experimental bindings. They do not promote the underlying services to stable public contracts.

The bindings intentionally do not standardize:

- memory storage layout, embedding implementation, ranking weights, token interpretation, or retention policy;
- scheduler persistence, systemd unit generation, concurrency, retry, or policy semantics;
- a complete OpenAI API surface;
- deployment authority, listener exposure, or private authentication and routing configuration.

Operator operations remain suitable only for trusted administrative boundaries and may change incompatibly while the release line remains experimental.

## Provenance

The bindings were reviewed against `ryjen/dubnium` commit `cfc0af808b3cac9e1098f630a187ab9497a80a70`.

Related: #38
