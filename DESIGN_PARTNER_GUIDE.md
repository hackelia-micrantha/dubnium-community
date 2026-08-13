# Design Partner Guide

Status: experimental  
Content: informative

## Purpose

Design partners help validate whether Dubnium's public interoperability model and broader engineering-environment direction address real deployment, reproducibility, security, and automation problems.

A design-partner conversation is not a promise of procurement, roadmap priority, support, certification, or commercial availability.

## Good fit

Useful participants often have one or more of these characteristics:

- local/private AI requirements;
- security-sensitive or regulated source/data;
- difficult-to-reproduce developer environments;
- self-hosted or security-sensitive CI/build infrastructure;
- autonomous developer tooling that needs bounded filesystem, network, credential, or effect authority;
- explicit audit/evidence requirements;
- interest in independent implementation or conformance with public Dubnium contracts.

## Intake topics

### Problem and workflow

- What engineering workflow is difficult, risky, slow, or expensive today?
- Who experiences the problem and who owns its resolution?
- What would a materially better outcome look like?
- Which current tools are involved?

### Trust boundaries

- What source/data is sensitive?
- Which endpoints are organization-managed versus BYOD?
- Which credentials or privileged operations are involved?
- What network/egress restrictions apply?
- What actions may AI tools or automation currently perform?

### Reproducibility and operations

- How are developer environments created and replaced?
- How long does onboarding/recovery take?
- Which project dependencies are machine-global or manually configured?
- Which failures are difficult to diagnose or recover from?

### AI and automation

- Which hosted/local models or agent tools are used?
- Which data may leave the organization?
- What tool, filesystem, process, network, and infrastructure authority is granted?
- Are consequential actions approved, attributable, and reversible?

### Evidence and governance

- Which decisions/actions need audit evidence?
- Who may approve higher-risk operations?
- What retention/privacy constraints apply?
- Which controls must remain useful when central infrastructure is unavailable?

### Commercial validation

Commercial discussions, budgets, pricing, contracts, procurement, and customer-specific deployment details belong in private channels, not public issues or this repository.

## What feedback is most useful

- reproducibility failures;
- unclear trust assumptions;
- public contract ambiguities;
- missing negative/adversarial cases;
- portability constraints;
- integration boundaries that are too broad or too narrow;
- recurring operational requirements;
- deployment models that do not match real organizations.

## Confidentiality and ownership

Do not submit confidential customer/employer information, credentials, private repository content, production topology, logs, incidents, policy thresholds, or proprietary source code to public Dubnium channels.

Before sharing non-public material, establish an appropriate private communication and confidentiality boundary.

Feedback does not automatically transfer ownership of pre-existing intellectual property. Contributions intended for this public repository must satisfy the repository's contribution, provenance, licensing, and sign-off requirements.

## Public issue extraction

When a private/design-partner finding is suitable for public tracking:

1. extract only the general technical problem;
2. remove identities and deployment-specific details;
3. replace real data/topology with synthetic examples;
4. avoid private pricing, roadmap, policy, incident, and security-sensitive material;
5. confirm that the resulting issue is useful without private context;
6. apply the publication/disclosure checklist before submission.

## Success criteria

A useful design-partner interaction should produce at least one of:

- a reproducible compatibility or documentation gap;
- a clearer threat-model assumption;
- a reusable requirement confirmed by more than one organization;
- an implementation-independent contract/conformance improvement;
- evidence that an assumed problem is not important enough to pursue.

The last outcome is valuable: design partnerships should reduce uncertainty, not merely validate an existing roadmap.
