# Contributing

Help implement correct Vanguard compatibility in Proton so League of Legends
can return to Linux. This is an experimental open source effort; accepted
Vanguard sessions and playable League are unproven. Read the
[feasibility study](docs/vanguard-linux-feasibility.md),
[roadmap](docs/ROADMAP.md), and [current evidence](docs/vanguard-implementation-progress.md)
before selecting work. Follow the [code of conduct](CODE_OF_CONDUCT.md).

## Choose a bounded contribution

Use an issue to describe a reproducible gap, proposed contract, or research
question. Link existing work before opening a duplicate. Small patches that
implement a coherent Windows contract and include a benign regression fixture
are easier to review than broad import-table completion. Documentation,
native-reference measurements, build reproducibility, and test results are
valuable contributions.

Keep the next architectural question visible: correct ordinary pointer access
after process attachment must be demonstrated before expanding memory APIs
that depend on that behavior. Platform verification is a separate acceptance
gate. A successful return code or a resolved import is insufficient evidence
for an implemented contract.

Work that disables checks, hides the host environment, forges attestation,
modifies proprietary target binaries, or promises an undemonstrated playable
League session is outside the project scope. Use public contracts and genuine
measurements. Do not submit vendor binaries, accounts, tokens, or proprietary
code to this repository.

## Develop and publish a patch

1. Clone the fork and initialize the pinned submodules as described in the
   [README](README.md#obtain-the-sources). Create a focused topic branch from
   `main`; examples include `fix/rundown-wait` and `docs/windows-reference`.
2. Inspect the affected component and preserve its coding style and license
   notices. Keep executable/interface identities unchanged. Use an explicit
   experimental build name such as `proton-vanguard-experimental`.
3. For Wine changes, make and commit them in `wine/`, publish that commit to an
   accessible branch in the Wine fork, and record its SHA. A Proton gitlink
   alone cannot publish component code. Update the Proton pointer only after
   the referenced component commit is available to contributors.
4. Build and run the relevant benign fixtures using the [build guide](docs/BUILDING.md)
   and [testing guide](docs/TESTING.md). Compare the patch with the same unpatched
   baseline. Explain any failing, skipped, or `todo_wine` cases.
5. Update the relevant evidence record and user-facing status if results or
   limitations changed. Stage explicit paths and inspect both parent and
   component diffs; avoid including unrelated work or generated artifacts.
6. Open a pull request against this fork's `main`. State the concrete behavior,
   source/component SHAs, validation, limitations, and relationship to any
   issue or upstream patch. Use the repository pull request template.

A clean clone must resolve every new gitlink. Keep dependency updates separate
from compatibility changes unless the dependency is necessary to reproduce the
patch. Do not silently update a submodule to its latest branch tip.

## Required evidence

Record the baseline and patched revisions, SDK tag and digest, target
architecture, configuration, exact commands, exit status, artifact/log hashes,
and relevant test output. Logs referenced only on a contributor's machine are
local evidence; include a redacted shareable excerpt or artifact when others
need to assess the result. The [testing guide](docs/TESTING.md) defines the
comparison and evidence conventions.

Tests should exercise contract behavior, including failure, lifetime, race,
and cleanup cases where relevant. Check declarations, export signatures,
structure layout, and x86 calling conventions such as `FASTCALL`; an x64 build
does not validate i386. State native Windows comparison separately from Wine
baseline comparison. State a full Proton build separately from a Wine-only
build. Repository CI currently checks repository conventions and documentation;
it does not prove driver conformance, vendor acceptance, or gameplay.

Use primary documentation for API contracts and cite the version or retrieval
date for changeable requirements. Label observations, published requirements,
hypotheses, and unknowns. Never substitute a fake success result for behavior
that has not been implemented.

## Repository checks

Use a disposable virtual environment for the lightweight repository checks:

```sh
python3 -m venv /tmp/proton-vanguard-checks
/tmp/proton-vanguard-checks/bin/python -m pip install PyYAML==6.0.3
/tmp/proton-vanguard-checks/bin/python scripts/check_repository.py
bash -n configure.sh
git diff --check
```

The read-only `Repository checks` workflow validates first-party documentation,
local links and anchors, required convention files, issue forms, workflow YAML,
and shell syntax. It does not build the SDK, run Wine fixtures, execute
Vanguard, or establish gameplay. Record runtime evidence separately.

## Review and upstreaming

Maintainers review the contract, implementation, reproducibility, and claims.
They may request a smaller patch or additional evidence before merging. Generic
Wine/Proton fixes should remain suitable for upstream review; check existing
upstream changes before doing overlapping work. Preserve authorship and
provenance when importing patches. See [governance](GOVERNANCE.md) and
[rebasing tips](docs/REBASING_TIPS.md) for integration policy.

Contributions retain the license of the affected file or component. Read
[LICENSES.md](LICENSES.md). This project does not add a separate CLA or DCO
submission gate. Only submit material you have the right to contribute.

For ordinary questions use [support](SUPPORT.md). Report sensitive security
findings through the [security policy](SECURITY.md), rather than posting
exploit details or personal data in a public issue.
