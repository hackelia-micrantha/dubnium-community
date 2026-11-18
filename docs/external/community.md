# Community and Contributions

The [Dubnium Community repository](https://github.com/hackelia-micrantha/dubnium-community) is the published source of truth for:

- the project website and generated Technical Overview;
- specifications, schemas, and API descriptions;
- conformance tests and synthetic fixtures;
- no-effect references, examples, and published tooling;
- compatibility, security, governance, contribution, and release policies;
- the bounded roadmap.

## Choose an entry point

- **Engineering teams and employers:** examine the [system architecture](architecture.md), [runner design](runner-controller.md), and [governance model](governance.md) to understand the engineering decisions and trade-offs.
- **Open-source contributors:** start with the [conformance suites](https://github.com/hackelia-micrantha/dubnium-community/tree/main/conformance), [no-effect reference](https://github.com/hackelia-micrantha/dubnium-community/tree/main/reference) and [contribution guide](https://github.com/hackelia-micrantha/dubnium-community/blob/main/CONTRIBUTING.md).
- **Design and integration partners:** use the [design-partner guide](https://github.com/hackelia-micrantha/dubnium-community/blob/main/DESIGN_PARTNER_GUIDE.md) to identify real reproducibility, isolation, private AI or integration constraints.
- **Investors and strategic collaborators:** explore the [community and commercial boundary](https://github.com/hackelia-micrantha/dubnium-community/blob/main/COMMUNITY_COMMERCIAL_BOUNDARY.md) and [Micrantha collaboration overview](https://github.com/hackelia-micrantha/.github/blob/main/profile/README.md#looking-for-collaborators). Potential supported products and services are opportunities for validation, not existing offers.

## Contribution boundary

Contributions should target published contracts, conformance, examples, conceptual documentation, release integrity, and independently useful tooling. A contribution must not depend on private source, private services, private registries, credentials, host configuration, operator data, or production policy.

Private-to-public imports receive additional review because publication is irreversible. Review covers ownership, licensing, patents, trade secrets, third-party provenance, secrets, operational disclosure, synthetic test data, generated metadata, and Git history.

## Documentation ownership

The Technical Overview is curated rather than mirrored. Every source file that enters the generated artifact must be explicitly allowlisted, and every Markdown page must be part of the reviewed navigation. Unlinked source files are not a supported disclosure mechanism.

The Community repository owns both the reviewed source and generated Technical Overview. Source changes and regenerated output are proposed together, with reproducibility and disclosure checks before deployment. The hand-maintained landing page and generated Technical Overview are separate artifacts with the same publication boundary but different detail levels.

## Reporting security issues

Use the private reporting process documented in the Community repository. Do not open a public issue containing a vulnerability, secret, sensitive topology, exploit evidence, or private implementation detail.
