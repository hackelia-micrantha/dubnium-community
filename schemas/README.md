# Schemas

Status: experimental
Content: informative
Canonical source: this file
Generated: no

`schemas/` contains canonical machine-readable schema source.

Each schema has one editable owner, stable `$id` and version metadata, bounded local reference resolution, positive and negative examples, and an explicit relationship to generated types. Generated copies are not independently editable.

Remote schema resolution is disabled by default.

## Schema lines

- `schemas/v1/` contains the Capability Gateway v1alpha schema set.
- `schemas/v1alpha/memory-service.schema.json` contains the experimental memory-service example and payload schemas.
- `schemas/v1alpha/supervisor-gateway.schema.json` contains the experimental supervisor/LLM gateway schemas.
- `schemas/v1alpha/scheduler.schema.json` contains the experimental scheduler schemas.

Service schemas are validated with their positive and negative examples through the generic bundle catalog in `conformance/service-bundles.json`.
