# Status and Direction

This page describes the published product surface and directional architecture only. It is not an internal delivery schedule and does not imply publication of private implementation.

The repository remains in incubation, and no protected `contract-v*` release has yet been accepted as a consumer identity.

## Current work

- maintaining the Community repository as the authoritative website, documentation, contract, and release surface;
- stabilizing experimental capability-boundary contracts and canonical behavior;
- hardening short-lived self-hosted CI admission, controller-owned status, and deterministic reconciliation boundaries;
- maturing local-first AI control boundaries, including bounded model escalation, scoped retrieval semantics, and governed model lifecycle transitions;
- expanding synthetic conformance, adversarial fixtures, validators, and no-effect references;
- maintaining an explicit source allowlist and guarded private-to-published documentation flow;
- improving architecture, governance, compatibility, security, and release guidance.

## Current architectural direction

The published design treats Dubnium as a reproducible, observable, governed engineering environment rather than only a single workstation plus AI runtime.

Directional themes include:

- smaller replaceable client environments alongside richer workstations and build/compute nodes;
- project-local reproducible development environments and explicit supply-chain trust;
- self-hosted CI through reviewed eligibility, bounded admission, short-lived workers, and controller-owned observation rather than permanently active job workers;
- local-first observability with bounded organizational posture when appropriate;
- private operator-owned status reporting and journaling kept distinct from organizational telemetry;
- local-first AI routing where stronger model selection changes reasoning capability but never widens effect authority;
- scoped memory retrieval where canonical records remain distinct from derived ranking and index state;
- model lifecycle boundaries that keep training, evaluation, promotion, and runtime activation as separate authorities;
- AI and automation behind explicit state, resource, and governed-effect boundaries;
- recovery and replacement based on declared configuration plus classified mutable state.

These themes are architecture, not a claim that a production fleet service, every model lifecycle transition, or every deployment form is currently available.

## Current engineering themes

Recent work spans several related outcomes:

- **Reproducible, self-hosted CI:** more predictable short-lived workers, smaller reusable runner foundations, and verified Nix output reuse. Cache adoption and performance qualification remain ongoing.
- **AI-assisted engineering interfaces:** read-only MCP access is being qualified for external clients, including ChatGPT, with governed effects remaining distinct from transport and tool invocation.
- **Governed capabilities:** scoped client interfaces and additional domain operations are being developed incrementally; public contracts are ahead of some production integrations.
- **Observable automation:** portable event interoperability, operational status, and traceable outcomes are being expanded without making telemetry an authorization source.
- **Resource-aware AI:** bounded usage concepts and local inference evaluations are active areas of exploration, not promised performance or deployed model offerings.

The strongest public artifacts are versioned contracts, synthetic examples, conformance tests, and reproducible demonstrations. Private infrastructure, operational incidents, implementation wiring, unpublished benchmark data, and policy internals are outside this book.

## Public validation opportunities

The following are **candidates for independent community validation**, not release promises:

- **Portable event interoperability:** mature synthetic [CloudEvents conformance examples](https://github.com/hackelia-micrantha/dubnium-community/issues/54) without publishing real operational events or producer topology.
- **Reproducible workstation demonstration:** make a small [local AI engineering demo](https://github.com/hackelia-micrantha/dubnium-community/issues/43) buildable by an outside contributor, with a documented failure case and no private dependencies.
- **Resource-budget interoperability:** evaluate a [small, implementation-neutral contract](https://github.com/hackelia-micrantha/dubnium-community/issues/57) only when independently useful; private accounting and provider routing remain out of scope.
- **Read-only tool integration and CI performance evidence:** consider synthetic MCP examples and reproducible cache benchmarks after their integration and measurement gates pass, avoiding private endpoints, runner inventories, and host-specific measurements.

The book is a conceptual entry point; public specifications are published separately only when reviewed as intentional interoperability commitments.

## Next published work

- keep generated publication and destination validation aligned with the explicit source allowlist;
- improve adopter documentation and contract integration examples;
- consume published contract releases immutably from downstream implementations;
- mature release checksums, software bills of materials, attestations, and deprecation guidance;
- document threat models and compatibility guarantees at stable interoperability boundaries;
- publish additional contracts only after their semantics are useful outside private implementation and have survived enough operational use to justify a compatibility commitment.

## Later, evidence permitting

- additional adapters or language bindings justified by real consumers;
- thin validation and conformance commands;
- additional API families where an interoperability need stabilizes;
- fleet or endpoint contracts only when they are useful without exposing private topology, identity, or policy.

## Explicitly outside this roadmap

The published roadmap does not imply disclosure of production prompts, routing heuristics, policy internals, trusted identities, private data, privileged provider implementation, host or fleet configuration, operational evidence, incidents, credentials, or private planning.