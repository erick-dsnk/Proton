# Project changelog

This records changes in the community Vanguard compatibility effort. For
Valve's upstream Proton releases, consult the separate
[upstream changelog](https://github.com/ValveSoftware/Proton/wiki/Changelog).
Entries describe engineering results, not a claim of playable League.

## 2026-10-10 — First compatibility increment and project foundation

- Published the feasibility study and implementation evidence for this fork's
  attempt to implement Riot Vanguard support in Proton and return League of
  Legends to Linux.
- Added eight ordinary rundown-protection APIs in Wine: initialization,
  acquisition, counted acquisition, release, counted release, waiting,
  completion, and reinitialization. Added benign driver tests for rejection
  during teardown, outstanding users, reuse, concurrency, and freeing the
  protected allocation immediately after waiting.
- Completed the configured x64 Wine build and confirmed all eight PE exports.
  The patched generic NT driver suite ran 34,156 tests, with 161 marked todo,
  21 failures, and no skips. The unpatched baseline ran 26,023 tests, with 161
  marked todo, 21 failures, and no skips. Normalized failure-message sets were
  identical: 8,133 additional assertions introduced no new failures or skips.
- Published the Wine component commit and updated this fork's Wine source
  location and gitlink so contributors can obtain the compatibility patch.
- Added project-facing documentation, contribution and governance conventions,
  conduct and reporting policies, issue/pull request guidance, and lightweight
  repository checks. Preserved Proton's component licenses and technical
  reference documentation.

Native Windows comparison, i386 execution, attached-process address-space
semantics, full Proton integration validation, genuine Linux verifier
acceptance, Vanguard execution, and connected League gameplay remain open.
See [implementation progress](docs/vanguard-implementation-progress.md) for
source and artifact hashes, commands, review fixes, and evidence boundaries.
