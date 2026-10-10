# Proton Vanguard compatibility effort

An experimental, community-driven open source effort to implement support for
Riot Games' Vanguard in Proton, with the goal of bringing **League of Legends
back to Linux**.

This repository is [erick-dsnk/Proton](https://github.com/erick-dsnk/Proton), a
fork of [Valve's Proton](https://github.com/ValveSoftware/Proton). Proton runs
Windows games on Linux using Wine and other compatibility components. This
fork researches and implements the Windows driver contracts and platform
integration needed by Vanguard. It is an independent community project, with
no affiliation with or endorsement from Riot Games or Valve.

**League of Legends compatibility is a goal, not a delivered feature. There
is no demonstrated accepted Vanguard session or playable League session in
this fork.** There is no release recommended for normal League play.

## Current state

The first implementation adds eight ordinary rundown-protection APIs to
Wine's `ntoskrnl.exe`, with benign driver tests for admission, teardown,
waiting, concurrent use, and immediate release of a protected allocation.
The configured x64 Wine build and export checks succeeded. The comparison
against the same unpatched Wine baseline recorded:

| Generic NT kernel driver suite | Tests executed | Marked todo | Failures | Skipped |
|---|---:|---:|---:|---:|
| Unpatched baseline | 26,023 | 161 | 21 | 0 |
| Rundown patch | 34,156 | 161 | 21 | 0 |

The normalized failure messages were identical between runs. The patch added
8,133 assertions with no new failures or skips; the wider suite still has 21
baseline failures. This is evidence for a generic x64 compatibility increment.
Native Windows comparison, i386 execution, attached-process address-space
semantics, genuine platform acceptance, and Vanguard execution remain open.
A Wine-only build does not establish a complete Proton build or game support.

The test-only E05 attachment falsifier now shows that the current x64 Wine
implementation raises access violations for ordinary pointer reads around
attach/detach, including a target-only mapping. This result falsifies that
implementation's modeled attach behavior; it does not establish that Vanguard
reaches the API or rule out every user-space design. The bounded A1b
shared-region prerequisite now passes for three cooperative processes with
serial fresh leaf calls, coherent shared state and distinct private mappings.
The same continuation now resumes through caller/A/B/A/caller, and a narrow
VEH test catches one deliberate fault on the migrated stack. A separate
frame-based x64 experiment then runs table handlers and `RtlUnwindEx` through
three mapped frames, returns through the native bridge, cleans up, and permits
a later healthy continuation. A Clang x64 follow-up executes nested
compiler-generated `__finally` funclets after the continuation arrives in B,
unwinds through the mapped frames and returns through B's native bridge; the
same run preserves the E05 attachment todos. This only covers the recorded
compiler scope table and return-PC ranges. These are test-only execution
experiments; none implements Wine attach semantics or establishes Vanguard
call-path relevance or Linux platform acceptance. A separate managed EXECUTOR
experiment now boots canonical real ntdll in a clean Linux AMD64 Wine process,
but has no target aliases or attach behavior; E05 retains all eight
attachment todos. See the
[implementation record](docs/vanguard-implementation-progress.md) and
[architecture guide](docs/ARCHITECTURE.md#current-e05-result).

## Start here

- [Documentation index](docs/README.md): engineering guides and evidence records.
- [Feasibility study](docs/vanguard-linux-feasibility.md): pinned research inputs,
  interface gaps, architecture options, and acceptance gates.
- [Implementation progress](docs/vanguard-implementation-progress.md): source
  hashes, commands, artifacts, reviews, test results, and unresolved gates.
- [Roadmap](docs/ROADMAP.md) and [architecture](docs/ARCHITECTURE.md): next work
  and the contracts each approach must demonstrate.
- [Build guide](docs/BUILDING.md) and [testing guide](docs/TESTING.md): begin with
  reproducible generic fixtures before interpreting target-specific results.
- [Contributing](CONTRIBUTING.md), [governance](GOVERNANCE.md), and
  [code of conduct](CODE_OF_CONDUCT.md): how this community works.
- [Support](SUPPORT.md), [security reporting](SECURITY.md),
  [licenses](LICENSES.md), and [project changelog](CHANGELOG.md).

## Obtain the sources

```sh
git clone --recurse-submodules https://github.com/erick-dsnk/Proton.git proton
cd proton
git switch main
git submodule update --init --recursive
```

Submodule commits are part of every reproducible result. The Wine submodule
points to [erick-dsnk/wine](https://github.com/erick-dsnk/wine), which carries
this effort's Wine changes. Keep component changes in their component
repository, publish the component commit, and then update the Proton gitlink.
See [Contributing](CONTRIBUTING.md) before changing a submodule pointer.

The source layout retains Proton's upstream structure: `wine/` contains the
Windows compatibility runtime and benign NT driver tests; `proton` is the
launcher; `configure.sh`, `Makefile`, and `Makefile.in` coordinate container
builds; graphics, audio, media, and runtime dependencies live in their own
components. Project research and validation records live in `docs/`.

## Upstream relationship and scope

Keep general Windows compatibility fixes suitable for review by Wine and
Proton upstream. Preserve upstream attribution, component licenses, and the
original names of executable files and interfaces. Project branding belongs
in documentation and explicit experimental build names. Upstream Proton's
[release changelog](https://github.com/ValveSoftware/Proton/wiki/Changelog)
describes upstream releases; it is separate from this fork's
[CHANGELOG.md](CHANGELOG.md).

This effort aims at correct compatibility for unmodified software and genuine
platform integration. Work that disables anti-cheat checks, fabricates
security evidence, or conceals the host state is outside the project scope.
Riot acceptance may require vendor participation beyond what this repository
can deliver. Research results should make that boundary explicit.

For ordinary Steam gaming, use the Proton version provided by Steam. The
instructions below retain useful upstream build and runtime reference
material for developers of this experimental fork. Their presence does not
claim that a local build can run Vanguard or League.

Building Proton
---------------

The [build guide](docs/BUILDING.md) preserves the inherited container build,
installation, debug-symbol, and editor setup instructions, and documents the
smaller Wine-only driver harness. For a full integration build, initialize the
pinned submodules, configure the SDK, and use an experimental name:

```sh
make build_name=proton-vanguard-experimental install
```

Read the guide first: this installs a local Steam compatibility tool and
requires a working container engine. It does not establish Vanguard
acceptance or playable League. Use `make help` for inherited build targets and
[the testing guide](docs/TESTING.md) to record what was actually validated.

Runtime configuration
---------------------

See [docs/RUNTIME.md](docs/RUNTIME.md) for the inherited Proton environment
variables and compatibility options. They are developer reference material;
no runtime option documented here establishes Vanguard or League support.
