# Project documentation

This fork develops genuine Riot Vanguard compatibility in Proton as an open
source effort to bring League of Legends back to Linux. It has a tested generic
Wine rundown-protection increment and a test-only x64 process-attachment
falsifier showing a gap in the current Wine implementation, followed by an
A1b shared-region result and a bounded raw-continuation prototype. A follow-up
tested VEH-caught fault recovery and native cleanup, then a bounded three-frame
x64 table-unwind experiment. A Clang x64 follow-up observes nested
compiler-generated `__finally` cleanup after arrival in B, with the recorded
compiler scope table and boundary limitations. Wine attachment, broader
execution-context compatibility, Vanguard acceptance and League gameplay
remain unproven. A separate opt-in x64 kernel-allocation experiment now passes
its added generic checks against the retained baseline; it backs allocations
within one driver-host process and does not provide cross-process executor
aliasing. A Linux x64 wineserver-backed private-mapping prototype also passes a
focused virtual-memory fixture, while foreign aliases and actual E05 reads
remain unsupported. The managed EXECUTOR bootstrap now validates a separate
physical host-runtime process with canonical ntdll and a bounded address
layout; foreign target aliases and E05 attach behavior remain unimplemented.
The project is independent of Riot Games,
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
| [Process-local kernel allocation experiment](evidence/2026-10-10-a1b-kernel-arena.md) | Opt-in section-backed x64 kernel allocations; no cross-process alias or attach behavior |
| [Private-mapping backing experiment](evidence/2026-10-10-a1b-private-backing.md) | Focused opt-in `MEM_PRIVATE` backing tests; no foreign aliases or E05 attach behavior |
| [A1b backing matrix and live-view experiment](evidence/2026-10-10-a1b-private-backing-matrix-and-live-view.md) | Private-backing matrix passed; managed TARGET to EXECUTOR live-view proof did not reach pointer checks |
| [Combined backing and kernel-arena integration](evidence/2026-10-10-a1b-backing-arena-integration.md) | Both opt-ins reach the service host in one assembled-artifact run; E05 attachment remains unimplemented |
| [Managed TARGET layout experiment](evidence/2026-10-10-a1b-managed-target-layout.md) | Strict Linux AMD64 guest-range admission and runtime descriptor; no executor role or attach behavior |
| [Managed EXECUTOR bootstrap experiment](evidence/2026-10-10-a1b-managed-executor.md) | Canonical host ntdll in a separate Linux AMD64 process; no target aliases or attach behavior |
| [Proposed attachment-backing decision](evidence/2026-10-10-a1b-attach-backing-design.md) | Staged mapping-backing proposal and E05 acceptance gates |
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
