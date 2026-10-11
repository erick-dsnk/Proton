# Testing and reporting compatibility

Test the behavior this fork claims, using its built Wine/Proton artifacts and
recorded inputs. The project currently has an x64 generic rundown-protection
increment; Vanguard execution, accepted session and League gameplay have no
demonstrated result. Consult the [implementation register](vanguard-implementation-progress.md)
for the initial evidence and the [roadmap](ROADMAP.md) for remaining gates.

## Run the isolated x64 generic driver suite

First follow [BUILDING](BUILDING.md#isolated-x64-wine-conformance-build). The
variables below come from that same Bash session. Use a unique prefix for each
attempt, including separate baseline and patched runs. Headless Xvfb is supplied
by the recorded SDK. The original Wineboot attempt opened an optional Mono
installer; disabling the unused CLR/HTML installers avoids that modal prompt.
The test wrapper adds `ntoskrnl.exe=b`; the generic driver imports remain active.

```bash
VANGUARD_RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)-$$"
VANGUARD_PREFIX="/build/prefix-$VANGUARD_RUN_ID"
set -o pipefail
docker run --rm \
  -v "$VANGUARD_BUILD/wine-src:/src" \
  -v "$VANGUARD_BUILD/wine-obj:/build" \
  -w /build --user "$VANGUARD_BUILD_USER" \
  -e HOME=/build/home -e XDG_CACHE_HOME=/build/cache \
  -e WINEPREFIX="$VANGUARD_PREFIX" -e WINEARCH=win64 \
  -e 'WINEDLLOVERRIDES=mscoree,mshtml=' \
  "$VANGUARD_SDK" \
  bash -lc 'timeout --kill-after=15s 300s xvfb-run -a \
    /src/tools/runtest -v -T /build -M ntoskrnl.exe \
    -p /build/dlls/ntoskrnl.exe/tests/x86_64-windows/ntoskrnl.exe_test.exe \
    ntoskrnl' \
  2>&1 | tee "$VANGUARD_BUILD/ntoskrnl-$VANGUARD_RUN_ID.log"
VANGUARD_RUN_STATUS="${PIPESTATUS[0]}"
printf '%s\n' "$VANGUARD_RUN_STATUS" > "$VANGUARD_BUILD/ntoskrnl-$VANGUARD_RUN_ID.exit"
sha256sum "$VANGUARD_BUILD/ntoskrnl-$VANGUARD_RUN_ID.log"
```

Use a Bash session without `errexit` for this block if you need to capture a
failing suite's status after the pipeline. A timeout, missing summary or stopped
attempt is incomplete evidence. Preserve it with its reason and rerun under a
new run ID only after understanding the cause.

Inspect the built PE exports inside the SDK, for example:

```bash
docker run --rm -v "$VANGUARD_BUILD/wine-obj:/build" "$VANGUARD_SDK" \
  x86_64-w64-mingw32-objdump -p \
  /build/dlls/ntoskrnl.exe/x86_64-windows/ntoskrnl.exe
```

Export presence verifies the artifact's export table, not function semantics.
Inspect all eight ordinary rundown names separately from the runtime result.

## Baseline and current observed result

The [initial rundown evidence bundle](evidence/2026-10-10-rundown-protection/README.md)
contains the exact original valid-run logs, source provenance, result metadata
and a reproducible comparison script. The runner exit statuses were not retained
for those historical runs; the complete log summaries support the comparison
below without establishing an overall green suite.

| Initial experiment | Runner count | Todo | Failures | Skipped |
|---|---:|---:|---:|---:|
| Wine base `e60892cc2398b0a83c332a2078c7b85e47bdb42b` | 26,023 | 161 | 21 | 0 |
| Base plus published rundown patch | 34,156 | 161 | 21 | 0 |

After normalizing file/line prefixes, the initial run had identical sets of 37
failure diagnostics (25 unique messages). The patch added 8,133 checks without
new failures or skips in that comparison. The full suite was **not green**,
and these counts are not a native Windows or target-game comparison. A repeated
run can have different counts or diagnostics; record its actual result rather
than copying this table into a new report.

To create an uncontaminated baseline, choose a separate source/object directory,
materialize the exact base source (for the initial comparison, `git -C wine
archive e60892cc2398b0a83c332a2078c7b85e47bdb42b`), and repeat the same configure,
build and runtime recipe there. Keep SDK, settings and test inputs equivalent
while using distinct clean prefixes. For future API changes, retain the new
test cases on the unpatched implementation when useful to demonstrate the bug;
label test-source differences explicitly. Compare diagnostics and the affected
block, not only aggregate failure counts.

## Contract tests expected for contributions

Cover valid initialization, ownership and reference counts, wait ordering,
concurrency, admission after teardown starts, final release, exceptions/error
paths and unload/free behavior as relevant. A worker timeout needs bounded
cleanup; no test should leave threads accessing freed fixture state. Use native
Windows reference results for the claimed contract and record OS/build,
architecture, statuses, exceptions and ordering differences. Any driver signing
or test-lab configuration is part of that experiment's scope; it is not a
Vanguard platform-acceptance result.

The rundown checkpoint still needs ordinary Windows x64 comparison and i386
execution. Source review corrected FASTCALL declarations, but x64 execution
cannot establish 32-bit ABI conformance.

## E05 process-attachment falsifier

The first E05 test-only increment is recorded in the
[2026-10-10 experiment record](evidence/2026-10-10-e05-attachment-falsifier.md).
On the retained Wine `2990a75de24c57ab0a8ff2dc3caab7d075d4df40` x64 runtime,
the benign fixture created two live targets with different bytes at the same
virtual address, confirmed a target-only mapping, and verified a valid driver
stack read and a caught NULL-read access violation. `PsLookupProcessByProcessId`
lookups succeeded. Yet direct-read probes in all five phases around
attach/detach raised `STATUS_ACCESS_VIOLATION` for the common and target-only
addresses available in each phase.
The eight new attachment expectations are `todo_wine`; there were no E05
unexpected failures or skips. The existing suite retained the same 21 failure
diagnostics as its prior patched run.

This falsifies attach behavior in the tested A1 implementation. It does not
establish that Vanguard reaches `KeStackAttachProcess`, rule out every
user-space architecture, or prove that an alternate A1b design provides Wine
attach behavior. The separate shared-region prerequisite and bounded raw
continuation prototype are now recorded below; they do not supply synthetic
stack exceptions, logical identity, target-lifetime, or concurrency semantics.
Remote-copy helpers and callbacks returning copied values do not test ordinary
pointer access in an attached continuation. Keep memory exports that depend on
this behavior gated until the required contract passes its tests. The E05
experiment was x64-only; native Windows and i386 comparisons remain pending.

The follow-up [A1b gate 1 experiment](evidence/2026-10-10-a1b-shared-regions.md)
adds a separate cooperative shared-region fixture. Its strict x64 run recorded
34,267 tests, 169 todos, 21 failures, no skips and runner exit 21. The new
shared-region checks passed and all eight E05 attachment todos remained; after
normalization, all 37 failure diagnostics matched the retained E05 run exactly.
The fixture invoked a fresh leaf in each process, not a migrated continuation.
Treat this as completion of the shared-region prerequisite only.

The follow-up [A1b continuation experiment](evidence/2026-10-10-a1b-continuation-migration.md)
tested one raw mapped continuation over caller → A → B → A → caller. It began
once, completed once, passed all four live register-state resume checks and
all 95 native-bridge preservation checks, and retained its nested stack locals
and real return chain. The run also rejected malformed and wrong-owner resume
contexts. The original E05 IOCTL then ran with its eight expected attachment
`todo_wine` results. The suite reported **34,388 tests, 169 todos, 21 failures,
0 skipped, runner exit 21**; it was not green. The normalized failure
diagnostics matched gate 1 exactly (37 lines / 25 unique messages). This is a
bounded serial x64 raw-code observation. It does not test Wine attach semantics,
synthetic-stack exception recovery, TEB/TLS or OS thread identity, concurrency,
target-lifetime races, native Windows or i386.

The [A1b caught-fault experiment](evidence/2026-10-10-a1b-caught-fault-recovery.md)
induced one real read access violation on the migrated shared stack in process
B. A narrowly scoped VEH recognized that event and returned through the
process's native bridge; its handler and fault allocation were then removed,
and TEB stack bounds were unchanged. An unrelated native access violation
reached an ordinary catcher while the recovery VEH was armed. Restart of the
faulted continuation was rejected, a fresh healthy continuation passed, and
the unchanged E05 IOCTL retained its eight `todo_wine` attachment expectations.
The suite reported **34,546 tests, 169 todos, 21 failures, 0 skipped, exit 21**;
all 37 normalized failure lines / 25 unique diagnostics matched the retained
continuation run. This tests VEH abort and native cleanup only. It does not test
table SEH, synthetic-stack unwinding, `finally`/destructor behavior, arbitrary
fault recovery, native Windows, or i386.

The [A1b frame-unwind experiment](evidence/2026-10-10-a1b-frame-unwind.md)
then registered three mapped x64 frames, observed real table-handler search
and `RtlUnwindEx`, consumed frame-owned resource tokens through actual unwind
callbacks, landed at the root and returned through B's current native bridge.
The fixture scoped `StackLimit`, `StackBase` and `DeallocationStack` to the
shared mapping during execution and restored them before native assertions. It
also verified function-table removal, handler/page/TLS cleanup, process/thread
identity, a TLS sentinel and a later healthy continuation. The strict run
reported 34,593 tests / 169 todos / 21 failures / 0 skipped, exit 21; all 37
normalized failure lines / 25 unique diagnostics matched the 34,546-test
caught-fault baseline. The eight E05 attachment expectations remain
`todo_wine`. This bounded fixture does not test compiler-generated
`finally`/destructor behavior, unwinding helper ranges or collisions, arbitrary
faults, concurrency, native Windows or i386.

The [compiler-finally experiment](evidence/2026-10-10-a1b-compiler-finally.md)
then used a Clang-built x64 test PE with real compiler scope metadata. A
linked helper entered after caller → A → B migration executed nested
`__finally` scopes on B's shared stack on both normal return and a deliberate
read AV. Both funclets ran once for each path, with abnormal termination true
during unwind; the raw mapped frames then unwound to the root and B returned
through its current native bridge. Its strict run reported **34,650 tests,
169 todos, 21 failures, 0 skipped, exit 21**. The same-Clang baseline had
34,593 / 169 / 21 / 0; all 37 normalized failure lines / 25 unique messages
matched. The eight E05 attachment expectations remained `todo_wine`.

This is specific to the compiler and scope table recorded in that experiment.
An earlier candidate exposed adjacent-scope return-PC overlap and an extra
funclet dispatch; the passing fixture records its protected and adjacent
ranges explicitly. This does not establish a general compiler boundary rule,
compiler frames migrating between processes, native Windows or i386 behavior.

Two separate x64 backing prerequisites now have focused records. The
[private-mapping run](evidence/2026-10-10-a1b-private-backing.md) passes its
opt-in virtual-memory fixture and ENOMEM cleanup check, but does not export a
foreign view; its full `ntoskrnl.exe` run leaves all eight E05 attachment
expectations as `todo_wine`, with 37/37 failure payloads matching the retained
GCC baseline. The [kernel allocation run](evidence/2026-10-10-a1b-kernel-arena.md)
adds 349 generic checks to a process-local section-backed allocator with no
baseline diagnostic changes. Neither fixture demonstrates cross-process
executor aliases or ordinary attached driver pointer access. Both experiments
are Linux x64 only and have no native Windows comparison.

The [combined backing and arena run](evidence/2026-10-10-a1b-backing-arena-integration.md)
checks the two current opt-ins together in one assembled-artifact runtime. Its
full suite matches the retained GCC baseline's 37 normalized failure lines
and 25 distinct diagnostics, while the eight E05 attachment expectations
remain `todo_wine`. This is integration evidence for the two local
prerequisites, not attach semantics or a full current-tree build.

The [managed TARGET layout run](evidence/2026-10-10-a1b-managed-target-layout.md)
validates 14 admission/rejection cases, safe collision rejection, boundary and
allocation behavior, failure injection and the managed descriptor in the E05
driver hosts. The same-artifact E05 suite retains its eight attachment todos.
This is Linux AMD64 TARGET admission evidence, not executor boot or a full
Wine/Proton build.

The separate [managed EXECUTOR run](evidence/2026-10-10-a1b-managed-executor.md)
validates a clean Linux AMD64 host-runtime boot, 16 admission/rejection cases,
native and PE fixtures, and a two-process read-only memory census. Its E05
OFF/ON runs both retain all eight attachment todos and the same ordered 37
failure payloads as the GCC baseline. Four intermediate census reads had
empty-diagnostic AssertionErrors and remain unexplained. This run rebuilt
selected Wine components and fixtures, not a full Wine or Proton tree; it does
not demonstrate an attach, a target alias, Vanguard acceptance or gameplay.

The [A1b backing-matrix and live-view record](evidence/2026-10-10-a1b-private-backing-matrix-and-live-view.md)
adds ordinary-pointer tests for private mapping zeroing, protection, decommit,
release, address reuse and failure cleanup. Against the selected x64 Wine-only
runtime, default-off and the unmodified baseline both passed **2,423 / 104 / 0
/ 0**, while opt-in passed **2,503 / 104 / 0 / 0**. The corrected fatal-
decommit rollback injection passed **2,509 / 104 / 0 / 0**; an earlier pair of
attempts omitted `PROTON_VM_FAIL_RESTORE_PROT=R` and is retained as an excluded
harness-parameter error. The phase-1 and current-source FD observers confirmed
separate same-address memfd backing and its child-exit/release lifetime. A real-owner lookup fixture passed
**87 parent + 6 child checks** off and **118 + 6** on, with no failures.

These are targeted Linux AMD64 Wine results based on component `084fc093`, with
the unmodified baseline `e60892cc`; the selected changes were built in targeted
Wine components, not as a full Proton build. The ordinary managed
TARGET-to-EXECUTOR pointer/revocation fixture did not reach its alias checks.
Therefore this matrix does not demonstrate ordinary cross-process pointer
loads/stores, revocation while access is active, public attach semantics, or
E05 conformance. All eight E05 attachment expectations remain `todo_wine`.

The later [live-pointer/revocation proof](evidence/2026-10-10-a1b-live-pointer-revocation/README.md)
passes three independent **249 checks / 0 failures** runs, all exit 0, after
local fixture and one runtime ENOMEM-status repair. Its backing-disabled
admission run passes **12 / 0**, exit 0. The same VM PE against the repaired
candidate off/on and the unmodified baseline passes **2,423 / 104 / 0 / 0**,
**2,503 / 104 / 0 / 0**, and **2,423 / 104 / 0 / 0** respectively. Ordinary
executor instructions access the original target VA; gated MAP/revoke races,
active readers, protections, collision, identity/address reuse and process
exit are checked. Final commands, logs and hashes are included in the evidence
bundle. This closes that bounded memory proof, not public E05 attachment.
The historical suspended-recipient attempt stalled after the auxiliary-thread
termination command and before acquisition completion; its log has no routing
events and cannot identify the recipient or blocking frame. Three later
Linux AMD64 runs each passed 52 checks for queued MAP cancellation and queued
REVOKE cancellation followed by retry to a surviving recipient and native ACK.
The follow-up [publication integration check](evidence/2026-10-10-a1b-live-pointer-revocation/integration-publication.md)
retrieved the published component commit from a fresh clone, rebuilt its
changed server and native ntdll, and reran queued cancellation (52/0) plus the
trace-control fixture (249/0) from committed source.
The opt-in trace records queue, dequeue, delivery, client completion,
cancellation, lease counters/readiness, retry and native revoke ACK as separate
events. `delivered` means the server supplied an APC handle, not that its
callback executed. The fixture holds the actual selected native thread with a
SIGUSR1 mask and blocked native read after trace-confirmed queue insertion;
this is a test scheduling control, not general scheduler conformance. The
tracing-only control also passed. No native Windows, i386, full Proton or
accepted Vanguard session is established.

## E05 buffered dispatch attachment chain

The current managed EXECUTOR prototype was evaluated with a benign compiled
driver through the ordinary buffered-IOCTL dispatch path. The experiment and
its evidence are tracked in the
[dispatch-chain record](evidence/2026-10-10-e05-dispatch-chain.md). Three strict
x64 runs have passed the bounded chain, each reporting 173 tests, one unrelated
SignerSign todo, zero failures and zero skips. The default-off full-suite
candidate matches the retained baseline's 37 normalized failure lines / 25
unique messages, with no new failures. A loader/bootstrap smoke check is
narrower evidence
and does not count as dispatch or attachment proof.

The intended first run is opt-in and bounded to one logical driver thread and
explicit read-only private memory extents. Preserve the same compiled driver
handler through `caller → A → B → A → caller`; use ordinary loads at the same
virtual address to check distinct bytes in each process plus a target-only
mapping. Check the handler's process/thread identity and kernel-owned state,
including IRP/buffers, pool pointers, stack locals, process references, and
`KAPC_STATE`, across the entire sequence. `PsGetCurrentProcessId()` should
remain the creator PID; `PsGetProcessId(PsGetCurrentProcess())` should track
caller/A/B/A/caller. Check `KAPC_STATE` contents while active and its
canary/storage lifetime after detach. A remote-copy result does not satisfy
these assertions. The current experiment selects the managed executor and two
attach ranges with:

```text
WINE_MANAGED_LAYOUT=v1:target:400000000000
WINE_SHARED_PRIVATE_BACKING=1
WINE_SHARED_KERNEL_MEMORY=1
WINE_EXPERIMENTAL_DRIVER_EXECUTOR=1
WINE_EXPERIMENTAL_ATTACH_RANGES=23000000:10000,24000000:10000
```

The full run also requires the managed TARGET layout, private backing and
kernel-memory options shown. Retain exact
Proton/Wine/harness SHAs, SDK digest, architecture, build and runtime commands
with separate exit statuses, artifact hashes, sanitized logs, and an equivalent
baseline. Record pointer values and statuses at all five points, identity and
kernel-state assertions, cleanup, and any failures. Leave native Windows,
i386, concurrency, target exit/cancellation, full Proton, Vanguard entry,
acceptance, and gameplay as separate open checks until directly observed.
Keep a caught fault followed by explicit driver detach separate from an
uncaught attached fault handled by the dispatch wrapper; only the latter,
followed by a healthy full-chain IOCTL, exercises wrapper cleanup.

## E05 concurrent buffered dispatch

The [concurrent dispatch record](evidence/2026-10-11-e05-concurrent-dispatch.md)
documents the next gate. Four strict final-source x64 runs each report 482
tests, one existing `SignerSign` TODO, zero failures and zero skips. Two
distinct caller threads keep their normal buffered IOCTLs outstanding together
at a barrier, then perform compiler-generated reads through independent
attached-process views. Both lanes read distinct bytes at the same virtual
addresses, including peer-lane values, with separate logical TIDs, `KTHREAD`s,
IRPs, SystemBuffers, IO stacks, `KAPC_STATE`s and stack locals. An uncaught fault
in one lane does not prevent the peer or a healthy follow-up pair.

The executor rejects a second outstanding request borrowing the same logical
`KTHREAD` with `STATUS_DEVICE_BUSY`; strict logs verify that the active request
remains pending and a distinct peer completes. A final-source serial regression
reports 173 tests, one TODO, zero failures and zero skips. The default-off full
suite reports 34,593 tests, 169 TODOs, 21 failures and one skip. Its 37
normalized failure lines / 25 unique diagnostics match the retained baseline
exactly, with no candidate-only or baseline-only failures. The separate
multi-reader lease fixture passes 46 checks with zero failures, and the
default A1b live-private-view fixture passes 249 checks with zero failures.

These results cover two synchronous logical threads, one request outstanding
per logical thread, declared read-only extents, shared driver data and the
tested shared kernel arena. They do not establish arbitrary imported-provider
writable-global coherence, asynchronous callbacks, automatic stack growth,
target exit/unmap/address reuse, native Windows or i386 behavior, full Proton,
Vanguard entry or acceptance, or gameplay. The next bounded runtime tests are
target lifetime and address-reuse behavior; retain native Windows/i386 and
platform acceptance as separate gates.

## Record distinct outcomes

1. Source/build identity and artifact export presence.
2. Generic driver loader, API, device-transport and lifecycle conformance.
3. Unmodified Vanguard driver entry and actual service/device readiness.
4. Genuine platform evidence and an accepted anti-cheat session.
5. Completed connected League gameplay and later regression across reboot/update.

Record failures, `todo_wine`, flaky markers and skips separately from passes.
An exported API, reported `SERVICE_RUNNING`, rendered window or client login
does not establish later stages. Use the [experiment template](evidence/experiment-template.md)
for logs/hashes, provenance and limitations. Keep vendor binaries, credentials,
account identifiers, access tokens and private machine identifiers out of public
records. Public diagnostics should remain sufficient to review the claim.
