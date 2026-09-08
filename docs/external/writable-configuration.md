# Writable User Configuration

NixOS and Home Manager make managed configuration reproducible, and many managed files are materialized from immutable Nix-store content. Those files should be regenerated rather than edited in place.

That does **not** mean the user environment is globally read-only.

Dubnium keeps an explicit writable boundary for application preferences, machine-specific choices, and first-run state that legitimately changes outside a system rebuild. `configctl` makes ownership and drift visible so mutable user state does not become undocumented configuration history.

## Layer model

| Layer | Ownership | Intended use |
| --- | --- | --- |
| **Managed** | Declarative configuration | Reviewed defaults and portable configuration; regenerated rather than edited in place |
| **Local** | User / machine | Machine-specific overrides that should remain local |
| **Custom** | User | Writable fragments that may be useful enough to review and promote |
| **Adopted** | Reconciliation history | Fragments already represented by managed configuration and no longer loaded as independent overrides |

The names describe ownership, not trust level. A writable fragment does not automatically become managed merely because it works locally.

## `configctl` responsibility

`configctl` provides a generic reconciliation surface around those layers. Its useful operator vocabulary includes:

| Surface | Responsibility |
| --- | --- |
| `status` | Show which configuration layers exist and where unpromoted state remains |
| `adopt` | Establish the expected writable layer structure for a supported tool |
| `promote` | Move a useful custom fragment into a reviewable declarative path |
| `reconcile` | Report drift between local writable state and managed configuration |
| `doctor` | Check that the reconciliation environment and contracts are healthy |
| `init` | Handle bounded first-run state that cannot be represented by declaring a static file alone |

This is an ownership workflow, not an attempt to make every application configuration format identical.

## Promotion rather than mutation

A portable preference can begin as a writable local/custom change. `configctl` can identify that the change is outside the managed layer and help move it into review. Once the reviewed declarative configuration represents the same intent, a rebuild can make it part of the managed default and the independent custom fragment no longer needs to carry authority.

That gives Dubnium both properties at once:

- managed defaults remain reproducible and reviewable;
- legitimate application and user preferences still have an explicit writable home.

## First-run mutable state

Some tools need initialization rather than a static configuration file. `configctl` supports explicit first-run contracts so these changes are inspectable and risk-gated rather than hidden in shell startup, installer side effects, or ad-hoc bootstrap scripts.

The technical overview intentionally describes the contract shape, not tool-specific mutable paths or operational procedures.

## Security boundary

Writable configuration is not an escape hatch from host policy. `configctl` does not grant authority over:

- secrets or credentials;
- privileged system state;
- service authorization;
- host security policy;
- deployment topology;
- governed effects.

Those concerns remain with their own declarative, runtime, secret-management, and governance boundaries.