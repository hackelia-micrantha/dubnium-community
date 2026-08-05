# Licensing policy

Status: stable
Content: normative
Canonical source: this file
Generated: no

## Default license

Unless an explicit reviewed notice states otherwise, all repository content is licensed under the Apache License, Version 2.0 in `LICENSE`, including:

- source code and scripts;
- specifications and schemas;
- API descriptions;
- documentation and examples;
- conformance fixtures;
- generated public artifacts committed to this repository.

SPDX identifier: `Apache-2.0`.

A path-specific exception MUST include an adjacent license notice or machine-readable metadata, a provenance record, and maintainer approval. Silent license mixing is prohibited.

## Why Apache-2.0

Apache-2.0 is retained for the initial public monorepo because it provides an explicit patent grant, supports broad protocol and SDK adoption, and keeps generated-code reuse straightforward. The primary Dubnium competitive boundary remains the private production runtime, policy, memory intelligence, privileged providers, host integration, and operational evidence.

Relicensing requires an architecture decision and confirmation that every affected contributor and third-party input permits the change.

## Contributions

Contributors retain copyright in their contributions and license them under the repository's applicable license. Each commit MUST include a `Signed-off-by` line certifying that the contributor has the right to submit the work under these terms.

Contributors MUST disclose material copied or derived content, employer or client ownership constraints, generated inputs, third-party licenses, and materially AI-assisted contributions that require provenance review. A sign-off does not cure missing rights.

## Specifications and implementations

Publishing a specification does not publish or license a private production implementation. Implementers may create independent compatible implementations under the Apache-2.0 patent and copyright terms, subject to the separate trademark policy.

## Third-party material

Third-party code, schemas, examples, media, datasets, or generated assets MUST NOT be added until:

- the source and copyright owner are recorded;
- license compatibility is confirmed;
- required attribution and notices are included;
- modification and redistribution obligations are understood;
- the material has passed security and disclosure review.

Required notices are maintained in `THIRD_PARTY_NOTICES.md` or adjacent to the affected path.

## Patents, trade secrets, and disclosure

Before first public disclosure of material derived from private work, maintainers MUST record a private decision to file, defensively publish, retain as a trade secret, or proceed because no patentable or strategically confidential subject was identified.

Public disclosure is treated as irreversible. Deleting or reverting material does not restore confidentiality.

## Trademarks

Apache-2.0 does not grant permission to use project names, logos, compatibility marks, or certification language in a manner that implies endorsement. See `TRADEMARKS.md`.
