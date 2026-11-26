# Governance and Safety

Dubnium treats automation as a request for bounded capability, not as ambient permission to act.

## Trust model

The conceptual flow is:

```text
intent
-> contract validation
-> authenticated actor and context
-> policy / approval decision
-> bounded capability
-> effect
-> durable outcome and evidence
```

Each stage has a distinct responsibility:

- **Intent** states the requested outcome without granting authority.
- **Contract validation** rejects malformed, ambiguous, or incompatible requests.
- **Identity and context** bind the request to trusted transport or enrollment facts rather than model assertions.
- **Policy / approval decision** determines whether the exact request is allowed, denied, constrained, or requires approval.
- **Bounded capability** receives only the scope needed for the authorized operation.
- **Effect execution** performs the domain operation without widening the decision.
- **Outcome and evidence** record enough durable state to inspect what happened.

## Security properties

Public Dubnium work emphasizes:

- deny-by-default capability access;
- least privilege and explicit effect boundaries;
- deterministic validation and canonicalization;
- clear separation between policy authority and effect execution;
- no automatic widening when a dependency is unavailable;
- synthetic adversarial fixtures and implementation-neutral conformance;
- reviewable compatibility and security changes;
- no-effect reference implementations where real effects would create unnecessary risk.

## Identity and posture are policy inputs

Network reachability, authenticated identity, endpoint posture, and attestation can constrain a decision. They are not universal permission for privileged effects. Unsupported or stale posture should remain visible rather than being treated as success.

## Multi-user and external account direction

Dubnium is exploring authenticated users, isolated workspaces, workload identities and explicitly authorized external account use. Application sign-in, access to third-party accounts, operation authorization and execution evidence remain distinct concerns. User or workspace membership does not grant unrestricted access to a host or to another user's provider account.

This is a planned direction, not a supported multi-tenant service or a commitment to a particular identity provider.

## Private connectivity and remote access

Private connectivity and authenticated remote access are deployment choices, not capability grants. Encrypted network transport may reduce exposure to untrusted networks, but it does not establish endpoint trust, authorize an operation, or guarantee anonymity or leak-free routing. Each deployment requires its own threat model, identity, routing and failure-behavior qualification. The public architecture does not prescribe a particular network provider or topology.

## Public versus private governance

Public contracts may define request envelopes, decision references, authorized manifests, errors, evidence shapes, and compatibility rules.

Production policy, approval rules, thresholds, trusted identities, prompts, fallback behavior, provider wiring, audit records, and recovery procedures remain private. Publishing a contract does not publish the implementation or policy behind it.

## Relationship to Anthesis

Where Dubnium integrates with Anthesis, Anthesis remains authoritative for governance decision and approval semantics. Dubnium transports and enforces bounded decisions through its capability boundary; it does not redefine Anthesis policy authority in the public Dubnium contracts.
