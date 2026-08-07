# Publish Experimental Service Contract Bundles

Status: experimental
Content: informative
Canonical source: this file
Generated: no

Date: 2026-08-06

## Summary

Publish complete experimental contract bundles for the current Dubnium memory service, packaged supervisor/LLM gateway, and scheduler API.

Each bundle includes a normative specification, canonical JSON Schema, OpenAPI 3.1.2 transport binding, synthetic positive and negative examples, operation coverage, schema-to-OpenAPI consistency checks, and generic conformance enrollment.

## Scope

### Memory service

- Publish health, store, retrieve, expire, retrieval-event, and error wire shapes.
- Preserve bearer authentication, credential scope and sensitivity ceilings, operator visibility, and private ranking and storage semantics.
- Add positive examples for every operation and negative examples for invalid scope and retrieval limits.

### Supervisor / LLM gateway

- Align the public contract to `dubnium_supervisor_gateway.lineage_app:main`.
- Publish logical alias negotiation, capabilities, trusted execution identity, normalized errors, streaming metadata, and delegation lineage.
- Model specialist prompt behavior as truncation to 2,000 characters rather than request rejection.
- Add positive examples for health, model declaration, chat JSON, streaming metadata, and errors plus negative capability, version, and alias fixtures.

### Scheduler

- Publish process health, schedule list/detail, recent history, control, and error wire shapes.
- Describe current history behavior accurately: up to 20 parsed journal JSON records, no field redaction, and no separate response-byte bound.
- Describe control responses as commands issued rather than proof of successful systemd state transitions.
- Add positive examples for every operation and negative history/control fixtures.

## Generic conformance architecture

`conformance/service-bundles.json` remains data-only. It declares:

- canonical specifications, schemas, OpenAPI bindings, and examples;
- exact operation-to-example coverage;
- required canonical schema definitions;
- schema-to-OpenAPI bindings;
- declarative OpenAPI assertions.

`conformance/contract_bundle.py` is the single generic validator. It:

- rejects unknown catalog keys and contract-specific code hooks;
- rejects unknown JSON Schema keywords and unsupported formats instead of silently ignoring them;
- enforces file-size, nesting, collection-size, duplicate-key, and local-reference boundaries;
- validates positive and negative examples;
- requires every OpenAPI operation to have examples;
- resolves and structurally compares canonical schemas with their OpenAPI representations;
- verifies declared paths, components, and contract-specific assertions.

No memory-, supervisor-, or scheduler-specific executable was added.

## Compatibility

These changes remain experimental and additive. They do not promote the services to stable public contracts.

The bundles intentionally do not standardize:

- memory storage layout, embeddings, ranking, consolidation, or retention;
- scheduler persistence, unit generation, retry, command-success attestation, or host policy;
- a complete OpenAI API surface;
- deployment authority, listener exposure, private authentication, or routing configuration.

## Security

- All examples are synthetic.
- Remote schema references and repository escapes are prohibited.
- Scheduler history is explicitly classified as sensitive unredacted administrative output.
- Supervisor backend-authored metadata is not treated as trusted execution or lineage.
- Memory content remains evidence and does not grant execution authority.

## Provenance

The transport behavior was reviewed against `ryjen/dubnium` commit `cfc0af808b3cac9e1098f630a187ab9497a80a70`.

The public specifications, schemas, examples, and conformance catalog are independently reviewable from this repository and do not require private source access.

Related: #11
