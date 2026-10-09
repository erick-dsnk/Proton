## Problem and contract

Describe the observed problem, the Windows/Linux contract this change implements,
and the resulting behavior. Link the issue, roadmap experiment (E-number), and
acceptance gate (G-number) where applicable. Explain architecture assumptions.

## Change and scope

- What changed, including component commits and submodule pointers:
- Why this design is sufficient for the stated contract:
- Upstream relationship, attribution, and license considerations:

## Validation evidence

- Proton and affected component SHAs; patch/source hashes if uncommitted:
- Host, architecture, SDK image digest, toolchain, build mode, and runtime:
- Exact build/test commands and a durable evidence record or attached logs:
- Actual results, baseline failures, new failures, todo cases, and skips:
- Native Windows reference result, or explicitly **not run**:
- Complete Proton integration, actual Vanguard execution/acceptance, and League
  gameplay observations, or explicitly **not run / not demonstrated**:

For documentation or infrastructure changes, report the relevant checks instead
of filling unrelated runtime fields. A successful build, present export, or green
repository check does not establish runtime semantics or Vanguard acceptance.

## Contributor checks

- [ ] I read CONTRIBUTING.md and followed the project scope and evidence policy.
- [ ] The patch implements real behavior and does not fabricate security evidence,
      disable anti-cheat checks, or conceal the host state.
- [ ] I have the right to contribute this material and preserved attribution.
- [ ] I excluded credentials, personal account data, and proprietary vendor binaries.
- [ ] I updated the relevant documentation and recorded unresolved limitations.

Maintainers may request further contract tests, native comparison, or architecture
review before accepting an implementation claim.
