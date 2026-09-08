# Contracts and Conformance

Dubnium publishes contracts when interoperability is useful and disclosure does not require publishing the production implementation behind the boundary.

## Suitable published material

- normative protocol and schema definitions;
- canonicalization and compatibility rules;
- request, response, error, state, and evidence envelopes;
- synthetic positive, negative, and adversarial fixtures;
- implementation-neutral conformance tests;
- thin clients, validators, and authoring helpers;
- minimal no-effect reference implementations;
- release checksums, software bills of materials, and published attestations.

Published contracts may eventually cover additional capability, scheduling, state, or model-independent interfaces when there is a stable interoperability need. Publication follows usefulness and disclosure review rather than mirroring internal APIs by default.

## Material that remains private

- production planning, prompts, routing, retries, and fallbacks;
- production policy, approvals, thresholds, and trusted identities;
- private data ranking, retention, consolidation, retrieval, and stored content;
- privileged providers, deployment workers, and recovery behavior;
- host and fleet topology, credentials, operator configuration, and runbooks;
- real logs, incidents, traces, evidence, and operational measurements.

## Compatibility model

Published contracts are versioned and classified by stability. Consumers should pin immutable releases, verify digests and provenance, and exercise conformance tests at their integration boundary.

A contract describes observable behavior. It does not promise a particular internal architecture, service layout, implementation language, deployment model, or provider.

## Disclosure model

A contract crosses the publication boundary only when its external value exceeds the cost and risk of maintaining it openly. Private implementation details are not documentation debt merely because a published contract exists.

## Source of truth

Specifications, schemas, conformance assets, reference implementations, release metadata, and community documentation are maintained in the [Dubnium Community repository](https://github.com/hackelia-micrantha/dubnium-community).