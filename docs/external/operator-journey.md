# Operator Journey

This chapter shows how the public Dubnium responsibilities fit together from an operator's point of view. It is an **illustrative workflow**, not a production runbook: exact deployment values, privileged procedures, and private enforcement details remain outside the published surface.

## Start by discovering the installed surface

Dubnium favors discoverable commands and semantic help over memorized implementation details. The operator should be able to identify what is installed before changing anything.

Representative read-only entry points include:

```sh
dubctl commands
dubctl service list
modectl status
configctl status
dubctl runners status
```

Read-only status, list, show, and diagnostic commands should remain side-effect free. Machine-readable forms are useful for automation when a stable JSON contract is available.

## 1. Inspect declared and observed state separately

The first question is not "what should be running?" but "what does this endpoint declare, and what is actually running now?"

An operator may inspect:

- the installed capability surface;
- current runtime posture;
- service and workload state;
- writable configuration ownership and drift;
- self-hosted CI eligibility and active worker state.

This prevents a common failure mode in managed environments: assuming that a successful build or declaration proves the runtime converged.

## 2. Change only the responsibility that actually needs changing

Dubnium intentionally keeps several operator surfaces separate.

| Need | Surface |
| --- | --- |
| Apply reviewed host configuration | `dubctl` + declarative apply |
| Select an already-declared runtime posture | `modectl` |
| Reconcile legitimate writable user configuration | `configctl` |
| Inspect or administratively gate CI capacity | `dubctl runners` |

The separation matters because each action has a different source of truth and authority boundary.

For example, selecting a runtime mode does not install a capability that was not declared. Likewise, changing a writable preference does not become a way to redefine privileged host policy.

## 3. Observe convergence after a change

A requested transition is only one piece of evidence. After a bounded change, the operator checks the resulting state rather than assuming success.

A generic control loop looks like:

```text
inspect
  -> request bounded change
  -> reconcile
  -> observe resulting state
  -> report success, degraded state, or failure
```

This pattern appears across runtime modes, writable configuration, services, and CI worker lifecycle.

## 4. Treat automation as another caller

Scheduled jobs, workflows, and model-assisted tools follow the same authority rules as an interactive operator.

Automation may:

- read bounded status;
- propose intent;
- request a capability already available to it;
- consume structured results and evidence.

Automation may not infer additional authority from previous success, retrieved context, or the fact that a stronger model generated the request.

## 5. Inspect self-hosted CI without inferring from processes

For self-hosted CI, the controller owns the canonical lifecycle view. An operator can inspect it directly:

```sh
dubctl runners status
dubctl runners status --json
```

The important public semantics are eligibility, bounded capacity, occupancy, worker lifecycle, and reconciliation health. An empty worker list can be a healthy idle state when no work is owned; it is not evidence that capacity disappeared.

See [Self-Hosted CI Runner Controller](runner-controller.md).

## 6. Use structured state for tooling

Operator-facing output can remain readable for humans while exposing versioned structured forms for scripts and dashboards. Structured consumers should use the same validated state contract rather than reparsing human-oriented output or reconstructing state from logs.

That gives the operator and automation the same answer to questions such as:

- what is eligible;
- what is active;
- what is owned;
- what is degraded;
- what requires reconciliation.

## 7. Escalate ambiguity without widening authority

When a task is ambiguous or difficult, Dubnium may route reasoning to a stronger model or require human review. That changes who helps interpret the request, not what the request is allowed to do.

The final effect still crosses the same policy and capability boundary.

## What good operation looks like

A healthy operator workflow has a few recognizable properties:

- inspection precedes mutation;
- commands explain their responsibility and effect;
- requested state and observed state are both visible;
- failures remain explicit rather than being papered over by retries;
- structured evidence is bounded and reusable;
- no convenience surface silently becomes a new source of authority.

The objective is not to hide system complexity. It is to make the important complexity visible at the correct boundary while keeping implementation-specific machinery replaceable.
