# Dubnium Event Contract v1alpha

Status: experimental
Content: normative
Canonical source: this file
Generated: no

## 1. Scope

This specification defines the public Dubnium event envelope used for bounded,
interoperable domain and lifecycle events.

CloudEvents 1.0 is the outer event format. This profile adds only Dubnium-owned
naming, bounds, safe-data rules, and trace-context handling. It does not define
an event broker, durable store, notification provider, collector backend,
deployment topology, or authorization protocol.

OpenTelemetry remains the telemetry/correlation companion standard. An event is
not an OpenTelemetry span, and a trace is not canonical domain state.

Canonical public artifacts are:

- `schemas/v1alpha/event.schema.json`;
- `conformance/event_contract_v1.py`;
- `conformance/fixtures/events-v1/fixtures.json`;
- synthetic examples in `examples/events-v1alpha/README.md`.

## 2. CloudEvents envelope

A conforming event MUST use CloudEvents `specversion` `1.0`.

The following context attributes are required:

- `id`;
- `source`;
- `type`;
- `time`;
- `datacontenttype`, fixed to `application/json`;
- `data`, as a JSON object.

`subject` is optional.

Unknown safe CloudEvents extension attributes MUST be preserved by relays that
otherwise preserve CloudEvents context. Consumers MUST ignore extension
attributes they do not understand unless a narrower negotiated contract says
otherwise.

## 3. Identity and versioning

Event IDs MUST be globally unique within the producing system and MUST NOT be
derived from credentials or secret material.

Dubnium event types use:

```text
org.micrantha.dubnium.<domain>.<event>[.<event>...].v1
```

Examples:

```text
org.micrantha.dubnium.github.runner.started.v1
org.micrantha.dubnium.supervisor.run.started.v1
org.micrantha.dubnium.llm.inference.completed.v1
```

A semantic change that makes existing consumers misinterpret an event MUST use
a new terminal version component.

Public producer sources use bounded URNs:

```text
urn:dubnium:<component>[:<subcomponent>...]
```

The source identifies the logical producer class, not a private host name,
filesystem path, credential, repository mapping, or deployment instance.

`subject` MAY identify the bounded domain object relevant to the event, but it
MUST NOT contain secret values, arbitrary user-controlled text, prompts,
commit messages, or workflow payloads.

## 4. Data profile

`data` MUST be an object with a required `severity` field.

Allowed severities are:

```text
debug
info
warning
error
critical
```

Generic event data MUST be intentionally projected from domain state. Producers
MUST NOT serialize arbitrary domain objects, request objects, process
environments, or log records into the event.

The v1alpha profile limits a serialized event to 16 KiB, event data to 32
top-level properties, nested collections to 128 members, and data nesting to
eight levels. Implementations MAY impose smaller bounds.

The conformance profile rejects common sensitive field names, including secret,
password, credential, authorization, raw prompt/completion, raw memory,
request-body, workflow-payload, and environment fields. This denylist is a
minimum guard, not a substitute for producer allowlists.

## 5. W3C trace context

When an event is emitted inside a traced operation, the producer SHOULD preserve
the active W3C Trace Context using the CloudEvents distributed-tracing extension
attributes `traceparent` and, when present, `tracestate`.

A conforming `traceparent` MUST contain a non-zero trace ID and non-zero parent
ID and MUST use a valid W3C version/flags shape.

`tracestate` MUST NOT be emitted without `traceparent`.

An implementation MUST NOT synthesize a distributed trace identity merely
because one is absent. Domain request/run/event IDs remain separate identities.

Trace context is observational correlation only. A receiver MUST NOT interpret
`traceparent`, `tracestate`, event ID, source, or subject as authentication,
authorization, approval, or capability evidence.

## 6. Security and privacy

Generic events exclude by default:

- credentials, passwords, API keys, bearer material, signing secrets, and
  authorization headers;
- unrestricted environment values;
- GitHub JIT configuration or workflow payloads;
- raw prompts or completions;
- raw memory contents;
- raw capability request bodies;
- arbitrary source/log bodies;
- private host topology or local filesystem paths.

A producer that needs additional data MUST define a bounded domain-specific
event contract and review its privacy/security impact.

Receiving, persisting, replaying, correlating, or displaying an event MUST NOT
grant execution, Capability Gateway, provider, scheduler, deployment, or
governance authority.

## 7. Interoperability and compatibility

Implementations SHOULD use an official CloudEvents SDK for serialization and
transport bindings. The public conformance code validates this Dubnium profile;
it is not a replacement CloudEvents implementation.

A relay MAY change transport representation while preserving CloudEvents
context and profile-safe data.

The event contract is currently experimental. Compatible additive changes MAY
add new versioned event types, examples, or safe optional extensions. Changes
to required context attributes, type/source interpretation, authority
semantics, or existing event meaning require a reviewed compatibility change
and, when incompatible, a new profile/version.

## 8. Conformance boundary

Public conformance proves bounded wire/profile behavior only. It does not prove:

- a private producer emits every required operational event;
- a journal, database, collector, or notification sink is available;
- trace context came from a trusted caller;
- an event corresponds to a successful effect;
- any authorization or governance decision.

Private implementations may consume this contract without publishing private
topology, real event evidence, credentials, retention policy, or routing policy.
