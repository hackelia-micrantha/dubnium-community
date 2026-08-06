# Repository layout and dependency rules

Status: stable
Content: normative
Canonical source: this file
Generated: no

## Dependency direction

```text
spec/ and schemas/
  -> generated public types and API bindings
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

### `changes/`

Reviewed contract-change records. A normative contract, schema, or API change MUST add a record describing compatibility, security, authority, migration, evidence, and the private boundary. Records feed release notes but do not replace them.

### `packages/`

Thin public validators, clients, and authoring libraries. Packages MUST be usable without private services and MUST NOT embed production orchestration, policy, privileged dispatch, host topology, or operator configuration.

### `conformance/`

Implementation-neutral suites and synthetic fixtures. Test targets are explicit and remote targets are disabled by default. Conformance assets MUST be able to test an implementation other than the bundled reference.

HTTP contract bundles SHOULD be catalogued in `conformance/service-bundles.json` and validated by the generic `conformance.contract_bundle` module. Catalog entries MUST remain data-only and MUST NOT select arbitrary Python hooks.

A contract-specific executable MAY exist only when required semantics cannot be expressed through schemas, examples, and declarative assertions. Common parsing, resource limits, reference resolution, fixture discovery, and reporting MUST be shared rather than copied into per-API scripts.

### `reference/`

Minimal, deliberately non-production implementations. References use no real credentials, privileged effects, host control, production policy, or reusable privileged dispatch path.

### `examples/`

Synthetic examples only. Examples MUST NOT contain real identities, repositories, hosts, endpoints, incidents, logs, evidence, prompts, approvals, or operational measurements.

### `policy-examples/`

Illustrative, synthetic policy material. It is non-authoritative and MUST NOT be presented as Anthesis policy, production Dubnium policy, or a safe default for deployment.

### `release/`

Reviewed deterministic bundle and manifest tooling. It remains inactive until a real contract bundle exists. Release jobs MUST NOT publish empty scaffolding, private provenance, credentials, or private implementation.

### `docs/`

Architecture and process documentation. Normative policy files identify themselves explicitly. Documentation may describe boundaries but should minimize private coordinates and operational detail.

### `site/`

Generated publication output. `site/` is never canonical source for specifications, schemas, compatibility rules, or policy. Generated paths are reviewed and validated independently.

## Scripts and reusable tooling

`scripts/` is reserved for repository-wide operational entry points such as publication, release, policy, workflow, and whole-tree validation.

Contract or API behavior MUST NOT be implemented as a new script by default. Reusable validation belongs in a package or `conformance/` module, while API-specific variation belongs in schemas, fixtures, examples, and catalogs.

A script added to support one API MUST be generalized before merge or explicitly justified as irreducibly contract-specific.

## Private extensions

Private consumers may use namespaced extensions behind adapters. Extensions cannot weaken public requirements, widen authority or effects, or claim public conformance for non-public behavior.

## Imports and vendoring

Private-to-public material is imported as a clean reviewed artifact, not by making private Git history public. Public-to-private consumption uses an immutable public release or commit, exact artifact digest, and available provenance. Vendored private copies of public schemas are generated or mechanically synchronized and are not canonical.

## Architecture enforcement

The always-running Contract CI gate validates repository policy, workflow trust boundaries, JSON resource limits and duplicate keys, bundled references, contract markers, OpenAPI JSON, examples, change records, generic contract bundles, and validator tests. Release activation and repository settings remain separately tracked where they require a real bundle or administrative access.
