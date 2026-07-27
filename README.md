# Dubnium

**Micrantha's reproducible, local-first distribution for agentic software development and operations.**

Dubnium combines an opinionated NixOS system with local and cloud model routing, development environments, workflow automation, bounded tool execution, and governance-aware operational controls.

It asks a practical systems question:

> How should a developer workstation behave when it is also an AI runtime, automation host, build environment, and governed operations surface?

## Product role

Dubnium is an **incubating Micrantha Solution** rather than a general-purpose Linux distribution. NixOS provides the reproducible operating-system foundation, while the product boundary is the integrated agentic development and operations environment built on top of it.

Dubnium is intended to provide:

- rebuildable workstation, compute, and automation profiles;
- explicit operating modes and resource ownership;
- local-first inference with controlled provider fallback;
- model and workload routing;
- repository-scoped agent workflows;
- reproducible development environments and self-hosted CI runners;
- governed automation and bounded execution;
- secrets, observability, provenance, and evidence boundaries.

## Agentic architecture

Dubnium separates planning and orchestration from authorization authority:

```text
operator or workflow
        |
        v
Dubnium agentic runtime
        |
        v
Anthesis policy decision
        |
        +---- deny ----------------------> evidence
        |
        +---- approval required --------> approval gate
        |
        +---- allow / approved ----------> bounded executor
                                              |
                                              v
                                      diff + run evidence
```

- **Dubnium** owns agent runtime composition, planning intake, routing, bounded execution, and host-level operational controls.
- **Anthesis** owns deterministic governance decisions, policy attribution, approval requirements, provenance, and governance contracts.
- **Anthesis Governance Lab** independently tests the public governance contract, canonical scenarios, and evaluator compatibility.
- The **Dubnium Governed Agent Demo** exercises that public contract and evaluator boundary through the bounded execution path without treating the agent or model as its own authorization authority.

## Public testbed

The current integration consumes the public Governance Lab contract and immutable evaluator releases from [anthesis-community](https://github.com/hackelia-micrantha/anthesis-community). The independent [Anthesis Governance Lab](https://github.com/ryjen/anthesis-governance-lab) repository validates the same boundary through canonical and adversarial scenarios; Dubnium does not require direct access to its fixture tree.

The testbed demonstrates:

- structured agent plans;
- deterministic `allow`, `approval_required`, and `deny` decisions;
- exact approval binding;
- a capability-bounded executor;
- protected-path and synthetic-secret denial;
- sanitized diffs and evidence bundles;
- fail-closed evaluator identity and contract checks.

It is a functioning integration slice, not yet a claim of complete production sandboxing, durable approvals, or generalized autonomous orchestration.

## Repository boundaries

This repository is the public community and distribution boundary for Dubnium.

Some implementation and reference-integration work currently remains under [`ryjen`](https://github.com/ryjen) while ownership is consolidated into the Micrantha organization. Public documentation intentionally describes product direction, architectural contracts, and supported integration surfaces without exposing trusted-operator configuration or machine-specific secrets.

Related projects:

- [Micrantha organization profile](https://github.com/hackelia-micrantha)
- [Anthesis public contracts and releases](https://github.com/hackelia-micrantha/anthesis-community)
- [Anthesis Governance Lab](https://github.com/ryjen/anthesis-governance-lab)

## Status

Dubnium is **Incubating**. The workstation, AI runtime, automation, and governed-agent capabilities are being integrated behind explicit support tiers and trust boundaries. Interfaces may still evolve as the public distribution contract is stabilized.
