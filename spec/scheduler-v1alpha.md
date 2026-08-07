# Scheduler API v1alpha

Status: experimental
Content: normative
Canonical source: this file
Generated: no

## 1. Scope

This specification defines the public HTTP contract for inspecting and operating the current systemd-backed Dubnium scheduler.

The API exposes schedule summaries, schedule detail, recent journal history, immediate trigger, pause, resume, and process health.

It does not define durable schedule authoring, Nix configuration, systemd unit generation, concurrency, retry policy, workflow orchestration, deployment authority, or repository mutation policy.

The canonical machine-readable artifacts are:

- `schemas/v1alpha/scheduler.schema.json`;
- `api/scheduler/v1alpha/openapi.json`;
- examples under `examples/scheduler-v1alpha/`;
- the bundle entry in `conformance/service-bundles.json`.

## 2. Administrative boundary

The current service does not enforce inbound authentication. A deployment MUST keep it on a trusted administrative boundary.

History and control routes MUST NOT be exposed directly to untrusted networks.

The API accepts schedule identifiers only through routes and resolves them against the configured schedule catalog before issuing systemd or journal commands.

## 3. Durable ownership

Durable schedules remain declarative system configuration.

The API does not create, edit, or delete durable definitions. Trigger, pause, and resume operate only on schedules already present in the service catalog.

## 4. Inspection

`GET /healthz` returns bounded process health.

`GET /schedules` returns normalized schedule summaries.

`GET /schedules/{schedule_id}` returns one normalized schedule definition or `404` when the identifier is unknown.

Schedule responses may include descriptive dispatch metadata. These fields do not grant authority and are not accepted as caller-controlled control input.

## 5. History

`GET /schedules/{schedule_id}/history` invokes `journalctl` for the catalogued service unit with a line limit of 20.

The current implementation returns up to 20 parsable JSON records from command standard output. Journal fields are implementation-defined and MAY change.

The current implementation does not redact returned journal fields and does not impose a separate response-byte limit. Deployments therefore MUST treat this endpoint as sensitive administrative output and control upstream logging accordingly.

Malformed journal lines are skipped. The current response does not attest that the journal command succeeded.

## 6. Controls

`POST /schedules/{schedule_id}/trigger` issues `systemctl start` for the catalogued service and returns status `started`.

`POST /schedules/{schedule_id}/pause` issues `systemctl mask` for the catalogued timer and returns status `paused`.

`POST /schedules/{schedule_id}/resume` issues `systemctl unmask` for the catalogued timer and returns status `resumed`.

These responses report that the command was issued by the current service. They do not attest that systemd completed the requested state transition successfully.

Pause and resume do not alter the declarative schedule source. A subsequent system rebuild MAY restore declarative state.

## 7. Errors

Unknown schedules return `404`.

This profile does not standardize every operational failure code. The current implementation may return a successful control envelope even when the underlying systemd command exits unsuccessfully; consumers MUST NOT treat the envelope as proof of unit state.

## 8. Compatibility

Schedule identifiers are opaque public identifiers. Consumers MUST NOT infer systemd unit names from them.

Changes to identifier interpretation, control meaning, or durable ownership are incompatible and require a reviewed contract revision.

## 9. Threat assumptions

Implementers MUST account for schedule-ID injection, unit-name traversal, arbitrary command execution, journal disclosure, unbounded log fields, unauthorized trigger, denial of service, and confusion between issued commands and confirmed state.

Conformance demonstrates contract behavior only; it does not validate the private scheduler catalog, systemd hardening, or host policy.
