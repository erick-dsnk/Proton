# Security policy

This experimental fork develops Vanguard compatibility in Proton. It does
not claim the security properties of a native Windows anti-cheat environment,
an accepted Vanguard session, or playable League. The implementation and
trust boundaries must be assessed on their actual behavior.

## Reporting a vulnerability

GitHub private vulnerability reporting is enabled for this repository. Use
[Report a vulnerability](https://github.com/erick-dsnk/Proton/security/advisories/new)
to send a private report to the repository maintainer. Do not publish sensitive
exploit details, credentials, personal information, or proprietary binaries
in a public issue while arranging disclosure.

Include the affected Proton and component SHAs, host/build environment,
reproduction steps, expected and observed behavior, impact, and redacted logs.
Prefer a minimal benign fixture that demonstrates the issue. Explain whether
the finding affects this fork's patch, inherited code, or a third-party
component. The maintainer will assess the report and coordinate a fix and
appropriate disclosure; this volunteer project has no guaranteed response
or remediation deadline.

For an upstream component vulnerability, use that component's current private
security-reporting policy as well when appropriate, and identify any related
report so maintainers can coordinate. A flaw in Riot's proprietary software
belongs in Riot's official security-reporting process; this fork's maintainer
cannot act on Riot's behalf.

## Supported versions and updates

There are no supported stable Vanguard-compatible releases. Current `main` is
the development target for fixes in this effort, with component commits pinned
by Git submodules. Reports concerning older revisions are still useful when
the affected revision and current reproducibility are stated. Upstream
components have their own support policies.

Driver compatibility changes can affect process memory, synchronization,
lifetimes, and system boundaries. Review them using generic regression tests
and the evidence gates in [docs/TESTING.md](docs/TESTING.md). A passing
repository check does not establish isolation, native kernel semantics,
attestation, or vendor acceptance. Keep experimental testing reproducible and
separate from claims of production readiness.
