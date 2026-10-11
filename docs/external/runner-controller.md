# Self-Hosted CI Runner Controller

Dubnium treats self-hosted CI capacity as a governed runtime resource rather than a collection of permanently waiting runner processes.

The public design goal is simple: **keep controller authority persistent, but make ordinary job execution short-lived and bounded**.

## Responsibility split

```mermaid
flowchart LR
    A[Repository demand] --> B[Runner Controller]
    B --> C{Admission permitted?}
    C -- no --> D[Remain waiting or denied]
    C -- yes --> E[Short-lived worker]
    E --> F[One job]
    F --> G[Cleanup and reconciliation]
    G --> B
```

The controller owns lifecycle decisions and status. The worker owns one admitted job and then disappears.

## Why not keep ordinary runners permanently idle?

A permanently waiting worker carries more ambient state than Dubnium needs for ordinary CI demand. Short-lived workers reduce the amount of time job execution environments exist and make ownership easier to reason about.

This does not make untrusted CI safe by itself. It provides a clearer lifecycle boundary that can be combined with reviewed repository policy, bounded resources, credential separation, filesystem isolation, and destination-side controls.

## Admission happens before worker creation

A workflow asking for capacity does not get to choose arbitrary authority.

Before ordinary work is admitted, the controller evaluates already-reviewed eligibility and current host state. Publicly relevant inputs include:

- whether the repository is eligible for local execution;
- whether the requested class of work is already declared;
- whether bounded capacity is available;
- whether administrative policy currently permits work;
- whether existing worker ownership can be explained.

Only admitted work receives a worker.

The exact registry, thresholds, credentials, scheduling algorithm, and host-specific resource values are deployment details and are intentionally not published here.

## The worker is intentionally disposable

An admitted worker has a narrow lifecycle:

```text
created
  -> accepts one admitted assignment
  -> executes inside bounded job isolation
  -> reports terminal outcome
  -> cleanup
  -> gone
```

Ordinary workers do not become a durable source of configuration or identity. A future job is admitted again from current policy and current host state.

## Controller credentials do not become job credentials

The controller may need authority to coordinate the runner lifecycle. That authority is not meant to become ambient authority inside the job environment.

This separation is important because the code under test should not inherit control-plane credentials merely because it runs on the same physical endpoint.

The public invariant is credential separation; exact credential material and transport remain private.

## Capacity is a state model, not a process count

Operators should not infer capacity from the number of visible worker processes.

A useful conceptual model is:

```text
configured eligibility
  + administrative permission
  + bounded host capacity
  - currently owned work
  = currently available capacity
```

The implementation may represent additional states, but this distinction explains an important behavior: **zero active workers can be a healthy idle condition**.

Likewise, configured capacity does not imply that idle workers must already exist.

## Canonical observation

The controller exposes bounded status through the operator surface:

```sh
dubctl runners status
dubctl runners status --json
```

The status model is intended to answer questions such as:

- is self-hosted CI administratively permitted;
- what capacity is currently eligible;
- how much admitted work is owned;
- which workers are active;
- whether controller observation is healthy;
- whether reconciliation is required.

Scripts and dashboards should consume the structured state rather than derive lifecycle truth from process lists or logs.

## Reconciliation is explicit

CI state can become stale or partially completed when a process crashes, a job disappears, or cleanup is interrupted. The controller therefore treats reconciliation as a first-class responsibility.

The goal is not to preserve a worker at all costs. The goal is to restore an explainable relationship between admitted work, owned resources, and observed runtime state.

Ambiguous ownership should fail safely rather than guessing that an unknown worker can be reused or deleted.

## Queue priority does not create authority

When multiple already-authorized jobs are waiting for bounded local capacity, ordering may decide which job receives the next available slot.

Priority changes **order**, not eligibility. A lower-level workflow request cannot use queue manipulation to select another repository's profile, stronger credentials, or additional capability.

## Project-owned toolchains and binary-cache reuse

Ordinary short-lived workers provide a **small execution substrate**. Repository-owned flakes declare browser, language, SDK, and test dependencies; adding a workload does not implicitly expand the shared runner image or the authority of other repositories.

Repeated realization of large Nix closures is addressed through the standard **Nix binary-cache data plane**, separate from the runner control plane:

```text
project-owned flake / derivation
    -> trusted builder and constrained publisher
    -> signed content-addressed Nix cache
    -> read-only verified substitution
    -> isolated short-lived job worker
```

An ordinary job may consume a verified cache object but must not overwrite the canonical cache, publish under the trusted signing identity, or write to another worker's store. Signature and trust-root checks apply even when the cache is local. A cache miss or invalid signature must be handled by declared, bounded build policy or rejection, **never** by silently using ambient host tools. Redis, model memory, and a general capability bus do not replace Nix content-addressed substitution.

Caching has two independent concerns: **data movement** uses Nix substituters and immutable artifacts; **authority to publish, manage retention, or change trust configuration** belongs to a reviewed host capability or administrative workflow. Capability-backed orchestration may authorize those bounded operations but must not convert worker input into cache-publisher authority.

**Maturity:** generic image reduction and initial signed-cache negative/positive validation have implementation evidence. End-to-end read-only JIT substitution, governed publication, cache retention, and representative cold/warm performance qualification remain active work; they are not asserted as deployed.

## CI jobs and the Capability Gateway

A workflow request, even from an eligible repository, is not a reusable privilege grant. The planned `ci.integration-test` provider is a **typed Capability Gateway module** for bounded OCI-based integration tests. It reuses the existing authenticated actor, Anthesis policy/approval, request ledger and execution-authority boundaries rather than adding a second OCI admission service.

Its intended constraints include exact CI-job provenance, an immutable authorized execution plan, reviewed image and test profiles, rootless containment, resource bounds, lifecycle observation and terminal evidence. Controller identity and worker-job identity remain distinct. A passing unit fixture or policy denial is not proof of a completed live container test.

## Trust boundaries

The runner design preserves several separations:

| Boundary | Public invariant |
| --- | --- |
| Repository demand → admission | Demand does not imply permission |
| Controller → worker | Lifecycle authority is not inherited by job code |
| Worker → host | Job execution is bounded and disposable |
| Queue → policy | Ordering does not widen eligibility |
| Logs → state | Logs are evidence, not lifecycle authority |
| Previous job → next job | Successful execution grants no future authority |

## What is deliberately omitted

This overview does not publish exact repository mappings, runner labels, service wiring, credential flows, filesystem paths, resource thresholds, scheduling heuristics, cleanup implementation, or production incident procedures.

Those details are not required to understand the public contract: reviewed eligibility becomes bounded short-lived execution through an observable controller-owned lifecycle.
