# Specifications

Status: experimental
Content: informative
Canonical source: this file
Generated: no

`spec/` contains normative Dubnium-owned protocol specifications.

Specifications may reference canonical schemas and external standards. They MUST NOT depend on implementation packages, private source, operator configuration, or generated site output.

Each specification identifies its stability level, contract version, normative scope, external authority boundaries, compatibility behavior, threat assumptions, and canonical machine-readable artifacts.

## Service specifications

| Specification | Status | Transport binding |
| --- | --- | --- |
| `capability-gateway-v1.md` | v1alpha | `api/capability-gateway/v1/openapi.json` |
| `memory-service-v1alpha.md` | experimental | `api/memory-service/v1alpha/openapi.json` |
| `supervisor-gateway-v1alpha.md` | experimental | `api/supervisor-gateway/v1alpha/openapi.json` |
| `scheduler-v1alpha.md` | experimental | `api/scheduler/v1alpha/openapi.json` |

Experimental HTTP specifications SHOULD be enrolled in `conformance/service-bundles.json` with their schemas and synthetic examples.
