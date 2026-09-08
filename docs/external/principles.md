# Principles

Dubnium is guided by system-level principles that apply across workstation, client, compute, automation, and AI-assisted deployments.

## Declarative intent before accumulated setup

Long-lived configuration should be declared, reviewable, and reproducible. A working machine should not depend on undocumented installation history.

## Desired state is not observed state

Configuration says what should be true. Runtime observation says what is true now. A transition, deployment, or workflow is not successful merely because it was requested.

## Local-first, not local-only

Endpoints should remain useful, diagnosable, and recoverable with local resources. Remote services may extend the system through explicit compatibility, privacy, security, and availability boundaries.

## Capabilities instead of ambient authority

A caller should request a bounded capability rather than inherit broad host, network, data, device, credential, or tool access.

## Reachability is not authorization

Network location, VPN membership, endpoint health, and authenticated identity are useful security inputs. None of them alone grants authority for an unrelated or privileged effect.

## Durable domain state before log reconstruction

Workflows, approvals, automated operations, and other stateful domains should own their exact records. Logs and events provide evidence; they should not be forced to become a substitute database.

## Structured evidence before generated narrative

Reports and summaries should be derived from bounded structured evidence. AI may help synthesize that evidence, but it should not decide what may be collected, retained, or exported.

## Reproducibility is not supply-chain trust

Pinned inputs make behavior easier to reproduce. Trust still requires explicit provenance, verification, update, and dependency policy appropriate to the deployment.

## Bounded resource use

Interactive development, background automation, builds, and AI workloads should coexist intentionally. Resource contention, disk growth, and runaway work are operational concerns to design for rather than surprises to tolerate.

## Personal observability is not organizational surveillance

A system can help its operator understand work without covert productivity monitoring. Personal reports and journals require a separate ownership and sharing boundary from organizational endpoint posture.

## Contracts before coupling

Public and private consumers should depend on versioned contracts, canonical behavior, and conformance evidence rather than production implementation details.

## Safe public disclosure

Public artifacts should be independently useful while revealing no private topology, credentials, privileged implementation, policy internals, operator data, or private provenance. Publication is an irreversible security and intellectual-property decision.
