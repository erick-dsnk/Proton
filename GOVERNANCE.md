# Governance

This repository is an independent open source effort to implement Vanguard
compatibility in Proton, with the goal of returning League of Legends to
Linux. It is not affiliated with Riot Games or Valve. No accepted Vanguard
session or playable League session has been demonstrated here.

## Maintainer and decisions

The initial maintainer is repository owner
[@erick-dsnk](https://github.com/erick-dsnk). The maintainer reviews and merges
changes, manages repository settings and releases, and enforces the
[code of conduct](CODE_OF_CONDUCT.md). Contributors participate through issues,
pull requests, documentation, and reproducible experiments. There is no
separate steering committee or guaranteed review schedule.

Discuss meaningful changes to architecture, trust boundaries, dependency
ownership, or release claims in an issue or design document before treating
them as settled. Include the Windows contract, Linux implementation model,
limits, falsification experiment, and evidence needed to decide. Record the
decision and its rationale in the relevant document, with links to discussion.
The maintainer makes the final repository decision after considering the
available evidence. Disagreement should address behavior and evidence,
respectfully and in public where the material is suitable for public sharing.

Maintainer responsibilities may be expanded by an explicit repository change
naming a consenting contributor and their scope. Commit access does not imply
affiliation with an upstream project or a vendor.

## Engineering scope

The project prioritizes correct generic NT driver contracts, reproducible
reference tests, coherent execution and memory semantics, and genuine
platform integration. Work must preserve the distinction between compilation,
API conformance, local driver/service operation, an accepted anti-cheat
session, and connected gameplay. Follow the gates in the
[feasibility study](docs/vanguard-linux-feasibility.md) and
[roadmap](docs/ROADMAP.md).

Disabling anti-cheat checks, concealing the real host state, fabricating
security evidence, and redistributing proprietary target binaries are outside
the scope. Vendor acceptance may require Riot participation. That dependency
must remain explicit even when local compatibility improves.

## Upstream and component ownership

The fork retains Proton's source structure, licenses, and upstream attribution.
Wine, DXVK, and other dependencies have their own maintainers, policies, and
licenses. Generic changes should be prepared for upstream review where
appropriate, with a link to any submission and its actual disposition.
Upstream submission, upstream acceptance, and integration into this fork are
separate events.

Keep upstream synchronization on a reviewed branch. Record the upstream base,
component pins, preserved project patches, and regression results before
merging it. Do not rewrite public `main` history as part of an ordinary sync.
Publish a component commit before updating its Proton gitlink. See
[contributing](CONTRIBUTING.md) and [rebasing tips](docs/REBASING_TIPS.md).

## Releases and status claims

The maintainer may publish experimental development artifacts when source,
build inputs, license obligations, and known limitations are recorded.
Experimental builds must use a distinguishable build name. A release label or
passing repository CI is not evidence of Vanguard acceptance or playable
League. Any future support claim must link to reproducible gate-specific
results, state the tested versions and environment, and describe unresolved
regressions. Changes in verified support belong in the
[changelog](CHANGELOG.md) and implementation record.
