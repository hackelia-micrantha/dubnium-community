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

## Optional public-network privacy layer

For users working from untrusted networks such as public Wi-Fi, a **separately operated, Headscale-managed exit node** can be an additional network-security layer around a Dubnium engineering endpoint. This is an **optional deployment pattern under qualification**, not a default Dubnium feature or a claim that every client platform is leak-proof.

Conceptually:

```text
Dubnium client on untrusted Wi-Fi
  -> encrypted Tailscale-compatible data-plane tunnel
  -> explicitly authorized home/router exit node
  -> Internet
       |
       +-- DNS resolved through the tunnel, subject to client policy
```

Headscale coordinates peer identity and route policy; it is **not** the ordinary browsing-traffic proxy. Network reachability and tailnet membership do not grant Dubnium capabilities, host access, runner authority, or private LAN permissions. The exit node must be explicitly authorized, with forwarding and firewall policy isolated from unrelated networks.

**What this can protect:** a public Wi-Fi operator should not see DNS queries or destination traffic carried *inside an established, correctly routed encrypted tunnel*. It can still see VPN connection metadata and traffic timing. The home ISP and any upstream DNS resolver retain visibility appropriate to the home egress and DNS configuration; an exit node does **not** provide anonymity.

**What remains to qualify:** DNS and IPv4/IPv6 leak behavior, client/browser resolver bypass, tunnel disconnect and reconnect, captive-portal bootstrap, mobile VPN-on-demand limits, exit-node recovery and rollback. Merely selecting an exit node is not a universal kill switch. If fail-closed routing cannot be enforced on a particular platform, users need that limitation stated rather than a guarantee of no leaks.

This layer is intentionally independent of Dubnium's capability authorization and of optional encrypted DNS upstream from the home network. Production-specific router topology, policy values, addresses, and activation procedures belong in private operator documentation.

## Public versus private governance

Public contracts may define request envelopes, decision references, authorized manifests, errors, evidence shapes, and compatibility rules.

Production policy, approval rules, thresholds, trusted identities, prompts, fallback behavior, provider wiring, audit records, and recovery procedures remain private. Publishing a contract does not publish the implementation or policy behind it.

## Relationship to Anthesis

Where Dubnium integrates with Anthesis, Anthesis remains authoritative for governance decision and approval semantics. Dubnium transports and enforces bounded decisions through its capability boundary; it does not redefine Anthesis policy authority in the public Dubnium contracts.
