# Dubnium Technical Overview

Dubnium is a reproducible, observable, governed engineering environment for developer workstations, smaller client environments, build and compute nodes, and AI-assisted automation.

Within Micrantha, Dubnium serves as the **canary implementation for the wider development and VM ecosystem**: it integrates and exercises NixOS, VM, runtime, and automation patterns before broader reuse.

This technical overview explains the system through **responsibilities, state models, invariants, observable behavior, and published interoperability contracts**. It is intentionally more detailed than the landing page while stopping before deployment-sensitive implementation and operator material.

## What Dubnium is trying to preserve

The project is built around four system qualities:

- **reproducibility** — environments can be rebuilt, replaced, and reviewed from declared inputs;
- **observability** — intended state and observed runtime state remain distinct and explainable from bounded evidence;
- **security** — connectivity, identity, capabilities, and automated effects remain explicit rather than ambient;
- **development acceleration** — project environments, builds, automation, and AI support reduce setup and recovery cost without making the workstation fragile.

Dubnium is local-first, not local-only. A useful endpoint should remain inspectable and recoverable without depending on a central control plane while still being able to consume remote services through explicit contracts and policy boundaries.

## Deployment is compositional

Dubnium is not limited to one workstation shape. The same architectural contracts can support smaller client environments, richer interactive workstations, build or compute nodes, remote managed development environments, and stronger security or administrative environments. Each deployment enables only the capabilities it needs.

AI is one capability of the environment, not the authority for the environment. Deterministic configuration, runtime observation, policy, durable state, and recovery remain useful without a model.

## Start with the system flow

- [How Dubnium Works](how-dubnium-works.md) gives the end-to-end mental model from declared intent through runtime observation and governed effects.
- [Operator Journey](operator-journey.md) shows how the public operator surfaces fit together without exposing deployment-specific procedures.
- [Self-Hosted CI Runner Controller](runner-controller.md) explains bounded admission, short-lived workers, canonical status, and reconciliation.

Then inspect the implemented surfaces:

- [Components](components.md) describes the major platform pieces, their maturity, state ownership, and intentional boundaries.
- [Operator Tooling](operator-tooling.md) explains why `dubctl`, `modectl`, and `configctl` remain separate surfaces.
- [Runtime Operating Modes](runtime-modes.md) describes desktop, media, and compute posture and the guarded reconciliation model.
- [Writable User Configuration](writable-configuration.md) explains how legitimate mutable preferences coexist with Nix-store-backed managed configuration.

Then continue into the broader design:

- [Vision and Deployment Model](vision.md) describes the long-term product shape.
- [Conceptual Architecture](architecture.md) describes responsibility and source-of-truth boundaries.
- [Reproducible Engineering](reproducibility.md) covers replacement, project environments, mutable-state classification, and supply-chain trust.
- [Observability and Evidence](observability.md) separates intended state, runtime facts, durable state, and derived understanding.
- [AI and Automation](ai-and-automation.md) explains how model-assisted work fits without becoming ambient authority.
- [Governance and Safety](governance.md) describes bounded effects and trust boundaries.
- [Contracts and Conformance](public-contracts.md) describes the independently inspectable interoperability surface.
- [Status and Direction](status.md) distinguishes implemented, experimental, and directional work.
- [Community and Contributions](community.md) points to the open source and contribution surface.

## Disclosure boundary

The useful rule for this overview is:

> Publish what the system promises and what an integrator or operator can observe; keep private how a particular deployment enforces it.

This overview may therefore publish stable component names, maturity, operator-tool responsibilities, runtime-mode semantics, configuration ownership layers, state-machine invariants, conceptual control flow, and published contracts.

It deliberately omits machine identities, exact topology, ports/endpoints, service-unit wiring, credentials, hardware/resource assignments, exact policy thresholds, trusted identities, provider-selection or model-routing heuristics, privileged recovery procedures, private prompts/data, and real operational evidence.

The published Community repository is independently useful for contracts, conformance, references, and documentation. This technical overview is not a sanitized mirror of private operator documentation.
