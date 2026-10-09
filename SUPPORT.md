# Support

This is a development and research effort to implement Riot Vanguard support
in Proton and bring League of Legends back to Linux. It has no demonstrated
accepted Vanguard session or playable League session. No build is currently
recommended for normal League play, and volunteer responses have no
service-level guarantee.

## Where to ask

Use this fork's [GitHub issues](https://github.com/erick-dsnk/Proton/issues)
for reproducible compatibility gaps, build problems, research questions, and
project proposals. Read the [documentation index](docs/README.md),
[build guide](docs/BUILDING.md), and [testing guide](docs/TESTING.md), and search
existing issues first. Follow the [code of conduct](CODE_OF_CONDUCT.md).

A useful report includes the exact Proton and affected component SHAs, host
architecture and distribution, SDK identity, reproduction commands, observed
behavior, expected contract, and redacted output. State whether the result is
from a generic fixture or from actual target execution. Use the issue template
that matches the work. Do not attach proprietary Riot binaries, account data,
tokens, serial numbers, or unredacted personal paths where they identify you.

Use [CONTRIBUTING.md](CONTRIBUTING.md) for patches and evidence contributions.
Report vulnerabilities according to [SECURITY.md](SECURITY.md).

## Boundaries

This project cannot provide official Riot account support, guarantee account
outcomes, or change Riot's platform-verification policy. Use Riot's official
support channels for account and vendor-service matters. Ordinary upstream
Proton game issues belong with the relevant upstream project unless they
reproduce specifically in this fork. Identify that boundary in reports so the
right maintainers can assess them.

There is no installation shortcut or runtime option documented here that
establishes League support. The [roadmap](docs/ROADMAP.md) describes the
remaining engineering and acceptance gates; the
[implementation record](docs/vanguard-implementation-progress.md) states what
has actually been validated.
