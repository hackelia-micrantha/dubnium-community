Status: v1alpha
Content: informative
Canonical source: changes/2026-08-05-capability-gateway-v1.md
Generated: no

# Capability Gateway v1alpha contract bundle

## Classification

- Contract change: additive initial v1alpha vertical slice.
- Compatibility: experimental; no prior portable contract is superseded.
- Disclosure: synthetic fixtures and no-effect implementation only.

## Added

- normative request, status, manifest, canonicalization, idempotency, narrowing, and compatibility rules;
- JSON Schemas for the portable v1 cutline;
- canonical request bytes and SHA-256 vector;
- positive and negative conformance fixtures;
- an offline standard-library conformance command;
- a deterministic no-effect provider example;
- unit and CI coverage.

## Boundary

The bundle contains no production authentication, policy, approval, host, deployment, credential, topology, or privileged-provider implementation.
