# Governed agent execution: public reference

Status: experimental
Content: informative
Canonical source: this file
Generated: no

## Purpose

Dubnium is a reference execution environment for agentic workflows that consume an Anthesis governance decision before producing a consequential effect. Anthesis owns policy and approval semantics; Dubnium can constrain the tools and capabilities available to an agent and record execution outcomes. This document explains the **public integration boundary**, not a production installation procedure or a publication of private runtime implementation.

For an **executable, public trial**, use the [Anthesis reference trial](https://github.com/hackelia-micrantha/anthesis-community/blob/main/docs/product/try-anthesis.md). It uses the public Governance Lab and a separate, disposable constrained tool-wrapper harness. **That trial is not the Dubnium runtime.** A public, independently runnable Dubnium governed-agent distribution is not provided by this document.

## Conceptual walkthrough

```text
agent proposes an exact consequential effect
    -> Anthesis evaluates policy, identity, scope, and approval requirements
    -> integration checks the decision against the exact requested effect
    -> bounded runtime permits the authorized effect or blocks it
    -> outcome and evidence are recorded for inspection
```

An agent's intent is not authority. The governance decision is not itself enforcement: the surrounding integration must prevent the agent from reaching the same effect through an ungoverned tool, credential, network path, or privileged caller. A successful public decision-contract test alone cannot establish that an arbitrary external runtime has removed all bypass paths.

## Questions for an integrator

1. **Exact effect:** What action, target, actor, and scope does the decision authorize?
2. **Enforcement point:** Which tool, gateway, downstream validator, or runtime rejects the effect unless the authorization matches?
3. **Approvals:** If approval is required, is execution blocked until an approval for that exact effect is verified?
4. **Alternate paths:** Can the agent still reach a raw tool, direct API, credential, shell, or another executor for the same effect?
5. **Evidence:** Can a reviewer connect the requested action, decision, approval when applicable, attempted execution, and observed outcome?
6. **Negative test:** Does an unauthorized or out-of-scope request fail at the execution boundary without producing the effect?

For integration-specific controls and residual trust assumptions, see the [Anthesis integration modes](https://github.com/hackelia-micrantha/anthesis-community/blob/main/docs/product/integrations/README.md) and [trial criteria](https://github.com/hackelia-micrantha/anthesis-community/blob/main/docs/product/trial-criteria.md).

## A public trial you can run

The [Try Anthesis walkthrough](https://github.com/hackelia-micrantha/anthesis-community/blob/main/docs/product/try-anthesis.md) supplies a disposable repository-write example. The example evaluates an exact write, executes it through a deliberately constrained tool registry, and tests a raw-tool and out-of-scope bypass. Inspect its recorded decision, repository diff, denial reasons, and before/after state.

It demonstrates enforcement **within that reference composition**, not containment of a hostile local user or a different agent runtime that retains direct effect access. It does not establish production assurance for a Dubnium deployment.

## What Dubnium contributes

Dubnium's role in the overall design is the **execution-side boundary**: expose bounded capabilities, enforce the decision for the intended effect, and return observable outcomes and evidence. It does not independently define Anthesis policy authority, and integrating Anthesis does not make unrelated Dubnium or third-party effect paths governed.

The [Dubnium governance overview](external/governance.md) describes this responsibility split. The [Anthesis public product overview](https://github.com/hackelia-micrantha/anthesis-community/blob/main/docs/product/overview.md) explains why Dubnium is one reference integration, not a prerequisite for adopting Anthesis.

## Maturity and publication boundary

This is a conceptual, informative public reference. It contains no private execution commands, implementation paths, host topology, policy rules, operational evidence, or privileged controls. The public runnable example is hosted in the Anthesis Governance Lab; a separate Dubnium demonstration must be evaluated on its own runtime and bypass assumptions before making an enforcement claim.

For more detail, consult [Dubnium's publication boundary](../PUBLICATION_BOUNDARY.md) and [community engagement](../COMMUNITY_ENGAGEMENT.md).
