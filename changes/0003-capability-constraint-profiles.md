# Capability-specific constraint profiles

Status: v1alpha  
Compatibility: compatible  
Contracts: `spec/capability-gateway-v1.md`, Capability Gateway v1alpha conformance API

## Behavior

Capability Gateway v1alpha now explicitly permits a runtime or conformance consumer to supply a trusted deterministic constraint-profile registry keyed by the exact `(capability.name, capability.schema_version)` pair.

The default public conformance behavior is unchanged: only `example.noop` has a built-in non-empty constraint profile. A non-empty requested or granted constraint object for another capability still fails closed unless the consumer explicitly configures a profile for that exact capability/schema identity.

A configured profile validates and normalizes requested constraints and independently validates that granted constraints are equal to or narrower than the normalized request. Requested constraints continue to participate in canonical request identity and digesting.

No request, manifest, or other wire field is added. Existing generic JSON-object schema bounds remain unchanged.

## Security and authority

Constraint profiles are trusted runtime/conformance configuration, not caller data. A request cannot select a validator, schema URL, Python module, executable, or profile implementation. The public conformance implementation performs no dynamic code loading or remote schema resolution for profiles.

The same exact profile set must be used for request normalization, digesting, idempotency binding, and authorized-manifest validation. Profiles are capability/schema-specific and cannot silently override the built-in `example.noop` profile through registry extension.

Profile outputs are revalidated against the restricted JSON value profile before they become normalized contract data. Missing or mismatched profiles fail closed. Granted constraints cannot widen requested authority according to the selected profile's semantics.

Registering a constraint profile does not allocate a capability namespace, admit a provider, authenticate a caller, install policy, or authorize an effect.

## Migration

No migration is required for consumers using the default conformance API. Their accepted inputs, normalized representations, and digests remain unchanged.

Consumers that need additional capability-specific constraints may construct an explicit immutable `ConstraintProfileRegistry` and pass the same registry to request normalization/digesting, idempotency state, and manifest validation.

Conformance claims using additional profiles must identify the exact profile set and must not claim equivalence with the default-profile acceptance surface.

## Evidence

- `tests/test_constraint_profiles_v1.py` covers default fail-closed behavior, exact capability binding, digest participation, equal/narrow grants, widening rejection, unknown fields, profile-bound idempotency, built-in override rejection, and restricted-value revalidation.
- Existing Capability Gateway fixture tests remain unchanged and continue to validate `example.noop` canonical bytes/digests.
- `examples/capability-gateway-v1/constraint-profile.py` demonstrates a synthetic local profile without registering a provider or real effect.
- The wire schemas require no change because requested/granted constraints are already bounded generic JSON objects with the `example.noop` specialization layered on top.

## Private boundary

Production capability names, provider implementations, policy thresholds, host resource values, model-training recipes, deployment semantics, topology, credentials, and operational evidence remain outside this public change. Private consumers may register profiles through the public deterministic interface without publishing those operational details here.
