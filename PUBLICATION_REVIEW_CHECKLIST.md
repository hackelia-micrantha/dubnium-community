# Public Publication Review Checklist

Status: experimental  
Content: informative  
Normative boundaries: [PUBLICATION_BOUNDARY.md](PUBLICATION_BOUNDARY.md), [LICENSING.md](LICENSING.md), [SECURITY.md](SECURITY.md)

Use this checklist before publishing documentation, examples, slides, demos, design-partner findings, generated artifacts, or private-to-public candidate material.

This checklist summarizes review questions; it does not replace the repository's normative publication, licensing, security, compatibility, or contribution rules.

## Ownership and provenance

- [ ] The material has a clear owner and the repository has the right to publish it.
- [ ] Third-party source, documentation, data, models, images, and generated content are identified.
- [ ] Required licenses, notices, attribution, and contribution requirements are satisfied.
- [ ] Materially AI-generated/assisted content has been reviewed for provenance and accidental copying where applicable.
- [ ] Patent/trade-secret implications have been considered before irreversible disclosure.

## Private and customer information

- [ ] No customer, employer, design-partner, or individual confidential information is present.
- [ ] No private repository coordinates, branches, commits, issues, workflow/run IDs, or internal paths are present unless explicitly permitted by the publication policy.
- [ ] No private pricing, negotiations, contracts, unpublished roadmap commitments, or procurement information is present.
- [ ] Real findings have been generalized and replaced with synthetic examples where possible.

## Credentials and identity

- [ ] No passwords, API keys, tokens, certificates, recovery material, secret values, or encrypted secret blobs are included.
- [ ] Secret names or metadata do not unnecessarily reveal sensitive security architecture.
- [ ] Hostnames, usernames, addresses, endpoint identities, VPN identities, and trusted actors have been removed or intentionally approved.

## Security and topology

- [ ] No production topology, private network ranges, ports, service coordinates, device topology, or runner mappings are disclosed unnecessarily.
- [ ] No production policy thresholds, allowlists, exceptions, approval mappings, bypass details, or escalation rules are disclosed.
- [ ] No privileged provider/worker internals, recovery mechanisms, or operational controls are exposed beyond the accepted public boundary.
- [ ] Threat-model examples are useful without becoming a deployment bypass guide.

## AI, model, and data boundaries

- [ ] No production prompts, routing heuristics, retry/fallback behavior, private evaluation corpora, memory contents, ranking signals, or customer context are included.
- [ ] Model/runtime/data licenses and provenance are compatible with the intended public use.
- [ ] Examples do not imply commercial eligibility, certification, or support merely because a model/runtime is technically usable.

## Logs, evidence, and measurements

- [ ] No real logs, traces, incidents, crash dumps, evidence records, environment dumps, or source content are included without explicit review.
- [ ] Measurements are sanitized and do not reveal private infrastructure or exploitable limits.
- [ ] Screenshots and recordings have been checked for terminals, paths, usernames, notifications, browser tabs, credentials, and background content.

## Compatibility and claims

- [ ] Experimental versus stable status is explicit.
- [ ] The material does not claim unsupported deployment forms, certification, SLA, compatibility, or general availability.
- [ ] Public contracts are not silently extended or reinterpreted by examples.
- [ ] Organizational/community participation is not presented as endorsement.

## Generated and staged output

- [ ] The complete generated/staged artifact—not only source Markdown—has been reviewed.
- [ ] Unexpected files, symlinks, executables, source maps, debug output, and metadata are absent or explicitly approved.
- [ ] Generated links do not expose private/local endpoints or edit-source URLs.
- [ ] Size/path/file-count limits and repository-specific validators pass.

## Final decision

- [ ] The material is useful to a public reader without private context.
- [ ] Disclosure is intentional and understood to be effectively irreversible.
- [ ] Any uncertainty about ownership, licensing, patent/trade-secret status, security exposure, or confidential information has been resolved before publication.
