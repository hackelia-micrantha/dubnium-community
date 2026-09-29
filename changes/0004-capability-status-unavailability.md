# Declare retryable status-inspection unavailability

Status: v1alpha
Compatibility: compatible
Contracts: spec/capability-gateway-v1.md, api/capability-gateway/v1/openapi.json

## Behavior

Capability Gateway status inspection now explicitly distinguishes temporary service
unavailability from request absence. `GET /v1/capability-requests/{request_id}`
declares `503 Service Unavailable` using the existing RFC 9457 `Problem`
response in addition to `200` and `404`.

A `404` remains reserved for an unknown or no-longer-retained request identity.
Temporary ledger or runtime unavailability uses `503` with `retryable: true`.

## Security and authority

The correction prevents a transient internal failure from being represented as
request absence. It does not expose storage topology, implementation exceptions,
credentials, or additional request authority.

## Migration

Existing clients that already handle the shared `Problem` envelope may treat
`503` as a bounded retryable status-inspection failure. Clients that assumed
status inspection could return only `200` or `404` must add the declared
retryable `503` case.

No request, status, error, or canonicalization schema changes are required.

## Evidence

The Capability Gateway test suite asserts that the status-inspection OpenAPI
operation declares both `404` and `503` through the shared `Problem`
response. Contract-tree and release checks continue to validate the OpenAPI
reference graph.

## Private boundary

Ledger implementation, retry scheduling, service topology, socket paths, and
operational recovery remain private runtime concerns.
