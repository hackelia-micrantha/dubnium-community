# Vision and Deployment Model

Dubnium's long-term direction is a family of reproducible engineering environments built from shared contracts rather than one machine that must perform every role.

## Product shape

```text
Dubnium
├── Client environment / VM
│   └── small, replaceable development and access environment
├── Workstation
│   └── interactive environment with richer local device or compute access
├── Build / compute node
│   └── bounded non-interactive build, CI, cache, or compute capacity
├── Remote managed environment
│   └── sensitive work kept on infrastructure with an appropriate trust boundary
└── Security / administrative environment
    └── stronger isolation and access controls selected by threat model
```

These are deployment compositions, not identities or permission levels. A deployment should enable only the services and capabilities justified by its use case.

## Why a smaller client environment matters

A small managed VM can make project setup, replacement, credential cleanup, and offboarding easier without forcing the user's entire physical machine into one configuration model. It can also give teams a consistent development substrate while leaving heavyweight build, AI, or infrastructure workloads elsewhere.

A VM on an unmanaged physical host is **not** a confidentiality boundary against that host. If the host itself is outside the trust model, sensitive source, data, or credentials may require a managed endpoint or remote execution environment instead of stronger claims about the guest.

## Identity, posture, and authority stay separate

The architecture intentionally distinguishes:

```text
network reachable
identity authenticated
endpoint posture known
operation authorized
```

Each can inform policy, but one should not silently stand in for another.

## Local operation remains important

Central inventory, observability, policy distribution, or remote services may be useful for larger deployments. They should extend local behavior rather than becoming the only way to inspect, diagnose, or recover an endpoint.

## Direction, not a support claim

This page describes a public architectural direction. It does not claim that every deployment form, fleet function, identity system, or remote environment is currently implemented or generally available.
