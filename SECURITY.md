# Security policy

Status: stable
Content: normative
Canonical source: this file
Generated: no

## Reporting a vulnerability

Do not disclose suspected vulnerabilities, credentials, private topology, bypass techniques, or sensitive evidence in a public issue or pull request.

Use GitHub's **Security** tab and private vulnerability reporting when available. When private reporting is unavailable, open a minimal public issue requesting a private maintainer contact without including technical details.

A useful private report includes:

- affected version, commit, contract, package, or publication;
- impact and realistic attacker prerequisites;
- minimal reproduction using synthetic data;
- whether secrets, private systems, or third parties may be affected;
- suggested mitigation, if known;
- disclosure constraints or deadlines.

## Scope

Security reports may cover:

- schema ambiguity, parser differentials, canonicalization, replay, or identity confusion;
- unsafe reference implementations or examples;
- conformance gaps that permit constraint widening or fail-open behavior;
- dependency, workflow, artifact, release, provenance, or attestation compromise;
- generated-site disclosure or active-content risks;
- accidental publication of private coordinates, topology, prompts, policy, incidents, logs, evidence, or personal data;
- trademark or compatibility claims that create unsafe trust assumptions.

Production Dubnium vulnerabilities that are not present in this public repository should be reported through the private product's security channel rather than described publicly here.

## Maintainer response

Maintainers will:

1. acknowledge receipt when the channel supports it;
2. assess scope and coordinate affected maintainers;
3. preserve evidence without expanding disclosure;
4. prepare a fix, mitigation, or contract clarification;
5. coordinate release and disclosure timing;
6. publish an advisory when public action is appropriate.

No response-time guarantee is offered while the project is incubating, but credible reports are prioritized.

## Safe research expectations

Use synthetic fixtures and systems you own or are authorized to test. Avoid privacy violations, service disruption, credential access, persistence, lateral movement, and public disclosure before maintainers can evaluate the report.
