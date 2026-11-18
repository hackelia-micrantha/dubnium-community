# Vision and Deployment Model

Dubnium's long-term direction is a family of reproducible engineering environments built from shared contracts rather than one machine that must perform every role.

## Why this direction matters

An engineering team may need consistent developer endpoints, private inference, isolated build resources or automation that respects the same approval constraints as human operators. It should not have to adopt every Dubnium component to evaluate one of those requirements.

The project therefore separates the environments where people work from the resources that perform builds or automation. The intended benefits are easier replacement, clearer responsibility boundaries and integration without a mandatory central stack. These are design goals to validate with real users, not measured savings or promises of a released commercial product.

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

## Layered execution environments

Different workloads need different isolation boundaries. Technology families to evaluate or compose include Incus-managed virtual machines or containers, NixOS environments and containers, Podman containers, and Nono-style process-level sandboxing for agent tools. Declarative packaging, container isolation, virtual-machine isolation and restrictions on individual tool processes solve different problems.

Select the weakest sufficient boundary for the workload's threat model, and qualify actual filesystem, network, credential and resource restrictions. None of these technologies is by itself a universal containment guarantee. Integration completeness and operational qualification vary; this is a description of design options, not a live deployment inventory.

## Private connectivity and edge networking

Private service access can use encrypted overlay networking, including Tailscale-compatible networks and optional self-managed coordination through Headscale. The direction also includes OpenWrt-based edge and exit-node integration for controlled Internet egress. See [Governance and Safety](governance.md) for the public-network threat model and limitations.

Private reachability is complementary to application authentication and capability authorization. It is not a substitute for either, and does not automatically grant access to a local network. Router recovery, exit-node behavior and client qualification must be established before a deployment is described as supported.

## Virtual appliance distribution

An experimental QCOW2 client-image direction explores replaceable VM environments and independent writable state. Reproducible image output, lifecycle and recovery qualification are still required before a released appliance can be claimed.

Cloud distribution is a separate later possibility, including an AWS-compatible AMI target. QCOW2 is a virtual-disk format, not a claim of a native AWS release; cloud image preparation, security, supply-chain verification and demand must be assessed independently. There is no current commitment to a published cloud appliance or marketplace listing.

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
