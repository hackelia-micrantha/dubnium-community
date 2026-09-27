# Add Operator Gateway sender-bound authentication v1alpha

Status: experimental
Content: informative
Canonical source: this file
Generated: no
Compatibility: additive experimental contract

## Summary

Adds the public Dubnium application-authentication contract for Operator Gateway client-visible routes.

The profile requires both a Dubnium-validated client credential and Keylix-verified DPoP sender binding. It prohibits Bearer fallback, tailnet-only identity, request-body identity, and unverified forwarding metadata.

## Added

- a strict compact-JWS Dubnium client credential profile using Ed25519 / EdDSA;
- issuer, audience, lifetime, active-client, revocation, token-type, scope, and trusted `cnf.jkt` validation requirements;
- exact presented-credential correlation into the Keylix sender-binding boundary;
- immutable `ValidatedCredential + VerifiedSenderBinding -> CallerIdentity` composition;
- durable fail-closed replay requirements for the single-verifier deployment profile;
- the trusted effective-target and local-only `/healthz` publication boundary;
- explicit browser/WebAssembly key-custody constraints;
- a canonical JSON Schema for the signed credential claims object.

## Authority boundary

This contract defines authentication only. It does not grant endpoint authorization, runner or diagnostic authority, Capability Gateway authority, Anthesis approval, mutation authority, or arbitrary execution.

Keylix remains the sender-binding authority; Dubnium remains responsible for credential validation and application identity composition.

## Compatibility

This is a new experimental v1alpha contract. It does not change an existing stable wire contract. Future incompatible changes require a reviewed contract revision.
