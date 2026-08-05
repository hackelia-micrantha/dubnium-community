# Contract change records

Status: stable
Content: normative
Canonical source: this file
Generated: no

A pull request that changes normative content under `spec/`, canonical JSON under `schemas/`, or transport bindings under `api/` MUST add a Markdown record under `changes/`.

File name format:

```text
NNNN-short-description.md
```

A record contains:

```text
# Change title

Status: experimental | v1alpha | v1beta | stable
Compatibility: compatible | breaking | security-hardening
Contracts: paths or contract identifiers

## Behavior

Normative behavior added, changed, clarified, or removed.

## Security and authority

Identity, parsing, replay, canonicalization, effects, constraints, policy-authority, and failure implications.

## Migration

Consumer and generated-artifact changes, deprecation window, or explanation that no migration is required.

## Evidence

Schemas, examples, positive/negative/adversarial fixtures, conformance tests, and consumer validation.

## Private boundary

Implementation, policy, data, topology, or operational details that remain private.
```

Change records are reviewed release inputs. They do not replace release notes or compatibility policy.
