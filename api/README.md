# API bindings

Status: experimental
Content: informative
Canonical source: this file
Generated: no

`api/` contains public transport bindings derived from normative contracts, including OpenAPI descriptions when HTTP is applicable.

A binding MUST NOT invent authority, identity, lifecycle, canonicalization, error, or compatibility semantics absent from the normative specification. Generated bindings identify their canonical source version or digest.

## Published bindings

| Binding | Release line | Specification | Canonical schema | Examples |
| --- | --- | --- | --- | --- |
| `capability-gateway/v1/openapi.json` | v1alpha | `spec/capability-gateway-v1.md` | `schemas/v1/` | `examples/capability-gateway-v1/` |
| `memory-service/v1alpha/openapi.json` | experimental | `spec/memory-service-v1alpha.md` | `schemas/v1alpha/memory-service.schema.json` | `examples/memory-service-v1alpha/` |
| `supervisor-gateway/v1alpha/openapi.json` | experimental | `spec/supervisor-gateway-v1alpha.md` | `schemas/v1alpha/supervisor-gateway.schema.json` | `examples/supervisor-gateway-v1alpha/` |
| `scheduler/v1alpha/openapi.json` | experimental | `spec/scheduler-v1alpha.md` | `schemas/v1alpha/scheduler.schema.json` | `examples/scheduler-v1alpha/` |

The three experimental service bindings are enrolled in `conformance/service-bundles.json`. That catalog is data-only and is validated by the generic `conformance.contract_bundle` runner.

## Boundary rules

- OpenAPI documents describe wire shapes; they do not grant authority or define deployment exposure.
- `x-dubnium-visibility: operator` marks operations that belong behind a trusted administrative boundary.
- `x-dubnium-canonical-source` records implementation provenance for review; public specifications and schemas remain independently usable.
- Alpha bindings intentionally leave private implementation semantics open. In particular, memory storage, embedding, and ranking and scheduler persistence, unit generation, concurrency, retry, and policy behavior are not standardized here.
- The supervisor gateway is an OpenAI-compatible subset, not a claim of compatibility with every OpenAI API parameter or endpoint.
- New API bundles SHOULD add catalog data, schemas, examples, and declarative assertions rather than a contract-specific script.
