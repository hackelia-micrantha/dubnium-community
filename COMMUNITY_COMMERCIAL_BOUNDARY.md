# Community and Commercial Boundary

Status: experimental  
Content: informative  
Canonical source: this file

## Purpose

Dubnium Community exists to provide independently useful public contracts, conformance assets, documentation, developer tooling, and safe reference implementations.

Commercial support or products may be built around the broader Dubnium ecosystem, but the existence of commercial work does not change the public repository's role or compatibility commitments.

## Community commitment

The community layer should remain useful without a paid service, private repository, private endpoint, or commercial account.

Public work may include:

- normative interoperability contracts and schemas;
- canonicalization, compatibility, and stable error semantics;
- synthetic positive, negative, and adversarial conformance fixtures;
- implementation-neutral conformance tooling;
- thin clients, validators, and authoring libraries;
- minimal no-effect reference implementations;
- public architecture and threat-model documentation;
- contribution, governance, compatibility, security, and release processes.

Commercialization must not intentionally make these assets incomplete or unreliable in order to force adoption of a paid implementation.

## Possible commercial value

Organizations may need operational capabilities beyond public interoperability assets. Examples can include:

- supported and validated distributions;
- managed endpoint or fleet administration;
- organization identity, policy, evidence, and compliance integrations;
- supported source-control, CI, VPN, identity, and security integrations;
- certified deployment or hardware profiles;
- curated capability bundles with tested runtime, evaluation, provenance, and support expectations;
- architecture reviews, deployment assistance, workshops, and support agreements;
- managed services where a stable public contract permits independent clients and implementations.

These are categories of possible commercial value, not availability, roadmap, pricing, certification, or support commitments.

## Interoperability rule

Where a public contract exists, commercial and private implementations should consume the same published compatibility boundary rather than requiring private knowledge to interpret public messages correctly.

A commercial implementation may provide additional private behavior behind that boundary, but it must not claim public conformance for undocumented extensions or reinterpret stable public semantics silently.

## Design-partner participation

Early adopters and design partners can help validate whether the public contracts and broader product direction solve real operational problems.

Useful feedback includes:

- deployment and trust constraints;
- developer-environment reproducibility problems;
- agent and automation authority boundaries;
- audit/evidence requirements;
- local versus remote inference constraints;
- CI and build isolation requirements;
- integration pain points;
- compatibility and conformance gaps.

Participation does not imply endorsement, procurement, preferred-vendor status, future support, or a commercial relationship.

Private customer, employer, deployment, pricing, or roadmap information must not be copied into public issues or documentation.

## Open-source and licensing boundary

Source licensing is governed by [LICENSING.md](LICENSING.md). Compatibility and stability are governed by [COMPATIBILITY.md](COMPATIBILITY.md).

The source license does not imply:

- free hosted or managed service;
- free enterprise support;
- a warranty for a particular deployment;
- rights to certification or compatibility marks;
- publication of private production implementations;
- a commitment that every future Dubnium component will be released here.

Likewise, commercial offerings do not change the license of already published material except through an explicit, legally valid licensing decision.

## Public/private disclosure boundary

Commercial activity must not weaken the repository's existing publication controls.

Do not publish:

- customer identities or confidential requirements;
- private deployment topology, endpoints, credentials, or operational evidence;
- private pricing negotiations or contracts;
- production policy, trusted identities, risk thresholds, or bypass details;
- proprietary prompts, routing, memory behavior, or provider implementations;
- unpublished commercial roadmap commitments;
- private repository coordinates or internal issue tracking.

See [PUBLICATION_BOUNDARY.md](PUBLICATION_BOUNDARY.md) for the complete public website and generated-book boundary.

## Guiding principle

The public ecosystem should make integration, validation, and independent implementation credible. Commercial value should come from trustworthy operationalization, supported integration, lifecycle management, and organizational complexity rather than from obscuring the public protocol boundary.