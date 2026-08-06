# Publish Experimental Service Contract Bundles

Date: 2026-08-06

## Summary

Publish complete experimental contract bundles for the current Dubnium memory service, packaged supervisor/LLM gateway, and scheduler API.

The bundles include normative specifications, canonical JSON Schemas, synthetic positive and negative examples, OpenAPI bindings, generic conformance enrollment, regression tests, and this change record.

## Scope

### Memory service

- Added `spec/memory-service-v1alpha.md`.
- Added `schemas/v1alpha/memory-service.schema.json`.
- Added a synthetic store request and an invalid-scope negative fixture.
- Enrolled health, store, retrieve, expire, and retrieval-event operations in the generic contract-bundle catalog.
- Preserved bearer authentication, bounded scopes, operator visibility, and private ranking/storage semantics.

### Supervisor / LLM gateway

- Added `spec/supervisor-gateway-v1alpha.md`.
- Added `schemas/v1alpha/supervisor-gateway.schema.json`.
- Added synthetic chat request/response examples and an unsupported-tools negative fixture.
- Kept the OpenAPI binding aligned to the packaged `dubnium_supervisor_gateway.lineage_app:main` executable.
- Enrolled alias negotiation, capabilities, trusted execution identity, normalized errors, streaming sanitization, and delegation lineage in declarative conformance assertions.

### Scheduler

- Added `spec/scheduler-v1alpha.md`.
- Added `schemas/v1alpha/scheduler.schema.json`.
- Added a synthetic schedule-detail response and an invalid-control-status negative fixture.
- Enrolled inspection, journal history, trigger, pause, and resume operations in the generic contract-bundle catalog.
- Preserved declarative schedule ownership and trusted administrative-boundary requirements.

## Generic conformance architecture

Added:

- `conformance/service-bundles.json`, a data-only catalog;
- `conformance/contract_bundle.py`, one bounded generic runner for all enrolled HTTP service contracts;
- generic regression coverage in `tests/test_service_openapi_bindings.py`.

The runner validates:

- normative specification markers and BCP 14 requirements;
- OpenAPI 3.1.2 documents, local references, unique operation IDs, expected paths, and expected components;
- declarative JSON-pointer assertions;
- canonical schema metadata;
- positive and negative example documents through a bounded JSON Schema 2020-12 subset;
- catalog completeness and the prohibition on contract-specific code hooks.

New HTTP APIs should normally add catalog data and artifacts rather than per-API scripts. Existing specialized conformance remains limited to semantics that are not adequately expressible as schemas and declarative fixtures.

## Repository guidance

Updated API, conformance, contribution, and repository-layout guidance to establish:

- `scripts/` as repository-wide operational entry points;
- reusable validators as modules or packages;
- API variation as data, schemas, examples, and assertions;
- explicit justification for any irreducibly contract-specific executable.

## Compatibility

These changes are additive and experimental. They do not promote the services to stable public contracts.

The bundles intentionally do not standardize:

- memory storage layout, embedding implementation, ranking weights, token interpretation, consolidation, or retention policy;
- scheduler persistence, systemd unit generation, concurrency, retry, or policy semantics;
- a complete OpenAI API surface;
- deployment authority, listener exposure, or private authentication and routing configuration.

Operator operations remain suitable only for trusted administrative boundaries and may change incompatibly while the release line remains experimental.

## Security

- All examples are synthetic and unsuitable for deployment.
- Remote schema references and contract-specific catalog hooks are prohibited.
- The generic validator applies bounded file-size and nesting limits.
- The supervisor contract excludes private backend identifiers and unsupported tool or structured-output capabilities.
- The memory and scheduler contracts preserve credential, scope, and administrative-boundary requirements.

## Provenance

The transport bindings were reviewed against `ryjen/dubnium` commit `cfc0af808b3cac9e1098f630a187ab9497a80a70`.

The public specifications, schemas, examples, and conformance catalog are independently reviewable from this repository and do not require private source access.

Related: #11
