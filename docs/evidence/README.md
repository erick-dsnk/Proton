# Evidence records

This directory defines the evidence convention for the open source Vanguard
compatibility effort. The [implementation register](../vanguard-implementation-progress.md)
contains the initial experiment; the [feasibility study](../vanguard-linux-feasibility.md)
preserves the original source/package/host snapshot. The
[initial rundown evidence bundle](2026-10-10-rundown-protection/README.md)
publishes the exact original patched and fresh-prefix baseline generic-runtime
logs, source provenance, result metadata and reproducible failure comparison.
The full SDK build log and remaining initial artifacts are retained locally.
The [E05 attachment falsifier](2026-10-10-e05-attachment-falsifier.md) records
the x64 test-only result and its local log/artifact hashes; raw build outputs
remain outside the repository. The
[A1b shared-region experiment](2026-10-10-a1b-shared-regions.md) records gate 1
and keeps the separate same-continuation gate open; raw logs and build
artifacts also remain outside the repository. The
[A1b continuation experiment](2026-10-10-a1b-continuation-migration.md) records
the bounded serial raw-continuation result; its raw log/build artifacts remain
outside the repository. The [A1b caught-fault experiment](2026-10-10-a1b-caught-fault-recovery.md)
records one VEH-caught fault, native-host return, deterministic handler and
allocation cleanup, and a subsequent healthy continuation; its raw log/build
artifacts remain outside the repository. The follow-up
[A1b frame-unwind experiment](2026-10-10-a1b-frame-unwind.md) records real
table-handler search and `RtlUnwindEx` through three mapped frames, unwind
callback cleanup, root landing, scoped TEB-bound restoration and native return.
Its raw log/build artifacts remain outside the repository. Neither result
establishes general compiler cleanup or Wine attachment semantics.
The [A1b compiler-finally experiment](2026-10-10-a1b-compiler-finally.md)
then observes compiler-generated nested x64 `__finally` funclets on the shared
stack after arrival in B, normal and abnormal cleanup, `RtlUnwindEx` through
the mapped parent frames, and native-host return. The result is specific to
the inspected Clang PE scope table; other compiler PC-boundary arrangements
remain unproven. Raw build and run artifacts remain local.

The [process-local kernel allocation experiment](2026-10-10-a1b-kernel-arena.md)
records an opt-in x64 section-backed allocator, 349 added generic checks with
the same baseline diagnostics, and host map observations. The sampled memfd
inodes differ between processes; this is not evidence of cross-process aliasing
or E05 attachment. Exact commands and environment details are preserved in
local metadata, whose manifest is linked from the record; raw artifacts remain
outside the repository.

The [private-mapping backing experiment](2026-10-10-a1b-private-backing.md)
records focused opt-in `MEM_PRIVATE` backing, commit/protection/decommit and
failure-cleanup runs. It preserves E05's eight attachment todos and does not
demonstrate that another process can dereference the mapping.

The follow-up [A1b private-backing matrix and live-view record](2026-10-10-a1b-private-backing-matrix-and-live-view.md)
records the completed ordinary-pointer lifetime/protection matrix, backing-FD
identity/lifetime observations, and real-owner metadata lookup. The separate
managed TARGET to EXECUTOR live-view fixture did not reach its pointer checks;
no foreign-view revocation pass is claimed.

The [combined backing and kernel-arena integration](2026-10-10-a1b-backing-arena-integration.md)
records a single generic x64 run with both options off and both options on.
The enabled settings were observed in the actual service-host processes and
the candidate retained the baseline failure diagnostics. The run used
assembled artifacts and did not implement or validate cross-process attach;
E05's eight attachment todos remain.

The [managed TARGET layout experiment](2026-10-10-a1b-managed-target-layout.md)
validates strict Linux AMD64 preloader admission, guest-range enforcement, and
the descriptor in actual Wine driver-host processes. Its scope is TARGET only:
it does not establish attach or cross-process kernel aliases.

The [managed EXECUTOR bootstrap](2026-10-10-a1b-managed-executor.md) records
the separate Linux AMD64 host-runtime process, canonical ntdll placement,
admission matrix and concurrent private-address census. Its E05 comparison
still has all eight attachment todos; no target aliases or attach semantics
are implemented.

The proposed [A1b attachment-backing architecture decision](2026-10-10-a1b-attach-backing-design.md)
defines a gated Linux x64 wineserver mapping-backing experiment and the
end-to-end prerequisites for implementing ordinary Wine process attachment.
The decision now includes a managed guest/host address-space constraint and a
real-loader executor boot gate. The focused backing run does not validate the
full phase or E05. The executor boot gate is now validated in its own bounded
experiment. The decision remains a design proposal for the unimplemented
foreign-view and attach phases; it does not claim that public attach/detach
APIs work.

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
