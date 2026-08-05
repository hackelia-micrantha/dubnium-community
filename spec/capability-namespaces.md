# Capability namespace registry

Status: v1alpha
Content: normative
Canonical source: this file
Generated: no

## Purpose

Capability names identify stable governed effects. They are not transport routes, package names, executable paths, user-facing labels, or evidence that a provider is installed or authorized.

## Syntax

A capability name MUST match:

```text
^[a-z][a-z0-9]*(\.[a-z][a-z0-9-]*)+$
```

Names are lowercase and case-sensitive. A Gateway or provider MUST NOT substitute an alias after authorization.

## Reserved namespaces

| Namespace | Owner | V1alpha status |
| --- | --- | --- |
| `example.*` | Dubnium Community | Synthetic no-effect examples and conformance |
| `deployment.*` | Private Dubnium deployment capability owner | `deployment.apply` synthetic naming fixture only |
| `dubnium.*` | Dubnium project | Reserved; requires explicit public governance decision |
| `anthesis.*` | Anthesis project | Reserved; this repository does not allocate Anthesis effects |
| `system.*` | Reserved | Prohibited for external allocation |
| `service.*` | Reserved | Deferred |
| `backup.*` | Reserved | Deferred |
| `storage.*` | Reserved | Deferred |
| `scheduler.*` | Reserved | Deferred |
| `github.*` | Reserved | Deferred and not affiliated with GitHub |
| `git.*` | Reserved | Deferred |

The executable public reference capability is:

```text
example.noop
```

The initial synthetic production-effect name is:

```text
deployment.apply
```

`deployment.request` MUST NOT be registered because request submission is a Gateway operation, not the governed deployment effect.

## External namespaces

External projects SHOULD use a reverse-domain namespace they control, for example:

```text
com.example.noop
```

A public name claim MUST identify the owner, effect semantics, payload schema authority, compatibility policy, and security boundary. Repository acceptance does not confer certification, endorsement, provider admission, or runtime authority.

## Extensions

V1alpha has no field extension mechanism. Ad hoc `x-*` fields and undeclared `extensions` objects MUST be rejected as unknown fields.

A future extension mechanism MUST use explicit namespace ownership and define authorization, canonicalization, compatibility, and unknown-extension behavior before publication.

## Compatibility

Renaming, transferring, reusing, or materially changing the effect semantics of a published capability name is breaking. A materially different effect MUST receive a new name or schema version.
