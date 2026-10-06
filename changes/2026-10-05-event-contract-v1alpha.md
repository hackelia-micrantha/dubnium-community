# Add Dubnium Event Contract v1alpha

Status: experimental
Content: informative
Canonical source: this file
Generated: no
Compatibility: additive experimental contract

## Summary

Adds the public Dubnium CloudEvents Event Contract v1alpha required by
`ryjen/dubnium#766/#767` and coordinated through the Micrantha observability
rollout.

## Added

- CloudEvents 1.0 as the outer event envelope;
- versioned Dubnium event-type and bounded producer-source rules;
- 16 KiB event and bounded data-shape limits;
- minimum sensitive-field rejection plus an explicit producer-allowlist
  requirement;
- W3C `traceparent` / `tracestate` preservation without authority semantics;
- machine-readable JSON Schema;
- synthetic public examples and positive/negative conformance fixtures;
- a dependency-free profile validator wired into Contract CI.

## Authority boundary

Event identity and trace context are observational correlation. They do not
grant authentication, authorization, approval, capability, provider,
deployment, scheduler, or governance authority.

No private topology, credentials, real event evidence, retention policy,
collector deployment, or notification routing is published by this change.

## Compatibility

This is a new experimental v1alpha contract and does not modify an existing
stable event wire contract. Incompatible meaning or envelope changes require a
reviewed version change.
