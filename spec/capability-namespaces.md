# Capability namespace registry

Status: experimental
Content: normative
Canonical source: this file
Generated: no

## Purpose

Capability names are stable governed-effect identifiers. They are not package names, transport routes, human labels, executable paths, or proof that a provider exists.

## Syntax

A capability name MUST match:

```text
^[a-z][a-z0-9-]*(\.[a-z][a-z0-9-]*)+$
```

Names are case-sensitive and lowercase only. Aliases MUST NOT be substituted after authorization.

## Reserved namespaces

| Namespace | Owner | Public v1 use |
| --- | --- | --- |
| `example.*` | Dubnium Community | Synthetic, no-effect examples and conformance only |
| `deployment.*` | Private Dubnium deployment capability owner | Synthetic `deployment.apply` fixture only; no public production implementation |
| `dubnium.*` | Dubnium project | Reserved; requires explicit public governance decision |
| `anthesis.*` | Anthesis project | Reserved; this repository does not assign Anthesis effects |
| `system.*` | Reserved | Prohibited for external allocation |
| `service.*` | Reserved | Deferred |
| `backup.*` | Reserved | Deferred |
| `storage.*` | Reserved | Deferred |
| `scheduler.*` | Reserved | Deferred |
| `github.*` | Reserved | Deferred and not affiliated with GitHub |
| `git.*` | Reserved | Deferred |

The only executable public reference capability in v1 is:

```text
example.echo
```

The initial synthetic production-effect name is:

```text
deployment.apply
```

`deployment.request` MUST NOT be registered because request submission is a Gateway operation rather than a governed effect.

## External namespaces

External projects SHOULD use a reverse-domain namespace they control, for example:

```text
com.example.echo
```

A name claim MUST identify the owner, intended effect, payload schema authority, compatibility policy, and security boundary. Repository acceptance of a name is not certification or runtime admission.

## Extensions

V1 has no field extension mechanism. Future extensions MUST use an explicit namespaced `extensions` object. Ad hoc `x-*` fields are prohibited because unknown fields fail closed and all digest-bearing fields require exact canonical semantics.

## Changes

Renaming, transferring, reusing, or changing the semantic effect of a published capability name is breaking. A materially different effect MUST receive a new capability name or schema version.
