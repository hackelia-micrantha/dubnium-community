# Schemas

Status: experimental
Content: informative
Canonical source: this file
Generated: no

`schemas/` contains canonical machine-readable contract shapes.

A public wire shape has one editable schema owner. OpenAPI components SHOULD reference the canonical definition directly. When duplication is unavoidable, the bundle catalog MUST declare a structural binding and generic conformance MUST reject drift.

Schema documents use JSON Schema 2020-12, local reviewed references, stable `$id` values, bounded files, and no remote resolution.

The experimental memory, supervisor, and scheduler schemas are under `schemas/v1alpha/`.
