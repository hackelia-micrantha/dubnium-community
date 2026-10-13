# Truthful indeterminate status attribution

Status: v1alpha
Content: normative
Canonical source: this file
Generated: no
Compatibility: breaking
Contracts: spec/capability-gateway-v1.md, schemas/v1/capability-status.schema.json, conformance/gateway_envelope_core_v1.py

## Behavior

Pre-dispatch indeterminate status does not invent a provider operation. It carries the mandatory request identity, digest and bounded error. Post-dispatch indeterminate status carries the original immutable provider operation. Transition checks reject losing an existing provider identity. Isolated indeterminate documents permit either shape because they lack history.

## Security and authority

No private gateway stage or provider operation is exposed when none exists. A verifier with history MUST enforce provider-operation presence after dispatch. The schema cannot prove temporal history.

## Migration

The v1alpha schema now admits a new status form; previously hard-required provider_operation consumers must update their indeterminate parser. Producers must cease inserting non-provider identities into provider_operation. Treat as compatibility-sensitive/breaking even though older valid post-dispatch documents remain accepted.

## Evidence

Positive synthetic conformance examples cover policy failure, invalid manifest, restart before dispatch, and restart after dispatch. Transition tests enforce provider-reference persistence.

## Private boundary

No runtime, policy implementation, topology, credentials, or downstream consumer identifiers are published.
