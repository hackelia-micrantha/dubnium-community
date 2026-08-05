# Publication review

Status: stable
Content: normative
Canonical source: this file
Generated: no

Any material derived from private work, third-party material, or generated output MUST pass this review before entering the public repository.

## Review record

The pull request records:

- candidate scope and public value;
- copyright owner and contributor authority;
- source and generation relationship;
- applicable licenses and notices;
- patent and trade-secret decision status;
- security and competitive-disclosure classification;
- exact staged file inventory and digests;
- validation performed;
- reviewer decision and intentionally excluded material.

Sensitive legal or product reasoning remains in a private record; the public pull request states that the required decision occurred without exposing confidential analysis.

## Required checks

### Ownership and provenance

- contributor has the right to publish;
- employer, client, contract, school, copied, adapted, translated, generated, and materially AI-assisted inputs are disclosed;
- third-party licenses and notices are compatible and complete;
- private Git history is not published by default.

### IP and competitive position

- patent filing, defensive publication, trade-secret retention, or no-patentable-subject decision is recorded before first disclosure;
- production heuristics, prompts, policy, memory intelligence, deployment mechanics, privileged controls, and operational evidence remain private unless separately approved;
- publication does not create unsupported compatibility, security, certification, or roadmap claims.

### Secrets and operational disclosure

Reject or sanitize:

- credentials, tokens, keys, encrypted secret blobs, secret names, and recovery material;
- usernames, personal information, hostnames, addresses, internal domains, local paths, ports, sockets, service accounts, and machine roles;
- private repositories, registries, package coordinates, workflow identifiers, run identifiers, and source edit links;
- trusted identities, allowlists, policy thresholds, exceptions, escalation mappings, and approval history;
- prompts, stored memory, incidents, logs, traces, real evidence, benchmarks, resource thresholds, and failure behavior.

### Artifact safety

- files are materialized into an isolated clean staging directory;
- traversal, collisions, case-folding conflicts, symlinks, devices, sockets, unexpected executables, and unsupported file types are rejected;
- archives are inspected before extraction and resource-bounded;
- generated JavaScript, source maps, images, fonts, and binary metadata are allowlisted and inspected;
- examples and fixtures are synthetic and cannot be mistaken for production values;
- canonical source and generated provenance markers are correct.

### Independent validation

The public repository validates incoming material independently. Producer tests or attestations are supporting evidence, not acceptance authority.

## Publication decision

A publication is accepted only when:

- the staged diff contains only reviewed material;
- all deterministic checks pass;
- a maintainer completes the human disclosure review;
- licensing and notices are unambiguous;
- compatibility and stability labels are accurate;
- rollback and incident-response implications are understood.

## Irreversibility

Publication is treated as irreversible. Reverting, deleting, or rewriting the repository cannot guarantee removal from clones, forks, caches, mirrors, package indexes, transparency systems, or logs.
