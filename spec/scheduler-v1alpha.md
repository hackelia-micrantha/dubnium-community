# Scheduler API v1alpha

Status: experimental
Content: normative
Canonical source: this file
Generated: no

## 1. Scope

This specification defines the public HTTP contract for inspecting and operating the current systemd-backed Dubnium scheduler.

The API exposes schedule summaries, schedule detail, recent journal history, immediate trigger, pause, resume, and health.

It does not define durable schedule authoring, Nix configuration, systemd unit generation, concurrency, retry policy, workflow orchestration, deployment authority, or repository mutation policy.

The canonical machine-readable artifacts are:

- `schemas/v1alpha/scheduler.schema.json`;
- `api/scheduler/v1alpha/openapi.json`;
- examples under `examples/scheduler-v1alpha/`;
- the bundle entry in `conformance/service-bundles.json`.

## 2. Administrative boundary

The current service does not enforce inbound authentication. A deployment MUST keep it on a trusted administrative boundary.

History and control routes MUST be treated as operator operations. They MUST NOT be exposed directly to untrusted networks.

The API MUST NOT accept arbitrary commands, unit names, file paths, shell fragments, calendar expressions, or repository coordinates from control requests.

## 3. Durable ownership

Durable schedules remain declarative system configuration.

The API MUST NOT create, edit, or delete durable schedule definitions. Trigger, pause, and resume operate only on schedules already present in the service catalog.

A conforming implementation MUST resolve schedule identifiers through its catalog before invoking systemd.

## 4. Health and inspection

`GET /healthz` MUST report only bounded process health.

`GET /schedules` MUST return normalized schedule summaries.

`GET /schedules/{schedule_id}` MUST return one normalized schedule definition or `404` when the identifier is unknown.

Inspection responses MUST NOT expose credentials, environment variables, private host topology, unrelated unit configuration, or unbounded command output.

## 5. History

`GET /schedules/{schedule_id}/history` returns recent journal entries for the schedule.

Journal entry fields are implementation-defined and MAY change. The response MUST remain bounded in count and size.

The service MUST filter history by the catalogued schedule unit and MUST NOT accept a caller-provided journal selector.

History output SHOULD remove credentials and secrets when upstream units accidentally emit them.

## 6. Trigger

`POST /schedules/{schedule_id}/trigger` starts the catalogued schedule service immediately.

The service MUST resolve the identifier before invoking systemd and MUST NOT derive a unit name by concatenating unvalidated caller text.

A successful trigger MUST return status `started`.

## 7. Pause and resume

`POST /schedules/{schedule_id}/pause` masks the catalogued schedule timer and MUST return status `paused`.

`POST /schedules/{schedule_id}/resume` unmasks the catalogued schedule timer and MUST return status `resumed`.

Pause and resume do not alter the declarative schedule source. A subsequent system rebuild MAY restore the declarative state.

## 8. Dispatch metadata

Schedule responses MAY include bounded dispatch metadata identifying a backend class, target, and payload file.

These fields are descriptive. They MUST NOT grant authority and MUST NOT be accepted as caller-controlled control input.

Private credentials, tokens, and unrestricted filesystem paths MUST NOT be published through dispatch metadata.

## 9. Errors

Unknown schedules MUST return `404`.

Systemd or journal failures SHOULD use bounded service errors and MUST NOT expose unrestricted stderr, environment variables, or private unit contents.

This profile does not standardize every operational failure code. Implementations MAY add bounded `5xx` responses while the contract remains experimental.

## 10. Compatibility

Schedule identifiers are opaque public identifiers. Consumers MUST NOT infer systemd unit names from them.

Additive response fields MAY appear where schemas allow them. Changes to identifier interpretation, control meaning, or durable ownership are incompatible and require a reviewed contract revision.

## 11. Threat assumptions

Implementers MUST account for schedule-ID injection, unit-name traversal, arbitrary command execution, journal disclosure, unbounded output, unauthorized trigger, denial of service, and confusion between temporary control and declarative state.

Conformance demonstrates contract behavior only; it does not validate the private scheduler catalog, systemd hardening, or host policy.
