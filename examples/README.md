# Examples

Status: experimental
Content: informative
Canonical source: this file
Generated: no

`examples/` contains synthetic request, response, error, stream-event, positive, negative, and adversarial fixtures.

Every JSON example MUST identify its canonical bundled schema with `$schema`. Examples MUST NOT contain real identities, repositories, hosts, credentials, incidents, logs, prompts, approvals, or operational measurements.

For catalogued HTTP contracts, every OpenAPI operation MUST map to at least one positive example. Important error and security boundaries SHOULD have explicit fixtures. Negative examples MUST fail canonical schema validation.
