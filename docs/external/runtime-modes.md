# Runtime Operating Modes

A reproducible endpoint does not need every declared capability active at the same time. Dubnium uses runtime operating modes to select which already-declared workload posture should be active **now** without treating an imperative mode change as a replacement for declarative configuration.

## Modes versus capabilities

The distinction is intentional:

```text
declarative configuration -> what the endpoint is allowed and able to run
runtime mode              -> which declared posture should be active now
observed state             -> what is actually active after reconciliation
```

A mode switch does not install new capabilities. A declared capability does not imply that its workload is currently active.

## Current mode model

| Runtime identifier | Human-facing intent | Runtime posture |
| --- | --- | --- |
| `desktop` | Normal interactive engineering | Graphical and developer-facing workloads take priority; compute-oriented AI workloads remain suppressed by mode policy |
| `studio-local` | **Media mode** | Desktop remains available while media-priority policy protects latency-sensitive work and suppresses competing compute pressure |
| `compute` | Dedicated compute and local AI | Graphical work is released and compute-oriented services receive the resources required by the declared compute posture |

`studio-local` remains the current runtime identifier for media mode. Some implementation identifiers may retain older studio/audio terminology for compatibility; that does not narrow the intended media-mode semantics.

## `modectl` responsibility

`modectl` is the operator surface for these transitions. Its observable behavior is a reconciliation loop rather than a collection of arbitrary service toggles:

1. record the desired mode;
2. observe the current runtime posture;
3. validate that the requested transition is allowed;
4. run guards that protect active work and resource safety;
5. reconcile bounded runtime changes;
6. observe again;
7. record success, blockage, or failure from the observed result.

The key invariant is that **attempting a transition is not evidence that the transition succeeded**. Success requires post-transition observation consistent with the requested mode.

## Transition guards

Disruptive transitions are guarded by categories of runtime evidence such as:

- active workload state;
- CPU/load and memory headroom;
- graphical/display resource ownership;
- protected media activity, including latency-sensitive audio where applicable;
- whether a service can be safely drained before its resources are reassigned.

Exact guard names, thresholds, service wiring, hardware assignments, and machine-specific exceptions are deployment policy and are intentionally outside this technical overview.

## Authority boundary

A mode request can change runtime posture only within capabilities already declared for the endpoint. It cannot:

- install a missing capability;
- widen authorization;
- bypass a governed-effect decision;
- rewrite the NixOS definition;
- redefine resource or security policy;
- turn a failed observation into success.

This keeps `modectl` useful for resource-sensitive work while preserving the separation between declarative intent, runtime control, and observed state.
