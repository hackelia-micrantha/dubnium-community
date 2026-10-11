# AI and Automation

Dubnium supports AI-assisted development and automation without making a model the operating-system authority.

## AI is optional capability

A Dubnium environment may use local models, remote models, or no model at all. Deterministic configuration, security boundaries, runtime observation, workflow state, and recovery should continue to work independently.

Model selection and provider choice are implementation concerns behind a stable caller-facing boundary. Changing a model must not silently widen access to data, tools, credentials, networks, or privileged effects.

## Local-first model routing

Local execution is the default direction where it is sufficient for the task. A request may use a stronger remote or frontier model only through an explicit bounded escalation path that preserves policy, sanitization, lineage, provider constraints, and traceability.

Escalation changes available model capability. It does not transfer effect authority, grant additional tools or credentials, or convert unresolved policy into permission. A policy ambiguity or required human decision remains unresolved rather than being "solved" merely by selecting a stronger model.

The exact production triggers, provider configuration, and routing heuristics remain private implementation concerns.

## External AI clients: native MCP, tunneling, and Desktop Commander

The intended external-tool interface is a **Dubnium-owned, provider-neutral MCP server using native Streamable HTTP**. An approved client may reach that same interface through a separately qualified private-network connection or the **OpenAI Secure MCP Tunnel**. The tunnel supplies a transport path; it is not a gateway for policy decisions, credential delegation, repository writes, or shell execution.

The initial OpenAI integration is deliberately read-only:

```text
ChatGPT / authorized MCP client
    -> OpenAI Secure MCP Tunnel (transport only)
    -> private native HTTP MCP tool interface
    -> runner.status
    -> authenticated canonical runner observation
```

`runner.status` is a bounded view over the existing runner-status authority, not another independent fleet state store. The current reference read originates from the Operator Gateway; **the MCP interface itself does not depend on routing all future tools through the Operator Gateway**. Other clients may use the same native MCP contract with separately reviewed transport and identity bindings. Direct reachability, a valid MCP request, tunnel registration, and a model's tool invocation each remain insufficient to authorize a consequential effect.

A later governed-effect tool follows a separate path:

```text
approved MCP client / typed intent
    -> authenticated actor and constrained tool request
    -> Capability Gateway
    -> Anthesis decision / required approval
    -> bounded provider effect
    -> verification and evidence
```

Identity binding and policy cannot be delegated to the model or tunnel. The tool catalog must distinguish inspection from mutation; arbitrary shell, unconstrained filesystem writes, HTTP-to-stdio adapters, and ambient host-control credentials are not substitutes for typed capabilities.

**Desktop Commander transition.** The existing Desktop Commander Remote integration is a *transitional client path*, not an execution-authority plane. The architectural goal is for native MCP tools plus governed capability clients to replace dependence on the vendor Remote bridge. Retirement is **conditional** on demonstrating equivalent or better authorized repository inspection, candidate editing, bounded validation, identity attribution, recovery and availability; no replacement is claimed complete simply because a tunnel or MCP fixture exists.

**Maturity:** HTTP-only tool definitions, transport qualification and integration fixtures are under review. This overview does not claim an activated tunnel, production ChatGPT pairing, approved mutating MCP catalog, or completed Desktop Commander retirement.

## Reasoning is not an effect

A useful separation is:

```text
reasoning proposes intent
-> deterministic validation
-> policy / approval boundary
-> bounded capability
-> effect execution
-> durable outcome and evidence
```

Model output can propose an action. It cannot mint its own identity, approve itself, or turn previous success into future authority.

## Retrieval is evidence, not authority

Where semantic memory retrieval is enabled, canonical memory records remain the authoritative stored state while embeddings and indexes are derived, rebuildable retrieval state. Similarity rank does not establish approval, permission, currentness, or operational truth.

The Memory Service owns retrieval over its own governed memory corpus; it does not become a generic search federation layer. Document or project search, repository state, and live runtime observation remain separate sources that the caller or Supervisor may consult according to the task and source-of-truth boundary.

## Stateful automation owns state

Scheduled work, durable workflows, memory/context systems, and long-running operations should expose explicit lifecycle and state rather than exist only inside model context.

That makes retries, recovery, auditing, and replacement possible without asking a model to reconstruct what probably happened.

## Training has separate authorities

Model training follows the same governed-effect model as other consequential automation. A backend-neutral training request can describe intent, but execution authority, resource enforcement, evaluation, promotion, catalog binding, and runtime activation remain separate responsibilities.

A successful training operation yields a candidate artifact. It does not by itself prove evaluation success, authorize promotion, select a production model, or activate that model for inference. Models and specialists cannot authorize their own training or promotion merely because they generated the proposal or candidate.

## Resource-aware operation

AI inference, builds, tests, model training, background automation, and interactive work can all compete for CPU, memory, storage, network, and accelerators. Dubnium treats resource placement and isolation as operating concerns rather than model-routing side effects.

## Evidence remains bounded

Automation should produce enough structured evidence to explain outcomes while avoiding indiscriminate capture of source, prompts, credentials, private messages, training data, or unrelated user activity.

## Public interoperability

Public Dubnium contracts may describe model-independent request surfaces, capability envelopes, scheduling or state semantics, and conformance behavior when those interfaces are useful to external consumers. Private routing heuristics, production prompts, trusted identities, provider configuration, training implementation, and stored user data remain outside the public boundary.
