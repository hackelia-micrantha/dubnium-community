# Operator Gateway authentication v1alpha

Status: experimental
Content: normative
Canonical source: this file
Generated: no

## Purpose

This contract defines the application-authentication boundary for Dubnium Operator
Gateway client routes. It does not define capability authorization, Anthesis policy,
runner semantics, diagnostics, mutation semantics, or Keylix's DPoP protocol.

Every client-visible `/v1/*` request requires both:

1. a valid Dubnium client credential using this profile; and
2. a Keylix `VerifiedSenderBinding` for the exact presented credential, request
   method, and externally addressed effective request target.

Authentication succeeds only after those two independently trusted results compose.
Tailscale membership, request-body identity, arbitrary forwarding headers, or a
DPoP proof by itself are never application identity.

The host-only `GET /healthz` liveness endpoint is not a client route and MUST
remain physically excluded from any remote publication path.

## Credential transport

A client sends exactly:

~~~text
Authorization: DPoP <credential>
DPoP: <proof>
~~~

`Bearer` and every other authorization scheme fail closed. Missing, repeated,
comma-joined, or otherwise ambiguous authorization/DPoP fields fail closed.

The exact UTF-8 bytes after `DPoP ` are the credential bytes supplied to the
Keylix protected-resource verifier for `ath` validation. Implementations MUST NOT
decode and reserialize the credential before computing or verifying sender binding.

## Dubnium credential profile

A v1alpha credential is a three-segment compact JWS:

~~~text
base64url(protected-header) "." base64url(claims) "." base64url(signature)
~~~

Base64url is RFC 4648 URL-safe encoding without padding. Non-canonical encodings,
empty segments, extra segments, oversized input, duplicate JSON member names, and
unknown members fail closed.

### Protected header

The protected header is exactly:

~~~json
{
  "alg": "EdDSA",
  "typ": "dubnium-client+jwt",
  "kid": "<configured issuer key id>"
}
~~~

Requirements:

- `alg` MUST equal `EdDSA`.
- The signing key MUST be Ed25519.
- `typ` MUST equal `dubnium-client+jwt`.
- `kid` MUST select one currently trusted issuer public key.
- No unprotected header participates in this profile.
- Unknown protected-header members fail closed.

The signature covers the original ASCII
`base64url(header) + "." + base64url(claims)` bytes.

### Claims

The claims object contains exactly:

~~~json
{
  "ver": 1,
  "iss": "urn:dubnium:operator-issuer:<deployment>",
  "sub": "principal:<stable-principal-id>",
  "aud": "urn:dubnium:operator-gateway:<deployment>",
  "client_id": "<stable-client-id>",
  "client_class": "mobile",
  "iat": 1700000000,
  "nbf": 1700000000,
  "exp": 1700003600,
  "jti": "<credential-id>",
  "token_type": "DPoP",
  "cnf": {
    "jkt": "<RFC-7638 P-256 thumbprint>"
  },
  "scopes": [
    "operator.health.read"
  ]
}
~~~

All fields are required. Unknown fields fail closed.

`client_class` is one of `mobile`, `web`, or `desktop-agent`. This is an
authenticated classification, not an authorization decision.

`scopes` is a bounded set of authenticated grant labels. Successful authentication
does not by itself prove that any endpoint or consequential effect is authorized.

### Validation

The Operator Gateway validates the exact presented credential before invoking the
Keylix sender-binding composition:

- exact supported credential version;
- exact issuer and audience from trusted host configuration;
- exact `EdDSA` / Ed25519 signature using the configured `kid`;
- `token_type == "DPoP"`;
- the configured credential clock tolerance is a non-negative duration no greater
  than 300 seconds in v1alpha;
- `iat <= nbf < exp` and `exp - iat <= 3600` seconds;
- the credential is not yet valid when `now + tolerance < nbf`;
- the credential is expired when `now - tolerance >= exp`;
- `iat > now + tolerance` is rejected as a future-issued credential;
- bounded identifiers and scope count/length;
- `cnf.jkt` is a syntactically valid base64url-no-pad 32-byte RFC-7638 SHA-256
  thumbprint;
- `client_id` exists in the active-client registry and maps to the signed
  `sub` and `client_class`;
- `jti` is not revoked;
- every required validation dependency is readable and internally consistent.

Missing or unreadable issuer configuration, active-client state, or revocation state
is an authentication outage, not permission to skip validation.

The v1alpha profile caps the signed credential lifetime at one hour. A deployment
that requires a different maximum must define a separately versioned and reviewed
profile rather than widening v1alpha at runtime.

