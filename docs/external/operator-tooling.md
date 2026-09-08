# Operator Tooling

Dubnium separates host control, runtime posture, and writable user configuration instead of putting all three responsibilities behind one privileged command.

| Tool | Primary responsibility | Must not become |
| --- | --- | --- |
| `dubctl` | Host/operator workflows and explicit declarative apply | General policy engine or application-data manager |
| `modectl` | Runtime posture selection and reconciliation | Capability installer or authorization bypass |
| `configctl` | Writable user-configuration ownership and reconciliation | Privileged host-configuration escape hatch |

## `dubctl`

`dubctl` is the host-operator façade for Dubnium. It provides one discoverable surface for system workflows that would otherwise require operators to know several lower-level implementation tools.

Its public responsibility model is deliberately narrow:

- **inspect** — report bounded host, workload, configuration, and diagnostic state;
- **select** — change only options or capabilities that are already registered by reviewed configuration;
- **apply** — evaluate and explicitly apply declared configuration;
- **develop** — enter or operate on declared development environments and inputs;
- **discover** — expose the installed command/capability surface without making documentation a static command inventory.

Representative command families include `dubctl service`, `dubctl capability`, `dubctl runners`, `dubctl apply`, `dubctl inputs`, and `dubctl commands`. The exact installed command tree may evolve as bounded components are added or removed.

### Authority boundary

`dubctl` does not own source-controlled host policy. A CLI selection does not become an unrestricted configuration language, and an apply operation does not make the CLI the source of truth for the resulting system.

`dubctl` also does not own:

- Home/user configuration layering managed through `configctl`;
- runtime-mode state managed through `modectl`;
- secrets or credentials;
- service-specific workflows, indexes, databases, or other application data;
- policy decisions for governed effects.

The design goal is a coherent operator experience without collapsing independent trust boundaries into one command.

### Runner operations

`dubctl runners` exposes bounded observation and control for self-hosted CI capacity. Its read-only status and watch surfaces report controller-owned state such as effective eligibility, capacity and occupancy, worker lifecycle, and reconciliation health instead of asking operators to infer runner state from labels or process lists.

Runner admission remains policy-bound. Repository identity, capability profile, credentials, and resource envelope come from reviewed configuration; workflow-controlled input cannot select a stronger profile or another repository's authority. Admitted jobs execute in short-lived workers and do not inherit the controller's long-lived credentials.

Administrative runner controls affect whether already-declared capacity may accept work. They do not edit the underlying registry, mint new capability, or turn a workflow request into authorization.

## `modectl`

`modectl` manages the current runtime posture. It records requested mode, observes current state, applies transition guards, reconciles bounded runtime changes, and verifies the result.

This is intentionally different from `dubctl apply`: declarative configuration determines what the endpoint can run; `modectl` determines which already-declared posture should be active now.

See [Runtime Operating Modes](runtime-modes.md).

## `configctl`

`configctl` handles the part of the user environment that legitimately needs to remain writable even when managed defaults come from immutable Nix-store-backed configuration.

It reports ownership and drift, establishes writable layers, supports reviewable promotion of useful changes, and handles bounded first-run state where declaring a file alone is insufficient.

See [Writable User Configuration](writable-configuration.md).

## Why the tools stay separate

The separation gives each question a clear authority:

```text
What should this endpoint be able to run?  -> declarative configuration
What host change should be applied?        -> dubctl + declarative apply
What CI capacity is eligible or active?    -> dubctl runners + controller observation
What runtime posture should be active now? -> modectl
Who owns this user preference?             -> configctl
What is actually active?                   -> runtime observation
```

Keeping these questions distinct makes state easier to explain and reduces the chance that a convenience CLI silently becomes a second configuration or authorization system.