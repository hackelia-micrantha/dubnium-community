# Community Engagement Plan

Status: experimental  
Content: informative

## Purpose

Use community participation to improve Dubnium's public contracts, documentation, reproducibility, threat models, and usability. Community activity should produce technically useful artifacts and external feedback rather than function as an advertising channel.

## Principles

- Lead with reusable technical content.
- Ask for criticism, reproducibility feedback, and interoperability gaps.
- Do not imply endorsement by a user group, foundation, employer, customer, or contributor.
- Keep private implementation, customer information, operational topology, pricing, and unpublished roadmap details outside public material.
- Prefer one substantial artifact or event per month over a high-volume content cadence.
- Convert feedback into public issues only when it is safe, generalizable, and appropriate for the public product boundary.

## Initial audiences

Useful audiences include:

- Linux and NixOS users;
- platform and developer-experience engineers;
- application/product security engineers;
- self-hosters operating local AI or CI infrastructure;
- engineers evaluating agent/tool interoperability and least-privilege execution.

## Talk and workshop candidates

### Building a reproducible local AI engineering workstation on NixOS

Audience outcome:

- understand the difference between reproducibility, isolation, and authorization;
- see how a workstation can declare AI/runtime dependencies without making them boot-critical;
- learn practical recovery and diagnostic patterns;
- reproduce a public-safe reference slice.

### Secure capability execution for AI agents on Linux

Audience outcome:

- distinguish model reasoning from effect authority;
- understand typed intent, deterministic validation, policy decisions, and bounded providers;
- examine failure-closed behavior and adversarial cases;
- identify where ordinary agent frameworks tend to over-grant authority.

### Self-hosted CI without turning the workstation into a privileged runner

Audience outcome:

- understand long-lived versus transient runner risks;
- examine credential, storage, network, cgroup, and cleanup boundaries;
- compare warm workers with bounded one-job execution;
- apply the same isolation reasoning to other local automation.

### Why local AI still needs governance

Audience outcome:

- separate data locality from authorization;
- understand how local models can still misuse credentials, files, tools, or infrastructure;
- discuss evidence, approvals, provenance, and safe failure semantics.

## Twelve-month cadence

The calendar is intentionally lightweight and may shift based on external interest and project maturity.

| Month | Primary artifact or event | Evidence to collect |
| --- | --- | --- |
| 1 | Reproducible local-AI workstation talk/demo | install/reproduction failures, questions, missing docs |
| 2 | Publish demo cleanup and troubleshooting improvements | external successful reproductions |
| 3 | Capability/effect-boundary article or workshop | authority-model confusion, contract feedback |
| 4 | Public threat-model review | missing threats, unclear assumptions |
| 5 | CI/runner isolation talk or lab | operational constraints and portability feedback |
| 6 | Contributor/documentation improvement month | contributor friction and issue quality |
| 7 | Public compatibility/conformance walkthrough | independent implementation questions |
| 8 | Local-AI governance discussion/workshop | governance and evidence requirements |
| 9 | Reproducible project-environment case study | onboarding/build/recovery feedback |
| 10 | Security/recovery exercise | failure-mode and runbook gaps |
| 11 | Design-partner findings synthesis using only sanitized recurring themes | repeated requirements, rejected assumptions |
| 12 | Public roadmap and community-boundary review | adoption quality, maintenance cost, next-year priorities |

Do not publish an artifact merely to satisfy the calendar. Skip or replace an item when there is no technically useful content ready for review.

## Funnel

Community engagement may lead to deeper participation, but each stage should stand on its own:

```text
awareness
-> technical engagement
-> reproducible evaluation
-> contributor or design-partner conversation
-> supported/commercial discussion outside the public repository
```

Public participation never requires a commercial relationship.

## Useful metrics

Prefer:

- successful independent reproductions;
- concrete bug/compatibility reports;
- conformance feedback;
- high-quality contributions;
- repeat attendees or implementers who can describe the architecture accurately;
- recurring deployment/security requirements reported independently.

Avoid optimizing primarily for stars, follower counts, impressions, or event attendance.

## Publication safety

Before publishing slides, demos, examples, recordings, or derived findings, apply the repository publication and disclosure rules. Use synthetic examples. Remove private topology, identities, customer information, credentials, logs, policy thresholds, and private roadmap material.
