# Status and Direction

This page describes the published product surface and directional architecture only. It is not an internal delivery schedule and does not imply publication of private implementation.

The repository remains in incubation. The first [Capability Gateway alpha contract bundle](https://github.com/hackelia-micrantha/dubnium-community/releases/tag/contract-v0.1.0-alpha.1) is published and independently verifiable. Release acceptance, downstream integration qualification, and production readiness remain separate gates. No stable consumer compatibility baseline has been accepted.

## Evidence available today

| Area | Engineering work | Public evidence and qualification |
| --- | --- | --- |
| Reproducible platform | Declarative environments, operator tooling and runtime reconciliation | [Components](components.md) and [operator journey](operator-journey.md) describe the implementation surfaces; no generally available distribution |
| Self-hosted CI | Short-lived workers and controller-owned admission and status | [Runner architecture](runner-controller.md); operational qualification remains ongoing |
| Governed execution | Experimental capability envelopes, lifecycle and negative conditions | [Published alpha bundle](https://github.com/hackelia-micrantha/dubnium-community/releases/tag/contract-v0.1.0-alpha.1) and [conformance suites](https://github.com/hackelia-micrantha/dubnium-community/tree/main/conformance); public release acceptance remains open |
| Local-first AI | Bounded model and tool interfaces, scoped context and explicit authority | [AI and Automation](ai-and-automation.md); interfaces and integration are experimental |

The distinction matters: architectural documentation can explain a working implementation without making it independently installable, and contract conformance does not establish production security assurance.

## Current priorities

- qualify reproducible, bounded execution and the first published contract release;
- improve independently usable conformance examples and downstream integration evidence;
- evaluate use cases for self-hosted builds, local AI and governed automation with external feedback.

The [public roadmap](https://github.com/hackelia-micrantha/dubnium-community/blob/main/ROADMAP.md) tracks the exact contract and release work.

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

Additional planned or developing capability families include Supervisor-mediated on-demand execution, durable workflows, staged AI-assisted recovery, multi-user account separation, and mobile/web operator diagnostics. Each requires its own qualification; the research directions are not a release or delivery commitment.

Recent work spans several related outcomes:

- **Reproducible, self-hosted CI:** more predictable short-lived workers, smaller reusable runner foundations, and verified Nix output reuse. Cache adoption and performance qualification remain ongoing.
- **AI-assisted engineering interfaces:** read-only MCP access is being qualified for external clients, including ChatGPT, with governed effects remaining distinct from transport and tool invocation.
- **Governed capabilities:** scoped client interfaces and additional domain operations are being developed incrementally; public contracts are ahead of some production integrations.
- **Observable automation:** portable event interoperability, operational status, and traceable outcomes are being expanded without making telemetry an authorization source.
- **Resource-aware AI:** bounded usage concepts and local inference evaluations are active areas of exploration, not promised performance or deployed model offerings.

The strongest public artifacts are versioned contracts, synthetic examples, conformance tests, and reproducible demonstrations. Private infrastructure, operational incidents, implementation wiring, unpublished benchmark data, and policy internals are outside this book.

See [Research foundations](research.md) for a ranked selection of relevant public literature.

## Public validation opportunities

The following are **candidates for independent community validation**, not release promises:

- **Portable event interoperability:** mature synthetic [CloudEvents conformance examples](https://github.com/hackelia-micrantha/dubnium-community/issues/54) without publishing real operational events or producer topology.
- **Reproducible workstation demonstration:** make a small [local AI engineering demo](https://github.com/hackelia-micrantha/dubnium-community/issues/43) buildable by an outside contributor, with a documented failure case and no private dependencies.
- **Resource-aware automation:** explain visible usage limits and accountable execution at a conceptual level; detailed budget state machines, ledgers, provider routing and policy are not book material.
- **Read-only tool integration and CI performance evidence:** consider synthetic MCP examples and reproducible cache benchmarks after their integration and measurement gates pass, avoiding private endpoints, runner inventories, and host-specific measurements.

The book is a conceptual entry point; public specifications are published separately only when reviewed as intentional interoperability commitments.

## Next published outcomes

- Complete release acceptance and verify immutable release consumption in downstream implementations.
- Make public integrations easier to evaluate with synthetic examples and compatibility guidance.
- Use independent adopter and design-partner feedback to determine which supported deployment patterns and additional interfaces justify further work.

These are directional outcomes, not delivery dates or commercial commitments. The [public roadmap](https://github.com/hackelia-micrantha/dubnium-community/blob/main/ROADMAP.md) retains the detailed engineering gates.

## Later, evidence permitting

- additional adapters or language bindings justified by real consumers;
- thin validation and conformance commands;
- additional API families where an interoperability need stabilizes;
- fleet or endpoint contracts only when they are useful without exposing private topology, identity, or policy.

## Explicitly outside this roadmap

The published roadmap does not imply disclosure of production prompts, routing heuristics, policy internals, trusted identities, private data, privileged provider implementation, host or fleet configuration, operational evidence, incidents, credentials, or private planning.