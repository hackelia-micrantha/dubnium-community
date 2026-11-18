# Dubnium Technical Overview

Dubnium explores how reproducible development environments, self-hosted infrastructure and local-first AI can support secure, accountable engineering automation. Built on NixOS, it is intended to make development, build and execution environments easier to replace, inspect and trust.

This overview is for engineers evaluating the design, organizations considering integration, and contributors who want to challenge or extend the public contracts. Dubnium is incubating: a personal engineering environment informs the design, and the first experimental Capability Gateway contract bundle is publicly available. A generally available workstation distribution or stable consumer compatibility baseline has not been established.

## Why it matters

Developer environments accumulate machine-specific dependencies and mutable state. Self-hosted builds need isolation and recoverability. AI-assisted tools can propose useful actions, but they may also inherit access to source, credentials or infrastructure beyond what a task requires.

Dubnium addresses these concerns through four complementary system qualities:

- **Reproducibility:** replace or recover environments from declared inputs instead of reconstructing undocumented manual changes.
- **Developer experience:** compose project tooling, local services and build capacity without making unrelated capabilities mandatory.
- **Security:** separate access, identity, policy, authorization and execution so that a request is not permission.
- **Observability:** distinguish intended state, actual behavior and the evidence needed to evaluate an outcome.

## Where the design could be useful

| Application | Problem being explored |
| --- | --- |
| Developer endpoints | Consistent setup, replacement and recovery across changing project requirements |
| Self-hosted CI | Short-lived job workers, scope-constrained execution and reliable reconciliation |
| Local and private AI | Useful model assistance while retaining explicit data and execution boundaries |
| Governed automation | Consequential actions that can be authorized, bounded and verified independently |

These are use cases to validate, not claims of enterprise availability or measured benefits. [Vision and Deployment Model](vision.md) explains the deployment assumptions and limitations.

## Explore the engineering

- **Product direction:** [Vision and Deployment Model](vision.md) and [Status and Direction](status.md).
- **System architecture:** [How Dubnium Works](how-dubnium-works.md), [Components](components.md) and [Conceptual Architecture](architecture.md).
- **Operator experience:** [Operator Journey](operator-journey.md), [Operator Tooling](operator-tooling.md) and [Self-Hosted CI Runner Controller](runner-controller.md).
- **Security and trust:** [Governance and Safety](governance.md), [AI and Automation](ai-and-automation.md) and [Observability and Evidence](observability.md).
- **Evaluate or contribute:** [Contracts and Conformance](public-contracts.md) and [Community and Contributions](community.md).

The [published alpha bundle](https://github.com/hackelia-micrantha/dubnium-community/releases/tag/contract-v0.1.0-alpha.1), [conformance suites](https://github.com/hackelia-micrantha/dubnium-community/tree/main/conformance), and [no-effect references](https://github.com/hackelia-micrantha/dubnium-community/tree/main/reference) are the public artifacts to examine first. The public repository requires no private implementation or credentials to exercise its contract fixtures.

## Scope of this overview

The overview describes observable system behavior, component responsibilities, design decisions and published interoperability commitments. It does not disclose deployment-specific implementation or operational evidence. See the [publication boundary](https://github.com/hackelia-micrantha/dubnium-community/blob/main/PUBLICATION_BOUNDARY.md) for the governing disclosure rules.

Within Micrantha, Dubnium serves as a reference and canary environment for validating shared NixOS, VM, runtime and automation patterns before broader reuse. The public Community repository is independently useful without access to the private environment.
