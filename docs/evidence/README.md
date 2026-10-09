# Evidence records

This directory defines the evidence convention for the open source Vanguard
compatibility effort. The [implementation register](../vanguard-implementation-progress.md)
contains the initial experiment; the [feasibility study](../vanguard-linux-feasibility.md)
preserves the original source/package/host snapshot. The
[initial rundown evidence bundle](2026-10-10-rundown-protection/README.md)
publishes the exact original patched and fresh-prefix baseline generic-runtime
logs, source provenance, result metadata and reproducible failure comparison.
The full SDK build log and remaining initial artifacts are retained locally.

Use a dated Markdown record named `YYYY-MM-DD-short-experiment-name.md` for a
new material result, or a dated directory when public logs and comparison
artifacts accompany it. Copy the [experiment template](experiment-template.md),
fill the relevant fields and remove unused prompts. A normal small code change
can place equivalent evidence in its PR rather than create redundant paperwork.
Link durable records from the implementation register.

## Claim labels

| Label | Meaning |
|---|---|
| Observed | Directly measured result under the recorded inputs; identify the log/artifact |
| Documented | Published contract/requirement; cite the source and access date |
| Hypothesis | Proposed behavior/design that still needs an experiment |
| Conditional | Relevant only if a specific call, parameter, mode or restriction is reached |
| Unknown | Not established; name what observation is missing |

Static imports establish requested interfaces, not reached runtime calls.
Metadata identifying a signer is not a verified signature/trust chain. A hash
identifies bytes, but it does not make a private artifact publicly retrievable.
State whether logs are committed, linked or retained locally; do not promise
reviewers can reproduce an observation solely from a local path.

For each experiment retain source and submodule SHAs, relevant working diff,
SDK digest/toolchain, host/OS/architecture, commands, exit codes, artifact/log
hashes, full runner summary, failure/skip/todo details and excluded attempts.
Keep baseline comparisons equivalent and never silently overwrite an earlier
result after an input changes.

Sanitize public records and commit only material you can distribute. Do not
commit Riot binaries, credentials, tokens, account data, or private host/device
identifiers. Describe acquisition/version/hash provenance without redistributing
the vendor artifact. If redaction removes necessary evidence, narrow the public
claim and state the limitation.

Use the [architecture-decision template](architecture-decision-template.md)
for significant changes to the execution/trust/ownership model, linking the
experiment that justifies them. Keep accepted decisions separate from proposals
and explicitly supersede old decisions when their assumptions change.
