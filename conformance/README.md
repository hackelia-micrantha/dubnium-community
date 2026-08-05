# Conformance

Status: experimental
Content: informative
Canonical source: this file
Generated: no

`conformance/` contains implementation-neutral suites, canonical vectors, and synthetic positive, negative, and adversarial fixtures.

Conformance targets are explicit. Remote targets are disabled by default, test execution is resource-bounded, and the suite MUST be capable of testing implementations other than the bundled reference.

A passing result is version- and profile-specific and does not imply security review, production suitability, endorsement, or certification.
