# AI and Automation

Dubnium supports AI-assisted development and automation without making a model the operating-system authority.

## AI is optional capability

A Dubnium environment may use local models, remote models, or no model at all. Deterministic configuration, security boundaries, runtime observation, workflow state, and recovery should continue to work independently.

Model selection and provider choice are implementation concerns behind a stable caller-facing boundary. Changing a model must not silently widen access to data, tools, credentials, networks, or privileged effects.

## Local-first model routing

Local execution is the default direction where it is sufficient for the task. A request may use a stronger remote or frontier model only through an explicit bounded escalation path that preserves policy, sanitization, lineage, provider constraints, and traceability.

Escalation changes available model capability. It does not transfer effect authority, grant additional tools or credentials, or convert unresolved policy into permission. A policy ambiguity or required human decision remains unresolved rather than being "solved" merely by selecting a stronger model.

The exact production triggers, provider configuration, and routing heuristics remain private implementation concerns.

## Model serving and token efficiency

The serving direction includes multiple local model surfaces, heterogeneous accelerators and multi-GPU configurations where they improve useful workload capacity. A routing decision must first respect model eligibility, data boundaries, available resources and quality requirements. Efficiency can then be evaluated through model selection, reuse of relevant context and avoiding unnecessary calls or generated tokens.

Cost and token savings are objectives, not guarantees. Comparisons need matched task quality and end-to-end costs including classification, retries, escalation and verification. Source-level composition is not proof of simultaneous physical model residency or a production serving profile.

## Classification and prediction

Classification can help identify the kind of work or reasoning capability a task requires. Predictive capabilities can help anticipate workload transitions, likely failures or whether a proposed action warrants more evidence. These are distinct from generation, and from each other.

The experimental direction is to evaluate these signals under conservative or shadow-mode conditions before allowing them to influence planning or routing. Neither a prediction nor a classifier may authorize an effect, override a hard guard, increase a budget, or substitute for deterministic validation. Effectiveness and runtime integration remain under qualification.

## Connecting external AI tools

Dubnium is developing a native Model Context Protocol (MCP) interface so approved assistants and engineering tools can request **bounded, observable operations** without gaining general host access. OpenAI's Secure MCP Tunnel is a candidate transport for connecting ChatGPT to a private MCP service without making that transport an authorization decision.

The initial focus is **read-only engineering status**, beginning with CI runner observation. Governed write operations are a separate future capability: a tool request alone cannot approve an effect, choose its own privileges, or substitute for independent verification.

**Status:** MCP interoperability and transport qualification are in progress. The public overview does not imply that the ChatGPT integration, privileged tools, or a supported remote-control service is deployed.

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

## Memory and scheduling interfaces

The [Memory Service v1alpha](https://github.com/hackelia-micrantha/dubnium-community/blob/main/spec/memory-service-v1alpha.md) publishes scoped storage, retrieval and expiry semantics; retrieved evidence is not automatically trusted or current. The [Scheduler API v1alpha](https://github.com/hackelia-micrantha/dubnium-community/blob/main/spec/scheduler-v1alpha.md) publishes inspection and control of declared schedules within an administrative boundary. It is not a public arbitrary-job endpoint or a grant of execution authority.

A local-first data strategy should let operators retain control of durable context, schedules, source and evidence, and make external sharing or inference an explicit decision. Model selection and data residency remain separate questions; local inference alone does not prove confidentiality or compliance.

## Training has separate authorities

Model training follows the same governed-effect model as other consequential automation. A backend-neutral training request can describe intent, but execution authority, resource enforcement, evaluation, promotion, catalog binding, and runtime activation remain separate responsibilities.

A successful training operation yields a candidate artifact. It does not by itself prove evaluation success, authorize promotion, select a production model, or activate that model for inference. Models and specialists cannot authorize their own training or promotion merely because they generated the proposal or candidate.

## Resource-aware operation

AI inference, builds, tests, model training, background automation, and interactive work can all compete for CPU, memory, storage, network, and accelerators. Dubnium treats resource placement and isolation as operating concerns rather than model-routing side effects.

## Evidence remains bounded

Automation should produce enough structured evidence to explain outcomes while avoiding indiscriminate capture of source, prompts, credentials, private messages, training data, or unrelated user activity.

## Public interoperability

Public Dubnium contracts may describe model-independent request surfaces, capability envelopes, scheduling or state semantics, and conformance behavior when those interfaces are useful to external consumers. Private routing heuristics, production prompts, trusted identities, provider configuration, training implementation, and stored user data remain outside the public boundary.
