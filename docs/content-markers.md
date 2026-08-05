# Content and source markers

Status: stable
Content: normative
Canonical source: this file
Generated: no

Public documents that define behavior, compatibility, policy, or generated-source relationships MUST begin with a visible metadata block:

```text
Status: experimental | v1alpha | v1beta | stable
Content: normative | informative
Canonical source: this file | <repository-relative path>
Generated: no | yes from <repository-relative path or public artifact identity>
```

## Normative content

Normative content defines requirements. It uses BCP 14 terms (`MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, `MAY`) only when those words carry requirement meaning.

Normative specifications live under `spec/` unless a repository-level policy file is the natural canonical location.

## Informative content

Informative content explains, illustrates, or records intent. It cannot silently override a normative contract. Examples and diagrams are informative unless explicitly incorporated by a normative requirement.

## Experimental content

Experimental content has no compatibility guarantee. Its metadata and release notes must make this visible. Experimental assets must not be described as stable, certified, production-ready, or supported merely because they are public.

## Canonical source

Each contract, schema, policy, and generated artifact has one editable canonical source. Generated outputs identify their source version or digest and MUST NOT become an alternate editable authority.

Generated public-site content under `site/` is never canonical specification or schema source.

## Generated files

A generated file or directory includes a machine-readable provenance marker when practical. The marker records:

- public artifact or publication identifier;
- generator name and version;
- canonical public source version or digest;
- output digest;
- generation timestamp;
- schema version for the provenance record.

Private repository coordinates, commits, workflow identifiers, local paths, and generation cadence are omitted by default. A disclosure exception requires explicit review.

## Conflict resolution

When content conflicts:

1. normative content prevails over informative content;
2. canonical source prevails over generated output;
3. the more specific versioned contract prevails over general description;
4. unresolved ambiguity fails closed and requires a contract correction.
