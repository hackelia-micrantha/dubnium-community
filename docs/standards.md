# Public contract standards baseline

Status: stable
Content: normative
Canonical source: this file
Generated: no

The first public Dubnium contracts use established standards rather than project-specific equivalents where a suitable standard exists.

## Normative language

Normative requirements use BCP 14 terminology from RFC 2119 and RFC 8174. Uppercase `MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, and `MAY` carry requirement meaning only in content marked normative.

## Schemas and APIs

- JSON Schema Draft 2020-12 is the canonical JSON schema dialect.
- OpenAPI 3.1.2 is the initial HTTP API description baseline when an HTTP binding exists.
- Schema references resolve only within a reviewed, bundled graph by default. Remote resolution is disabled.
- Each schema uses stable `$id` and explicit contract-version metadata.

## Serialization and digests

- RFC 8785 JSON Canonicalization Scheme is used when a contract requires canonical JSON.
- SHA-256 is the v1 digest algorithm and uses contract-specific domain separation.
- Digest-bearing objects avoid arbitrary floating-point representations and other values with ambiguous cross-language serialization.
- Digest inputs, excluded fields, encoding, and expected vectors are normative and versioned.

## Time and identifiers

- RFC 3339 UTC timestamps are used with contract-defined precision and normalization.
- Identifiers define syntax, case sensitivity, normalization, length, uniqueness, and authority.
- Caller-controlled data cannot substitute for transport-derived or otherwise authoritative identity.

## Errors

HTTP bindings use RFC 9457 Problem Details plus stable, documented Dubnium error codes. Transport status, machine code, retryability, and human detail are distinct.

Error behavior fails closed for unknown versions, authority-bearing fields, identities, effects, constraints, canonicalization inputs, and digest semantics.

## Versioning and licensing metadata

- Coordinated repository releases follow Semantic Versioning 2.0.0.
- SPDX identifiers describe licenses.
- SPDX or CycloneDX may describe executable release SBOMs; release requirements are completed under issue #14.

## Deviations

A contract may deviate only when the normative specification records:

- the incompatible requirement or missing capability in the baseline standard;
- the exact replacement behavior;
- interoperability and security consequences;
- conformance vectors;
- migration expectations.

A convenience implementation detail cannot silently change the public contract.
