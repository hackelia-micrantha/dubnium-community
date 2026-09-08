# Reproducible Engineering

Dubnium aims to make engineering environments replaceable without turning every project dependency into permanent workstation state.

## Layered ownership

A useful mental model is:

```text
platform configuration
  -> operating system, security baseline, resource policy

portable user environment
  -> shell, editor, terminal, user-facing development preferences

project environment
  -> project-specific SDKs, compilers, dependencies, tools, and workflow requirements

trusted acceleration
  -> caches, builders, prebuilt artifacts, and remote capacity
```

The layers can use different tools, but their ownership should remain explicit.

## Immutable managed configuration is not a read-only user environment

NixOS and Home Manager deliberately make managed configuration reproducible, and many managed files are materialized from immutable Nix-store content. That does not mean legitimate application preferences and user state must be forced through a system rebuild.

Dubnium treats writable user configuration as a separate ownership problem. [Writable User Configuration](writable-configuration.md) describes the managed, local, custom, and adopted layers and the role of `configctl` in making drift and promotion visible.

The important reproducibility invariant is that writable state remains **classified**: a local preference does not silently become the managed source of truth, and a generated managed file is not edited in place merely because it is convenient.

## Desired developer path

A project should increasingly be able to approach:

```text
clone
-> enter declared environment
-> build
-> test
-> run
```

without depending on undocumented machine history.

## Reproducible does not mean trusted

A perfectly reproducible malicious dependency is still malicious. Supply-chain policy may therefore include:

- pinned source and dependency identities;
- reviewed trust roots for caches or artifacts;
- signatures, provenance, or attestations where they add value;
- controlled update and rollback behavior;
- visible failure when required trust evidence is unavailable.

The exact mechanisms can vary by deployment and project.

## Mutable state is classified, not ignored

Not everything should live in declarative configuration. Dubnium uses a conceptual state classification:

| Class | Meaning | Typical treatment |
| --- | --- | --- |
| Declarative | Reconstructable from reviewed configuration | Rebuild |
| Re-fetchable | Available again from another trusted source | Download or regenerate |
| Recoverable | Mutable or costly state worth preserving | Explicit backup and restore |
| Irreplaceable | Loss breaks identity, trust, or access | Separate recovery or escrow strategy |

A replaceable environment should be reconstructed from declared inputs plus explicitly restored state rather than depend on an opaque machine image.

## Performance is part of developer experience

Reproducibility should not require every task to rebuild the world. Shared immutable inputs, bounded caches, remote build capacity, and resource-aware scheduling can accelerate work as long as their trust and ownership boundaries remain explicit.