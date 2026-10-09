# Project documentation

This fork develops genuine Riot Vanguard compatibility in Proton as an open
source effort to bring League of Legends back to Linux. It currently has a
tested generic Wine rundown-protection increment. Vanguard acceptance and
League gameplay remain unproven. The project is independent of Riot Games,
Valve, and Wine upstream.

| Start here | Purpose |
|---|---|
| [Project overview](../README.md) | Mission, current limits, upstream Proton context |
| [Implementation register](vanguard-implementation-progress.md) | Published revisions, observed results, remaining evidence |
| [Roadmap](ROADMAP.md) | Ordered work, dependencies, completion gates |
| [Architecture](ARCHITECTURE.md) | Proposed execution model and decisive experiments |
| [Building](BUILDING.md) | Clone, submodules, isolated Wine build, full Proton integration |
| [Testing](TESTING.md) | Generic conformance, reference comparisons, outcome reporting |
| [Runtime configuration](RUNTIME.md) | Inherited Proton environment options and logging |
| [Evidence convention](evidence/README.md) | Reproducible records and decision templates |
| [Frozen feasibility study](vanguard-linux-feasibility.md) | 9 October 2026 target/package/source investigation and E00–E12 backlog |

Contributor and community conventions live in [CONTRIBUTING](../CONTRIBUTING.md),
[GOVERNANCE](../GOVERNANCE.md), [CODE_OF_CONDUCT](../CODE_OF_CONDUCT.md),
[SECURITY](../SECURITY.md), [SUPPORT](../SUPPORT.md), and
[LICENSES](../LICENSES.md). Changes are summarized in the [changelog](../CHANGELOG.md).

The inherited technical guides remain useful for the underlying compatibility
stack. Their presence does not establish Vanguard support:

- [Debugging on Linux](DEBUGGING-LINUX.md) and [Windows crash debugging](DEBUGGING-WINDOWS.md).
- [Rebasing tips](REBASING_TIPS.md) for maintaining the fork and its Wine changes.
- [Controllers](CONTROLLERS.md), [hybrid graphics/PRIME](PRIME.md),
  [ICMP echo](ICMP_ECHO.md), and [thread priority](THREAD_PRIORITY.md).

Keep the feasibility study's original inputs and findings intact. Put new
observations in dated experiment records and update the implementation register
with their scope; describe a hypothesis as a hypothesis until tested.
