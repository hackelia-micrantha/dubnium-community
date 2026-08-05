# Repository layout and dependency rules

Status: stable
Content: normative
Canonical source: this file
Generated: no

## Dependency direction

```text
spec/ and schemas/
  -> generated public types
    -> packages/, conformance/, reference/, and examples/
      -> external and private consumers
```

Dependencies MUST NOT point from public content into private Dubnium source, private repositories, private package registries, local filesystem paths, operator endpoints, credentials, production policy, or host configuration.

## Directory ownership

### `spec/`

Normative prose specifications. A specification may reference schemas and external standards, but MUST NOT import implementation packages or generated site artifacts.

### `schemas/`

Canonical machine-readable schema source. Each schema has one editable owner. Generated language types and bundled copies identify the schema version or digest and are not independently edited.

Remote schema resolution is disabled for conformance and release validation unless a contract explicitly defines a reviewed, pinned exception.

### `api/`

Transport bindings derived from normative contracts, such as OpenAPI descriptions. A binding cannot introduce authority, lifecycle, error, identity, canonicalization, or compatibility semantics absent from the normative specification.

### `packages/`

Thin public validators, clients, and authoring libraries. Packages MUST be usable without private services and MUST NOT embed production orchestration, policy, privileged dispatch, host topology, or operator configuration.

### `conformance/`

Implementation-neutral suites and synthetic fixtures. Test targets are explicit and remote targets are disabled by default. Conformance assets MUST be able to test an implementation other than the bundled reference.

### `reference/`

Minimal, deliberately non-production implementations. References use no real credentials, privileged effects, host control, production policy, or reusable privileged dispatch path.

### `examples/`

Synthetic examples only. Examples MUST NOT contain real identities, repositories, hosts, endpoints, incidents, logs, evidence, prompts, approvals, or operational measurements.

### `policy-examples/`

Illustrative, synthetic policy material. It is non-authoritative and MUST NOT be presented as Anthesis policy, production Dubnium policy, or a safe default for deployment.

### `docs/`

Architecture and process documentation. Normative policy files identify themselves explicitly. Documentation may describe boundaries but should minimize private coordinates and operational detail.

### `site/`

Generated publication output. `site/` is never canonical source for specifications, schemas, compatibility rules, or policy. Generated paths are reviewed and validated independently.

## Private extensions

Private consumers may use namespaced extensions behind adapters. Extensions cannot weaken public requirements, widen authority or effects, or claim public conformance for non-public behavior.

## Imports and vendoring

Private-to-public material is imported as a clean reviewed artifact, not by making private Git history public. Public-to-private consumption uses an immutable public release or commit, exact artifact digest, and available provenance. Vendored private copies of public schemas are generated or mechanically synchronized and are not canonical.

## Architecture enforcement

Repository policy CI performs lightweight checks for required policy files, prohibited dependency forms, symlinks, private/local runtime coordinates in public implementation paths, and canonical/generated markers. Contract-specific schema and conformance enforcement is added with the first contract slice and hardened under issue #14.