## Trusted validation result

Credential parsing does not itself produce identity. Successful validation produces
a typed `ValidatedCredential` containing at least:

- a fingerprint of the exact presented credential bytes;
- `sub`;
- `client_id`;
- `client_class`;
- `scopes`;
- expiration time;
- trusted `cnf.jkt`;
- validation key id.

Raw credential bytes are retained only as long as required to perform exact-token
sender binding and MUST NOT appear in logs, metrics, errors, traces, model context,
or public evidence.

## Keylix composition

The Operator Gateway passes to the packaged Keylix verifier only the trusted host
inputs required by the reviewed verifier contract:

- exact HTTP method;
- trusted externally addressed effective target;
- exact credential bytes;
- exact DPoP proof;
- trusted `cnf.jkt` from `ValidatedCredential`.

Keylix verifies proof signature, `htm`, `htu`, freshness, `ath`, replay state,
nonce policy when enabled, and the proof-key / trusted-`cnf.jkt` binding.

The Gateway MUST fail closed if the verifier, replay state, nonce state, or local
authenticated verifier transport is unavailable or indeterminate.

The trusted effective target MUST come from a narrowly configured publication
adapter. Arbitrary `Forwarded`, `X-Forwarded-*`, `Host`, request-body, or
tailnet metadata cannot select the DPoP target used for verification.

## CallerIdentity construction

`CallerIdentity` is constructed only from:

~~~text
ValidatedCredential
    +
VerifiedSenderBinding(exact same credential, exact request)
    ->
CallerIdentity
~~~

The verified sender key thumbprint MUST equal the validated credential's trusted
`cnf.jkt`. The exact-credential correlation established by Keylix MUST be preserved.

The resulting identity contains authenticated principal attributes only. A minimum
shape is:

~~~text
principal_ref
client_id
client_class
authenticated_scopes
credential_expires_at
sender_key_thumbprint
~~~

No request JSON field, model output, forwarding header, tailnet identity, or
unverified token claim may override those fields.

A later authorization layer decides whether this authenticated identity may access
an endpoint or request an effect. For consequential effects, the identity is input
to the separately governed Operator Gateway -> Capability Gateway delegation
contract; it is not itself an Anthesis approval.

## Replay, restart, and process topology

DPoP replay acceptance state MUST survive Operator Gateway and verifier process
restarts for the full proof acceptance lifetime. The replay check-and-record
operation MUST be atomic for the deployed verifier topology.

A single verifier using owner-only persistent local replay state is conforming for
a single-host/single-verifier profile. Multi-instance deployment requires a shared
atomic replay backend or an explicitly reviewed single-writer/routing design.

Corrupt, unreadable, full, unavailable, or otherwise indeterminate replay state
fails closed.

## Effective-target publication boundary

Remote publication is disabled until the deployed proxy boundary can prove both:

- only authenticated `/v1/*` routes are published; and
- host-only `/healthz` cannot be reached through the remote listener/proxy.

The production adapter owns one configured external origin and reconstructs the
effective target from that trusted origin plus the already accepted request path.
Client-controlled forwarding headers never widen that authority.

## Browser/Web key custody

The Web/Wasm client may use this credential and DPoP protocol only through a
separately reviewed browser key-custody adapter.

- Plaintext private DPoP keys in `localStorage`, IndexedDB application records,
  cookies, source bundles, or serialized app state are not conforming.
- Browser custody is not claimed to be equivalent to Android Keystore or iOS
  Secure Enclave.
- Where non-exportable WebCrypto key storage cannot meet the deployment threat
  model, the browser profile remains unsupported rather than downgrading to Bearer
  or exportable plaintext keys.

## Failure posture

Authentication fails before resource dispatch for at least:

- missing, malformed, expired, not-yet-valid, wrong-audience, wrong-issuer, revoked,
  inactive-client, unsupported, or bad-signature credentials;
- Bearer or ambiguous authorization;
- missing/malformed DPoP;
- method or effective-target mismatch;
- wrong proof/token key binding or `ath`;
- stale/future proof;
- replay;
- verifier/replay/nonce/configuration unavailability.

Externally returned errors are bounded categories. Sensitive raw inputs are never
reflected.

## Non-goals

This contract does not define:

- client credential issuance UI or a general identity provider;
- endpoint authorization policy;
- runner status or diagnostic resources;
- Capability Gateway mediation;
- Anthesis policy;
- mutations or arbitrary command execution;
- generic proxy trust.
