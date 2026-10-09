# Repository guidance for coding agents

This is the `erick-dsnk/Proton` community effort to implement Riot Vanguard
compatibility in Proton and bring League of Legends back to Linux. It is
experimental and independent of Riot Games and Valve. Accepted Vanguard
sessions and playable League are unproven.

## Read and scope the work

Read [README.md](README.md), [CONTRIBUTING.md](CONTRIBUTING.md), the relevant
component conventions, [docs/TESTING.md](docs/TESTING.md), and the current
[implementation record](docs/vanguard-implementation-progress.md) before
changing compatibility behavior. Use [docs/ROADMAP.md](docs/ROADMAP.md) and
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) to identify dependencies. Preserve
other contributors' changes; inspect status and stage explicit paths only.

Implement correct contracts with benign fixtures. Never treat a stubbed
success, exported name, passing build, or repository CI as proof of Vanguard
acceptance. Do not disable checks, fabricate security evidence, hide host
state, modify proprietary target binaries, or commit vendor binaries or
credentials. Keep executable filenames and API identities unchanged.

## Components and publication

`wine/` is a Git submodule with its own commits. Commit and publish component
changes to an accessible component repository before updating the parent
Proton gitlink. Verify a clean clone can retrieve the referenced commit.
Inspect parent and component diffs independently. Preserve component licenses
and authorship. Keep upstream synchronization and unrelated dependency
updates separate from a focused compatibility patch when possible.

## Build, test, and evidence

Use [docs/BUILDING.md](docs/BUILDING.md) for current build recipes. The
inherited full Proton build entry point is `make`; `make help` describes its
targets. Use the documented pinned SDK and an explicit experimental build
name such as `proton-vanguard-experimental`. A Wine-only build has a narrower
scope than a complete Proton build.

Record source/component SHAs, SDK tag/digest, architecture, commands, exit
status, log/artifact hashes, baseline comparison, failures, skips, and pending
native-reference checks. Check x86 calling conventions and structure layout
when relevant; x64 validation does not cover i386. Run tests that exercise the
changed contract and its lifetime/failure behavior. Documentation and
repository checks are complementary to runtime evidence.

Update the implementation record and affected status documentation when
results change. Report compilation, generic conformance, local operation,
accepted session, and gameplay as separate facts. Leave unresolved gates
explicit. Use primary sources and distinguish observed facts, documented
requirements, hypotheses, conditional relevance, and unknowns.

For local repository checks, create a disposable venv, install
`PyYAML==6.0.3`, and run `python scripts/check_repository.py` using that venv's
Python. Also run `bash -n configure.sh` and `git diff --check`. These read-only
checks validate documentation, conventions, YAML, and shell syntax; they do not
replace builds or runtime experiments.
