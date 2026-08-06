# Examples

Status: experimental
Content: informative
Canonical source: this file
Generated: no

`examples/` contains synthetic demonstrations of public contracts and packages.

Examples MUST NOT contain real people, repositories, hosts, endpoints, credentials, incidents, logs, evidence, prompts, policies, approvals, performance measurements, or operator configuration. Values should be visibly fictional and unsuitable for deployment.

Examples are informative unless a normative specification explicitly incorporates one.

## Service example sets

- `memory-service-v1alpha/` contains a positive store request and an invalid-scope fixture.
- `supervisor-gateway-v1alpha/` contains positive chat request/response fixtures and an unsupported-tools fixture.
- `scheduler-v1alpha/` contains a positive schedule response and an invalid-control-status fixture.

Each example declares its canonical bundled schema with `$schema`. Positive and negative behavior is checked by the generic catalog runner rather than per-API scripts.
