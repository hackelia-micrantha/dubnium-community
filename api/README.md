# API bindings

Status: experimental
Content: informative
Canonical source: this file
Generated: no

`api/` contains public transport bindings derived from normative contracts, including OpenAPI descriptions when HTTP is applicable.

A binding MUST NOT invent authority, identity, lifecycle, canonicalization, error, or compatibility semantics absent from the normative specification. Generated bindings identify their canonical source version or digest.

## Published bindings

| Binding | Release line | Scope |
| --- | --- | --- |
| `capability-gateway/v1/openapi.json` | v1alpha | Typed capability submission and bounded request status |
| `memory-service/v1alpha/openapi.json` | experimental | Memory collections, append/query, health, and explicitly marked operator projections |
| `supervisor-gateway/v1alpha/openapi.json` | experimental | OpenAI-compatible model listing and chat completions, including SSE streaming |
| `scheduler/v1alpha/openapi.json` | experimental | Job inspection, bounded controls, triggering, and metrics |

## Boundary rules

- OpenAPI documents describe wire shapes; they do not grant authority or define deployment exposure.
- `x-dubnium-visibility: operator` marks operations that belong behind a trusted administrative boundary.
- `x-dubnium-canonical-source` records the implementation repository, source paths, and reviewed commit.
- Alpha bindings intentionally leave private implementation semantics open. In particular, memory ranking/scoring and scheduler persistence, backpressure, concurrency, retry, and policy behavior are not standardized here.
- The supervisor gateway is an OpenAI-compatible subset, not a claim of compatibility with every OpenAI API parameter or endpoint.
