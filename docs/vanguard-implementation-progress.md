# Vanguard Linux implementation progress

This file tracks the open source Proton Vanguard compatibility effort after the feasibility study in
[`vanguard-linux-feasibility.md`](vanguard-linux-feasibility.md). It is a
working register, not a claim of Vanguard or League compatibility.

## Current project checkpoint — 11 October 2026

The first compatibility increment is ordinary Wine rundown protection. It
implements `ExInitializeRundownProtection`, `ExAcquireRundownProtection`,
`ExAcquireRundownProtectionEx`, `ExReleaseRundownProtection`,
`ExReleaseRundownProtectionEx`, `ExWaitForRundownProtectionRelease`,
`ExRundownCompleted`, and `ExReInitializeRundownProtection`. Public declarations,
PE exports, runtime synchronization, and generic driver tests changed together.
Review corrected the x86 FASTCALL declarations and test cleanup/lifetime behavior.

The implementation is published in Wine commit
[`2990a75de24c57ab0a8ff2dc3caab7d075d4df40`](https://github.com/erick-dsnk/wine/commit/2990a75de24c57ab0a8ff2dc3caab7d075d4df40),
based on `e60892cc2398b0a83c332a2078c7b85e47bdb42b`. Proton's initial
implementation/documentation checkpoint is
[`b5a134a8de15ad94a3af5b792314d6c700762727`](https://github.com/erick-dsnk/Proton/commit/b5a134a8de15ad94a3af5b792314d6c700762727).
The observed build used the original Wine base plus the exact four-file patch,
before those files were committed. Their recorded hashes below match the
published Wine tree; the publication did not rerun or broaden validation.

| Evidence | Result and limit |
|---|---|
| Isolated x64 Wine runtime | Full configured Wine `make -j8 all` completed successfully; no complete Proton integration build |
| PE exports | All eight ordinary rundown exports present in the built x64 image |
| Generic driver test, patched | 34,156 assertions/tests counted by the runner; 161 todo; 21 failures; 0 skipped |
| Generic driver test, unpatched baseline | 26,023 counted by the runner; 161 todo; 21 failures; 0 skipped |
| Comparison | Same 37 normalized failure diagnostics, 25 unique messages; 8,133 additional checks and no added failure or skip |
| Reference scope | No ordinary Windows comparison or i386 execution yet |
| Target outcome | No Vanguard execution, accepted session, or playable League evidence |

The full Wine build's exit status was directly observed as **0**. The exact
runner exit statuses for the valid patched and fresh-prefix baseline runs were
not retained before their execution sessions expired and are **unknown**.
Their retained logs contain complete suite summaries and the failure comparison
reported here; those establish execution of the new block and no added failure
or skip in that comparison, not an overall green suite or an inferred runner
exit status. The exit status from an earlier excluded baseline attempt must not
be attributed to the valid fresh-prefix run. Future runs should persist the
Docker runner status immediately, as the [test recipe](TESTING.md) does.

The historical commands and hashes below are the implementation record.
Their absolute paths are local provenance, not requirements for contributors.
The exact original generic-runtime test logs for the valid patched and
fresh-prefix baseline runs are now published with their hashes, source
provenance, results and reproducible comparison in the
[rundown evidence bundle](evidence/2026-10-10-rundown-protection/README.md).
The large full SDK build log and remaining local artifacts stay in the original
build directory and are not distributed; their hashes identify bytes but do
not make those artifacts publicly retrievable. Use the portable
[build](BUILDING.md) and [test](TESTING.md) recipes for new runs and record their
actual results with the [experiment template](evidence/experiment-template.md).

## Current work and next steps

1. **Freeze G0 inputs.** Keep the feasibility baseline pinned to Proton
   `bc896217ffcd67f892f952b010f898fe7bd0f0a1` and Wine
   `e60892cc2398b0a83c332a2078c7b85e47bdb42b`; retain the vendor hashes, host
   facts and SDK digest from the feasibility document. Select a Vanguard mode
   and obtain ordinary Windows reference evidence before interpreting runtime
   results. These last two pieces are still unavailable.
2. **Keep G1 explicit.** Record the selected mode's actual platform checks and
   returned restrictions. A Windows reference can establish normal Windows
   behavior; it cannot establish Linux acceptance. Genuine Linux verifier
   acceptance remains unresolved and is a dependency of any Vanguard session
   claim.
3. **E02 and the first E03 increment are established.** The isolated x64
   generic driver suite exercised the ordinary rundown patch against an
   unpatched Wine baseline. It added 8,133 checks without adding a normalized
   failure or skip; the full suite retained 21 baseline failures. Native
   Windows comparison and i386 execution remain open.
4. **E05 falsified attach behavior in the current A1 implementation.** The
   benign x64 test kept two child processes alive, mapped different bytes at
   the same address, confirmed a target-only mapping, and observed access
   violations in all five read phases around attach/detach. Eight new
   assertions remain `todo_wine`; the existing 21 suite failures were
   unchanged. This is a test-only result for the tested Wine build, not a
   Vanguard call-path finding or a verdict on all user-space architectures.
   See the [E05 experiment record](evidence/2026-10-10-e05-attachment-falsifier.md).
5. **A1b shared-region and raw-continuation prototype passed; broader G2 remains.** The cooperative fixture
   mapped shared RX code, RW data/control and RW stack regions at identical
   addresses in the caller and two live child processes. Five serial fresh leaf
   invocations observed coherent shared mutation, per-process private bytes,
   mapped RIP/RSP, restored native stacks and preserved RBX/RBP sentinels. An
   occupied-address collision preserved its allocation. The original E05
   driver IOCTL remained unchanged and its eight attachment expectations stayed
   `todo_wine`. See the [separate experiment record](evidence/2026-10-10-a1b-shared-regions.md).
   The separate [raw-continuation experiment](evidence/2026-10-10-a1b-continuation-migration.md)
   then started one mapped root, suspended it four times, and resumed it on the
   caller/A/B/A/caller host sequence. Its nested shared-stack frames and mutable
   local survived; all 4 live register snapshots and 95 native-bridge
   preservation checks passed. Admission controls rejected malformed and
   wrong-owner checkpoints. The original E05 IOCTL remained unchanged and
   retained its eight attachment `todo_wine` expectations. This is a bounded
   serial raw-code result, not Wine attach/detach behavior. OS thread identity,
   TEB/TLS, table SEH/unwind, concurrency, target-lifetime races, native Windows
   and i386 remain open; G1 remains an independent platform-acceptance
   dependency. The follow-up [caught-fault experiment](evidence/2026-10-10-a1b-caught-fault-recovery.md)
   induced one genuine read AV on the migrated stack in process B. A scoped VEH
   consumed that exact fault and redirected to the current native bridge; the
   handler was removed, the fault allocation released, and TEB bounds remained
   unchanged. An unrelated native AV reached its ordinary catcher, a terminal
   restart was rejected, and a fresh healthy continuation passed afterward.
   The unchanged E05 IOCTL retained its eight attachment todos. The strict run
   reported 34,546 tests / 169 todos / 21 failures / 0 skips, exit 21, with all
   37 normalized failure lines / 25 unique diagnostics matching the retained
   continuation baseline. This is VEH abort/cleanup evidence only, not table
   SEH, frame unwinding, or Wine attach behavior. The follow-up
   [frame-unwind experiment](evidence/2026-10-10-a1b-frame-unwind.md) then
   registered function-table entries for three mapped frames. A real B read
   AV ran search handlers inner/outer/root, invoked actual `RtlUnwindEx`,
   consumed three frame-owned resources through unwind handlers, landed at
   the root target and returned through B's native bridge. Scoped TEB stack
   bounds were restored before native execution; function table, handlers,
   fault page and TLS state were cleaned. The later healthy continuation and
   unchanged E05 IOCTL passed, with all eight attach todos retained. This adds
   47 checks to the prior suite and preserves the same 37 normalized failure
   lines / 25 unique messages. It establishes only the described cooperative
   x64 frame path; compiler `finally`/destructor behavior, helper-range faults,
   collisions, async/concurrent switching, native Windows/i386 and Wine attach
   semantics remain open.

### A1b compiler-generated finally result

The [compiler-finally experiment](evidence/2026-10-10-a1b-compiler-finally.md)
used Clang 19 with `USE_COMPILER_EXCEPTIONS` and genuine linked PE scope
metadata. A linked helper entered only after the continuation arrived in B;
its single parent function contained nested `__try`/`__finally` scopes and two
outlined compiler funclets. Each funclet ran once on normal return and once
with abnormal termination during the deliberate shared-stack access
violation. Their stack-owned resource locals were consumed before the raw
mapped frames unwound through `RtlUnwindEx` to the root. The current native
bridge returned to B with 57 ABI checks, and the fixture verified TEB bound
restoration, identity, table/handler/page/TLS cleanup, and a later healthy
continuation.

The scratch build used the pinned SteamRT4 SDK plus a disposable derived image
containing Debian `lld-19` `1:19.1.7-3+b1`, because the base SDK had Clang 19 but
no `lld-link`. The final Clang-built `ntoskrnl.exe` module and test PE were run
with retained ntdll, wineserver and launcher. This was not a fresh complete
Wine or Proton build. Three intermediate candidate snapshots are retained:
each produced two extra assertions when the exception PC overlapped an
adjacent compiler cleanup range. The final inspected scope table excludes that
adjacent range for the recorded call return PC; this does not prove a general
scope-boundary rule.

The same-Clang baseline reported **34,593 tests / 169 todos / 21 failures / 0
skipped**, runner exit 21. The final candidate reported **34,650 / 169 / 21 /
0**, exit 21: 57 added checks, with the same 37 normalized failure lines / 25
unique diagnostics as baseline. E05 still reports eight attachment
`todo_wine` expectations. This bounded result covers compiler cleanup only
for the exact x64 Clang scope table and cooperative helper path; compiler
frames themselves were not migrated. General compiler-boundary behavior,
helper-range faults, collisions, concurrency, native Windows, i386, Wine
attachment and Vanguard acceptance remain open.

The default GCC configuration also built the final source and explicitly
skipped only this fixture because native compiler `__try`/`__finally` support
is unavailable there; its suite reported **34,593 / 169 / 21 / 1 skipped**,
exit 21. An earlier `win_skip` guard caused one extra Wine failure and was
replaced with `skip`. Both compiler paths and the failed guard attempt are
recorded in the evidence bundle.

### A1b process-local kernel allocation result

The [kernel allocation experiment](evidence/2026-10-10-a1b-kernel-arena.md)
adds an explicitly opt-in, 64 MiB section-backed allocator in the
driver-hosting `ntoskrnl.exe` process. With `WINE_SHARED_KERNEL_MEMORY=1`, the
fixture covers pool/IRP/device-object backing, invalid arguments, zeroing and
reuse, alignment, executable and NX pages, bounded exhaustion/recovery and
concurrent allocation/free. The normal run added 349 checks and reported
**34,942 tests / 169 todos / 21 failures / 1 skip**, exit 21; the default-off
run reported **34,593 / 169 / 21 / 1**, exit 21. Both retained the same 37
normalized failure lines / 25 unique diagnostics as the GCC baseline. The
single skip is the compiler-finally fixture, unavailable in the default GCC
build.

The host `/proc` capture showed real memfd-backed ranges, with a distinct inode
for each sampled process. It does not show shared views between an executor and
target, a parent and child, or two `ntoskrnl.exe` instances. The section handle,
arena base and initialization state are process-local. The unchanged E05
fixture retains eight attachment `todo_wine` expectations. An earlier
186-failure opt-in snapshot lacked the environment variable in the Windows
service host and did not exercise this allocator; the rebuilt service host now
passes it through. Exact test-runner and outer build invocations were not
recovered from retained tool metadata and are recorded with the local manifest;
they are not part of the committed evidence record.

### A1b private-mapping backing result

The [focused private-backing run](evidence/2026-10-10-a1b-private-backing.md)
reports 2,418 / 104 / 0 / 0 with the Linux x64 opt-in and 2,340 / 104 / 0 / 0
with the option unset. A post-fix injected mapping `ENOMEM` returned
`STATUS_NO_MEMORY` and retried successfully; an unrecoverable decommit rollback
terminated its child process while the parent fixture passed. The full
`ntoskrnl.exe` run reports 34,593 / 169 / 21 / 1, with E05's eight attachment
expectations still `todo_wine` and the attach/detach routines still stubs. The
candidate's 37 ordered failure payloads match the retained GCC baseline's 37
exactly, with no missing or extra entries. The explicit semantic normalizer
produces 18 distinct templates; it does not reproduce the historical
25-message grouping. This validates only the focused local backing path; no
foreign alias or ordinary attached pointer behavior has been demonstrated.

#### Completed private-backing matrix follow-up

The follow-up [private-backing matrix record](evidence/2026-10-10-a1b-private-backing-matrix-and-live-view.md)
extends that focused run with ordinary-pointer lifetime and protection checks.
Using the same PE fixture, the candidate default-off and unmodified Wine
baseline each reported **2,423 / 104 / 0 / 0**, while the candidate with
`WINE_SHARED_PRIVATE_BACKING=1` reported **2,503 / 104 / 0 / 0**; all three
runners exited 0. The matrix also passed six injected mapping, protection,
decommit and rollback cases. Each of the nine final runs exited 0 with 104
existing todos, zero failures and zero skips. The default-off candidate and
baseline summaries and ordered unexpected-failure payloads match.

The fixture covers initial/recommit/address-reuse zeroing, RW/RX/NX and
read-only/no-access behavior, decommit and release faulting, neighboring-page
preservation, retry after recoverable failures, fail-closed child exit after
fatal rollback, and parent usability after same-address child exit. Runtime
artifacts came from a fresh isolated copy of the checked managed-EXECUTOR
source/object tree with the changed PE test rebuilt; this remains assembled
Wine-only evidence, not a full Wine/Proton build. It supplies no native Windows
or i386 comparison.

Separate bounded fixtures pass for backing identity and owner lifetime on the
phase-1 Wine `084fc093` snapshot: actual same-address parent/child memfd
mappings were observed, the server backing FDs closed at child exit and final
release, and an ENOSPC creation injection left neither candidate object in the
server. An integrated real-owner lookup fixture on the later server source
checks identity/page flags, generation and protection/decommit/recommit
updates, stale requests, release lookup, and fresh identity after exact-address
reuse. The current-runtime opt-in FD-lifetime observer also passed
**2,503 / 104 / 0 / 0**, observing separate same-address parent/child memfd
backings, child-FD closure while the parent remains, and release/exit closure.
Together these runs close the documented phase-1 private-backing matrix for
the bounded Wine AMD64 source snapshot. They do not establish an ordinary
pointer into a foreign view.

At the private-matrix checkpoint, the managed TARGET to EXECUTOR live-view
proof was not completed. Two fixture
attempts ended before alias operations with helper `LoadLibrary` error 126; one
also reported a storage-prefix setup failure. A later execution was stopped
by the automated safety filter after it flagged a possible cybersecurity risk.
No ordinary pointer read/write, acknowledgement, active-access revocation,
consumer/target exit, or collision result is claimed. A1b remains incomplete.
The opt-in private mapping work remains experimental; public attach/detach
behavior and all eight E05 attachment todos remain unchanged.

The selected-runtime fatal-decommit test first failed twice on separate
initialized prefixes because the command omitted
`PROTON_VM_FAIL_RESTORE_PROT=R`. The injected hole-punch returned
`STATUS_NOT_SUPPORTED` (`0xc00000bb`), but the shim expected RW while the
read-only fixture correctly rolled back to `PROT_READ`; each run reported
**2,509 / 104 / 1 / 0**, runner exit 1 without reaching the intended rollback
injection. An observer-only diagnostic confirmed that parameter mismatch.
Adding only the missing `R` setting injected the actual read-protection
rollback failure, the child exited `0xc0000001`, and the suite passed
**2,509 / 104 / 0 / 0**, exit 0. This corrected result, together with default-
off and baseline **2,423 / 104 / 0 / 0**, opt-in **2,503 / 104 / 0 / 0**, the
other injection cases, real-owner lookup, and current-runtime FD-lifetime
observer, closes the documented phase-1 matrix for the bounded Wine x64 scope.
The older phase-1 observer result ran on Wine `084fc093`; the current-source
rerun confirms the later owner-index and process-exit behavior at the recorded
checkpoints. See the
[fatal-decommit harness diagnosis](evidence/2026-10-10-a1b-private-backing-matrix-and-live-view.md#final-runtime-fatal-decommit-harness-diagnosis)
and local manifests.

### A1b live-pointer and revocation follow-up

The separate [live-pointer/revocation record](evidence/2026-10-10-a1b-live-pointer-revocation/README.md)
closes the bounded ordinary TARGET → EXECUTOR pointer experiment. Three
independent Linux AMD64 runs each passed **249 checks, zero failures, exit 0**.
Direct executor load/store instructions at the original target VA observe live
bidirectional writes while a second target's same-address contents remain
private. The fixture verifies collision rejection, rights and stale-identity
rejection, read-only/no-access/sparse extents, rejected executor VM mutations,
active readers during protection/decommit/release, a withheld revoke ACK,
pending MAP cancellation, recommit/address reuse, and target/consumer exit.
An injected revoke failure fail-stops a disposable executor; a target-held
Linux pidfd confirms native death before owner mutation completion.

The published fixture needed Unix/Windows environment handoff, a valid
executor-host image and a genuine helper DIR64 relocation. Observation and
acquisition workers now start after command acknowledgement so VM-lock-bound
pipe I/O cannot consume a native gate. During that initial pointer-proof repair
phase, the only runtime change maps alias mmap ENOMEM to `STATUS_NO_MEMORY`.
The later APC follow-up also adds server diagnostics and the procfs observer
repair. Native ntdll and the fixtures were rebuilt on an
isolated copy; other compatible modules were retained. This is assembled
Wine-only evidence, not a full current-source Wine/Proton build.

Backing-disabled managed admission passed **12 checks / 0 failures**, exit 0.
The existing VM suite passed **2,423 / 104 todos / 0 failures / 0 skipped**
with the repaired candidate off, **2,503 / 104 / 0 / 0** on, and
**2,423 / 104 / 0 / 0** with the unmodified baseline; all exited 0. The off
and baseline summaries and empty unexpected-failure payloads match. Source,
artifact and log hashes, commands, exclusions, final logs and the local patch
are included in the evidence bundle.

The historical suspended-recipient/asynchronous-acquisition attempt stalled
after `CMD_SUSPENDED_KILL` returned and before `CMD_END_ACQUIRE` returned
(exit 143, no summary). The begin command acknowledged worker creation, not
lease creation or APC queueing. A suspended Wine thread may run system APCs,
and process-wide routing chooses an eligible thread rather than the intended
auxiliary thread. The historical log has no routing or cancellation records,
so the recipient and blocking frame are unknown. The later focused exercise
uses opt-in server traces and a native SIGUSR1-mask/blocked-read fixture control
to hold the actually selected recipient after queue insertion.

Three independent Linux AMD64 queued MAP/REVOKE runs each passed **52 checks,
zero failures, exit 0**. MAP cancellation was observed before dequeue or
delivery; its count drained to zero, status became `STATUS_CANCELLED`, the
lease revoked and the surviving process had no readable or writable alias.
For REVOKE, cancellation did not acknowledge removal: the server retried to a
surviving thread, observed a distinct native revoke ACK, then completed the
owner mutation. A tracing-only control passed **249 / 0**, exit 0. The native
test barrier is an explicit fixture scheduling control, not an operating-
system scheduler conformance claim.

The original local MAP exercise also found an independent Linux procfs observer
defect: after the native group leader exited, `/proc/self/maps` returned no
rows from the surviving executor thread, causing a later correct reservation
check to reject MAP. The committed fix reads `/proc/thread-self/maps`; paired
output shows the former empty and the latter reporting the live guard and probe
mappings. Existing reservation identity, permissions, coverage and collision
checks remain. A committed-source rerun is recorded in the integration record.
This explains the intermediate later-MAP failure, not the earlier
suspended-recipient stall.

The original runs used a local component delta on Wine `d262e370` in a separate
component worktree, plus an untracked proof runner. The exact change is now
published as Wine
[`9c389578ccc8c7111047dbb826debc102a8ddf26`](https://github.com/erick-dsnk/wine/commit/9c389578ccc8c7111047dbb826debc102a8ddf26)
on `vanguard-a1b-apc-cancellation`; a fresh clone retrieved it and the
committed-source rebuild and fixture reruns are recorded in the
[publication integration record](evidence/2026-10-10-a1b-live-pointer-revocation/integration-publication.md).
This supersedes the earlier unverified memory-proof status, but A1b
execution-chain integration, public attach/detach, all eight E05 attachment
expectations, native Windows, i386, full Proton, Vanguard acceptance and
gameplay remain open.

### A1b combined backing and arena integration

The [combined integration record](evidence/2026-10-10-a1b-backing-arena-integration.md)
reports a default-off run of **34,593 / 169 / 21 / 1** and a run with both
backing and arena options enabled of **34,942 / 169 / 21 / 1**; each runner
exited 21. Both options were absent in five monitored default-off
`winedevice.exe` environments and present in all five monitored opt-in
environments. Under the retained GCC baseline's normalization, both runs
matched its 37 failure lines / 25 distinct diagnostics with no added or
missing diagnostics. The one skip is the existing GCC `__try`/`__finally`
fixture limitation.

This was an assembled-artifact integration using separate existing artifact
trees with identical `config.status` hashes; no compilation occurred during
integration and it is not a full current-source Wine build. The E05 block
still has eight attachment todos, attach probes still fault, and
`KeStackAttachProcess`/`KeUnstackDetachProcess` remain stubs. This establishes
that both options reach the service host and coexist in the generic test run;
it does not establish shared arena aliases, foreign mapping access, or attach
semantics. Its 37-line / 25-diagnostic comparison uses the GCC-baseline rule;
it is not the distinct 18-template normalization in the standalone backing
record.

### A1b managed TARGET layout result

The [managed-layout experiment](evidence/2026-10-10-a1b-managed-target-layout.md)
implements Linux AMD64 TARGET admission with
`WINE_MANAGED_LAYOUT=v1:target:400000000000`, guest range
`[0x10000, 0x400000000000)` and truthful highest user address
`0x3fffffffffff`. The corrected focused Wine run passed 3 preloader-child and
29 parent assertions; the separate injection run passed 3 child and 39 parent
assertions, including eight active reserved-mmap `ENOMEM` markers and one
child `setenv` marker. Admission/rejection passed 14/14, and a conflicting
reservation returned `EEXIST` without modifying occupied mappings or a
64-byte sentinel. The default-off virtual suite reported 2,338 / 104 / 0 / 0;
this observed count is not normalized to the 2,340 count in the earlier
backing run.

In the final combined E05 opt-in run, six actual `winedevice.exe` processes
showed the expected `TARGET` descriptor, guest bounds, process limit and
continuous guest coverage. The off and three-option-on E05 runs reported
34,593 / 169 / 21 / 1 and 34,942 / 169 / 21 / 1 respectively; both matched
the retained GCC baseline's 37 diagnostic lines / 25 unique messages. The
eight attachment todos remained. This is an x64 generic suite comparison,
not an attach pass.

The mode rejects executor role and is not an executor implementation. It
does not reserve executor-private runtime slots, boot canonical host ntdll,
create cross-process kernel aliases, or change the attach/detach stubs. The
bounded builds eventually passed after two generated-input setup failures;
the assembled runtime is not a complete current-tree Wine or Proton build.
The frozen manifest contains the complete source/artifact hashes, exact
commands, retained failed attempts and runtime evidence.

### A1b managed EXECUTOR bootstrap result

The [managed-EXECUTOR experiment](evidence/2026-10-10-a1b-managed-executor.md)
now validates a separate Linux AMD64 Wine process using the
`v2:executor:400000000000:410000000000` handoff. The 96-byte, layout-ID-2
descriptor keeps TARGET's version-1 ABI unchanged, reserves the same bounded
guest range and a disjoint 1-TiB host range, and places the actual Wine AMD64
`ntdll.dll` at `0x400000000000`. The 16-case admission matrix passed. The
native fixture exited cleanly; the PE parent and child reported 209 and 201
checks with no failures. The read-only observer captured two separate Wine
processes holding different bytes at the same private allocation VA and
recorded four complete snapshots of the physical TEB, stacks, syscall state,
host mappings and cleanup. Four intermediate reads raised AssertionError
with empty diagnostics; their causes remain unlocalized and are preserved in
the evidence bundle.

The default-off virtual suite reported 2,340 / 104 / 0 / 0. The final E05
baseline-style and TARGET+backing+arena runs reported 34,593 / 169 / 21 / 1
and 34,942 / 169 / 21 / 1, runner exit 21 in each. Both retained the same
ordered 37 failure payloads and 25 unique diagnostics as the GCC baseline;
the eight attachment expectations remain `todo_wine`. This is not an
attachment pass. The experiment rebuilt the loader, native ntdll and fixtures
serially, assembling other compatible artifacts from prior checked trees; it
is not a full current-source Wine or Proton build.

This closes the clean host-runtime bootstrap gate only. It does not create
target aliases, share a kernel arena or driver image across processes, migrate
an initialized driver/import closure, or give the executor logical attached-
target identity. The ordinary/default Wine path still lacks general attach
semantics; the new implementation is limited to the opt-in synchronous
executor prototype. Native Windows and 32-bit validation, real Vanguard
execution, session acceptance and gameplay remain open.

### E05 buffered dispatch attachment-chain prototype — preliminary result

The next bounded experiment is now being implemented against one physical,
real `winedevice` managed EXECUTOR with explicitly declared read-only private
mappings. Its intended path keeps the existing benign compiled driver and
normal buffered-IOCTL sequence, then exercises caller → A → B → A → caller.
The driver must use ordinary compiler-generated pointer loads to distinguish
same-address bytes and read a target-only mapping while its code/globals,
IRP/buffers, pool allocations, stack locals, process references and
`KAPC_STATE` remain valid. The loader selector is
`WINE_EXPERIMENTAL_DRIVER_EXECUTOR=1`; the current range declaration is
`WINE_EXPERIMENTAL_ATTACH_RANGES=23000000:10000,24000000:10000`, alongside
`WINE_MANAGED_LAYOUT=v1:target:400000000000`,
`WINE_SHARED_PRIVATE_BACKING=1` and `WINE_SHARED_KERNEL_MEMORY=1`.
The identity assertions distinguish the stable creator reported by
`PsGetCurrentProcessId()` from the attached process reported by
`PsGetProcessId(PsGetCurrentProcess())`; `KAPC_STATE` contents are checked while
active, with its own storage canary/lifetime checked after detach.

The broad `make -j8 all` attempt and forced target/test builds completed with
exit 0 on the pinned SteamRT4 SDK. Three strict x64 runs then completed the
buffered dispatch chain: its common bytes were `0x59/0xa1/0xb2/0xa1/0x59`, its
target-only read faulted in the caller and returned `0xc3/0xd4/0xc3` in A/B/A,
and an uncaught attached fault returned `ERROR_NOACCESS` with zero bytes before
a healthy IOCTL completed. Each run reported 173 tests, one unrelated
`SignerSign` todo, zero failures and zero skips. This is a preliminary bounded
single-thread synchronous result; the default-off full-suite candidate matches
the retained baseline's 37 normalized failure lines / 25 unique diagnostics.
The suite remains non-green with its 21 baseline failures and one skip. The
first strict attempt exited 5 due to fixture setup touching absent execution
regions and did not reach the IOCTL. Neither result establishes general Wine
attach semantics, concurrent or lifetime behavior, Vanguard operation or
acceptance. Details and artifact hashes are in the
[dispatch-chain experiment](evidence/2026-10-10-e05-dispatch-chain.md).

### E05 concurrent buffered-dispatch experiment — bounded result

The follow-up two-thread experiment now passes on Linux AMD64 in four fresh-
prefix strict runs of the final source. Each reported 482 tests, one existing
`SignerSign` TODO, zero failures and zero skips. The fixture runs two outstanding
normal buffered IOCTLs through separate physical executors and verifies direct
compiler-generated reads at the same virtual addresses. Both lanes reach the
barrier together, observe their own distinct bytes and the peer's crossed bytes,
and retain distinct logical TIDs, `KTHREAD`s, IRPs, SystemBuffers, IO stacks,
`KAPC_STATE`s and stack locals. It also injects an uncaught fault into one lane,
checks that the peer continues, and passes a healthy follow-up pair.

The final source rejects a second outstanding request borrowing the same
logical `KTHREAD` with `STATUS_DEVICE_BUSY`; its negative test verifies the
original lane remains pending and a distinct peer still completes. A strict
serial regression also passed 173 tests with one TODO and zero failures/skips.
The tested Wine source tree is published through [Wine PR #1](https://github.com/erick-dsnk/wine/pull/1)
and is reachable from `main` at merge commit
[`ddf378e30bd26570821751b10b201ec546b5df18`](https://github.com/erick-dsnk/wine/commit/ddf378e30bd26570821751b10b201ec546b5df18);
the publication merge preserved the tested tree, and the runtime was not rerun.
The final-source default-off full suite reports 34,593 tests, 169 TODOs, 21
failures and one skip; its 37 normalized failure lines / 25 unique messages
exactly match the retained baseline. The suite is not green. The four final
strict runs and their current hashes, alongside earlier failures and
pre-guard passes, are recorded in the
[concurrent dispatch experiment](evidence/2026-10-11-e05-concurrent-dispatch.md).

The scope remains two synchronous logical caller threads, one request each at
a time, bounded read-only private extents, shared driver data and shared kernel
arena. It does not prove arbitrary provider writable-global coherence,
asynchronous callbacks or stack growth, general Wine attach semantics, native
Windows/i386 behavior, full Proton, Vanguard acceptance or gameplay. Target
exit, unmap/address reuse, and broader lifetime tests remain open.

The implementation checkpoint now reaches E02 build and runtime evidence for
the first E03 x64 patch, the test-only E05 failure on current Wine A1 attach
behavior, the A1b shared-region prerequisite, a narrow x64 raw-continuation
prototype, a caught-fault VEH/native-cleanup experiment, table-based search
plus `RtlUnwindEx`/cleanup for three described mapped frames, compiler-
generated finally execution in a linked x64 helper, process-local section-
backed kernel allocations, focused wineserver backing for eligible private
mappings, a managed TARGET guest layout, and a clean managed EXECUTOR
host-runtime bootstrap. A later separate live-pointer/revocation proof now
supplies bounded live cross-process aliases in the published component commit.
General/default Wine attach behavior remains unimplemented; the opt-in
buffered-dispatch prototype is separately limited to the tested synchronous
serial and two-thread cases recorded above. Broader G2 execution-context
behavior, compiler scope-boundary generality, compiler-frame migration, native
Windows reference, i386 build, genuine Linux verifier acceptance, and Vanguard
execution remain unresolved.

The next E05 architecture proposal is recorded in the
[A1b attachment-backing decision](evidence/2026-10-10-a1b-attach-backing-design.md).
It proposes first validating an opt-in wineserver backing primitive for
eligible private mappings, then separately proving ordinary attached pointer
access in a suitable execution model. The proposal does not change or validate
the public attach/detach APIs. Architecture review narrowed the executor step
to an explicit managed process cohort: establish a truthful guest-address
limit and disjoint host-runtime slots in the preloader, reject collisions, and
boot the host RTL through Wine's real loader before attempting driver handoff.
The TARGET guest boundary and a separate canonical host-RTL executor boot are
now validated in the [managed-layout](evidence/2026-10-10-a1b-managed-target-layout.md)
and [managed-EXECUTOR](evidence/2026-10-10-a1b-managed-executor.md)
experiments. Neither exports foreign target views, shares writable kernel
state across processes, nor changes E05. The actual caller pointer load before
and after attach, the migrated driver continuation and kernel-owned pointers
remain the next unresolved behavior.

## Frozen build inputs

These are the pre-publication experiment inputs. They intentionally retain the
original branch and base SHAs rather than being rewritten as current checkout
state. See the checkpoint above for the published implementation revisions.

| Input | Value |
|---|---|
| Proton checkout | `/home/eric/repos/proton`, branch `research/vanguard-kernel-feasibility` |
| Proton SHA | `bc896217ffcd67f892f952b010f898fe7bd0f0a1` |
| Wine gitlink / checkout SHA | `e60892cc2398b0a83c332a2078c7b85e47bdb42b` |
| SDK image | `registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64:4.0.20260331.220802-0` |
| SDK manifest digest | `sha256:97526b794ce1a9bed5f891084462260b3a02399569f7438a3a57b5a253001db9` |
| SDK image ID | `sha256:97526b794ce1a9bed5f891084462260b3a02399569f7438a3a57b5a253001db9` |
| Isolated build directory | `/home/eric/repos/proton-build-vanguard/wine-obj` |
| Isolated source copy | `/home/eric/repos/proton-build-vanguard/wine-src` |
| Configuration | Wine `--enable-win64`, SDK container, x86_64 only |
| SDK toolchain | GCC 14.2.0; x86_64-w64-mingw32 GCC 14-win32; GNU make 4.4.1; GNU ld 2.44; Autoconf 2.72 |

The initial source copy excludes `.git` and is then updated with the changed
implementation/test files. Immediately before compilation, SHA256 values in
the checkout matched the copied versions:

| File | SHA256 |
|---|---|
| `wine/dlls/ntoskrnl.exe/ntoskrnl.exe.spec` | `01cc7d29995ce8eaacc18b5d65e3a6db9d27878fd2049eb4250e7e6f3dfab2a4` |
| `wine/dlls/ntoskrnl.exe/sync.c` | `93365168f4fdb52cea59270c1dd1c2591e737f2466dd88b03563d91e8a650dc2` |
| `wine/dlls/ntoskrnl.exe/tests/driver.c` | `f573e57207538dd0ea9ca5fde19152e303ddb8b26d8fb4d73a9a85eca1e29bf4` |
| `wine/include/ddk/wdm.h` | `480b18ddb41a3ce8ecac0dbfad935cfcaba77fd67ff6e6188aca3f642710a15d` |

The `driver.c` hash above includes the review fixes for FASTCALL declarations,
post-rundown rejection, bounded worker completion, unload safety, and immediate
free after rundown wait. The source SHA is pinned by the table, so a later edit
requires copying and verifying the file again before treating these artifacts
as built from that later edit.

## Commands and results

The SDK was pulled and configured with:

```sh
mkdir -p /home/eric/repos/proton-build-vanguard
cd /home/eric/repos/proton-build-vanguard
/home/eric/repos/proton/configure.sh --container-engine=docker --build-name=vanguard-baseline
```

This only generated Proton's external Makefile; it did not run the broad Proton
build. To avoid Proton's `module64` prerequisite that synchronizes every Proton
component, a Wine-only source copy was prepared and configured directly in the
same SDK:

```sh
mkdir -p /home/eric/repos/proton-build-vanguard/wine-src
mkdir -p /home/eric/repos/proton-build-vanguard/wine-obj
rsync -a --delete --exclude=.git /home/eric/repos/proton/wine/ \
  /home/eric/repos/proton-build-vanguard/wine-src/
```

The source copy was mounted as `/src` and the object directory as `/build`.
The SDK was run as uid/gid 1000 with a writable `HOME` and `XDG_CACHE_HOME`;
without these, Wine's Vulkan generator attempted to create `//.cache` and
failed. After autogen and before the module build, the four changed files were
copied from the working checkout and their hashes checked with:

```sh
cd /home/eric/repos/proton
for f in \
  dlls/ntoskrnl.exe/ntoskrnl.exe.spec \
  dlls/ntoskrnl.exe/sync.c \
  dlls/ntoskrnl.exe/tests/driver.c \
  include/ddk/wdm.h; do
  cp "wine/$f" "/home/eric/repos/proton-build-vanguard/wine-src/$f"
done
sha256sum \
  wine/dlls/ntoskrnl.exe/ntoskrnl.exe.spec \
  /home/eric/repos/proton-build-vanguard/wine-src/dlls/ntoskrnl.exe/ntoskrnl.exe.spec \
  wine/dlls/ntoskrnl.exe/sync.c \
  /home/eric/repos/proton-build-vanguard/wine-src/dlls/ntoskrnl.exe/sync.c \
  wine/dlls/ntoskrnl.exe/tests/driver.c \
  /home/eric/repos/proton-build-vanguard/wine-src/dlls/ntoskrnl.exe/tests/driver.c \
  wine/include/ddk/wdm.h \
  /home/eric/repos/proton-build-vanguard/wine-src/include/ddk/wdm.h
```

Configuration then succeeded with:

```sh
docker run --rm \
  -v /home/eric/repos/proton-build-vanguard/wine-src:/src \
  -v /home/eric/repos/proton-build-vanguard/wine-obj:/build \
  -w /src --user 1000:1000 \
  -e HOME=/tmp/vanguard-home -e XDG_CACHE_HOME=/tmp/vanguard-cache \
  registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64:4.0.20260331.220802-0 \
  bash -lc 'mkdir -p "$HOME" "$XDG_CACHE_HOME" && ./autogen.sh && \
    cd /build && /src/configure --enable-win64'
```

The patch and current generic fixtures compiled successfully with:

```sh
docker run --rm \
  -v /home/eric/repos/proton-build-vanguard/wine-src:/src \
  -v /home/eric/repos/proton-build-vanguard/wine-obj:/build \
  -w /build --user 1000:1000 \
  -e HOME=/tmp/vanguard-home -e XDG_CACHE_HOME=/tmp/vanguard-cache \
  registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64:4.0.20260331.220802-0 \
  bash -lc 'make -j1 V=1 -C dlls/ntoskrnl.exe && \
    make -j1 V=1 -C dlls/ntoskrnl.exe/tests'
```

Artifacts produced:

- `wine-obj/dlls/ntoskrnl.exe/x86_64-windows/ntoskrnl.exe`
- `wine-obj/dlls/ntoskrnl.exe/tests/x86_64-windows/ntoskrnl.exe_test.exe`
- `wine-obj/dlls/ntoskrnl.exe/tests/x86_64-windows/driver.dll`
- `wine-obj/dlls/ntoskrnl.exe/tests/x86_64-windows/driver2.dll`
- `wine-obj/dlls/ntoskrnl.exe/tests/x86_64-windows/driver3.dll`
- `wine-obj/dlls/ntoskrnl.exe/tests/x86_64-windows/driver_netio.dll`
- `wine-obj/dlls/ntoskrnl.exe/tests/x86_64-windows/driver_pnp.dll`

The built target DLL SHA256 is
`718e7adb5accf155445c60dfb9426274ed6a232a5b4943d5a7577b25b03e85b1`; the
test executable SHA256 is
`bd0fe7ecd565908fcf0573fdebf178e36a561bee80c0136d2867b909242c83c6`.
The x64 PE export directory was inspected with the SDK's
`x86_64-w64-mingw32-objdump -p`; all eight rundown exports are present:

| Export | PE ordinal |
|---|---:|
| `ExAcquireRundownProtection` | 4 |
| `ExAcquireRundownProtectionEx` | 5 |
| `ExInitializeRundownProtection` | 6 |
| `ExReInitializeRundownProtection` | 10 |
| `ExReleaseRundownProtection` | 14 |
| `ExReleaseRundownProtectionEx` | 15 |
| `ExRundownCompleted` | 16 |
| `ExWaitForRundownProtectionRelease` | 17 |

The first limited runner attempts exposed missing transitive Wineboot modules.
The isolated x64 Wine runtime was therefore built fully, without installing it
or building Proton. `make -j8 all` completed successfully (log SHA256
`2a8b21cd0acd57738910bef663d5014adf465be443f43af56a21c1f060d68519`):

```sh
docker run --rm \
  -v /home/eric/repos/proton-build-vanguard/wine-src:/src \
  -v /home/eric/repos/proton-build-vanguard/wine-obj:/build \
  -w /build --user 1000:1000 \
  -e HOME=/build/home -e XDG_CACHE_HOME=/build/cache \
  registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64:4.0.20260331.220802-0 \
  bash -lc 'make -j8 all'
```

The first fresh-prefix run then stalled in Wineboot because Wine's optional
Mono installer opened a modal `Wine Mono Installer` window under Xvfb. This
was an environment setup prompt, not a test hang. That attempt was stopped
deliberately and its log retained as
`wine-obj/ntoskrnl-test-final.log` (SHA256
`9a70c6c42b68998d694947bce3e644eaceb57d0d1cd5c016cc16ba9212a262ec`). Setting
`WINEDLLOVERRIDES=mscoree,mshtml=` suppresses that optional CLR/HTML setup; the
Wine test wrapper adds `ntoskrnl.exe=b` to the override list. This does not
disable any of the generic driver fixture imports.

The checkout-built test was then run directly with a fresh win64 prefix,
headless Xvfb, and a five-minute timeout:

```sh
docker run --rm \
  -v /home/eric/repos/proton-build-vanguard/wine-src:/src \
  -v /home/eric/repos/proton-build-vanguard/wine-obj:/build \
  -w /build --user 1000:1000 \
  -e HOME=/build/home -e XDG_CACHE_HOME=/build/cache \
  -e WINEPREFIX=/build/vanguard-test-prefix-no-mono \
  -e WINEARCH=win64 -e 'WINEDLLOVERRIDES=mscoree,mshtml=' \
  registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64:4.0.20260331.220802-0 \
  bash -lc 'timeout --kill-after=15s 300s xvfb-run -a \
    /src/tools/runtest -v -T /build -M ntoskrnl.exe \
    -p /build/dlls/ntoskrnl.exe/tests/x86_64-windows/ntoskrnl.exe_test.exe \
    ntoskrnl'
```

The patched run completed with `34156 tests executed (161 marked as todo, 0 as
flaky, 21 failures), 0 skipped.` The eight rundown exports were available, and
the new rundown block emitted no assertion, worker timeout, or skip diagnostic.
It includes the zero-reference and held-reference waits, concurrent acquire
and rundown rejection, reinitialization, bulk references, and eight
immediate-free-after-wait lifetime rounds. The run log SHA256 is
`0e9907ea8bd25032734f3fdff2888b2f8b831e93e2412e9a2bc1542f8ce334e7`.

To separate the changed block from existing generic-driver behavior, a
baseline source and object tree was copied from the same configured checkout.
Only the four files listed in the source-hash table were restored from Wine
HEAD (`e60892cc2398b0a83c332a2078c7b85e47bdb42b`) in the baseline source; the
baseline `ntoskrnl.exe` and tests were cleaned and rebuilt with the same SDK.
A unique, clean baseline prefix then ran the same direct test command and
environment. Its summary was `26023 tests executed (161 marked as todo, 0 as
flaky, 21 failures), 0 skipped.` After stripping filename/line-number prefixes
from `Test failed:` diagnostics, both runs have the same 37 diagnostic lines
(25 unique messages): no patch-only or baseline-only failure. The patched run
executes 8,133 additional rundown assertions and worker/lifetime checks, with
no new failure or skip. The clean baseline test log SHA256 is
`b40167b0d2c6b36e54ec0c8896ec5d2a22fc3603b20a7f35a89f81d2b27e447c` and its
target build log SHA256 is
`e4f7c2c13d81f0c47d256d52e7994d5176413a6f1eacc4a5bf0de8420899748b`.

One preliminary baseline invocation was excluded: the object-tree copy
included the patched run's already initialized prefix, and that attempt
reported six crypto-provider failures without a suite summary. The valid
comparison above uses a different, previously nonexistent prefix.

No installed system Wine is used as evidence. The isolated object tree keeps
the compile, full-runtime, bootstrap, patched-run, and baseline-run logs under
`/home/eric/repos/proton-build-vanguard/`.

During compilation, WIDL/WRC reported five shift/reduce conflicts in the
existing `/src/tools/wrc/parser.y`; assembly emitted an indirect-jump warning,
and the existing `ntdll/unix/virtual.c` emitted a const-qualifier warning.
The changed `ntoskrnl.exe` source and test driver compiled without a diagnostic.

## Evidence still required

- Build and test on ordinary x64 Windows to provide the reference behavior.
- Validate x86/i386 calling conventions and data exports independently.
- Extend the bounded A1b result only for a specified contract. The x64 VEH
  abort/native-cleanup step, scoped three-frame table-unwind step, and exact
  Clang compiler-finally fixture passed. Compiler scope-boundary generality,
  migration of compiler-generated frames, arbitrary mapped helper faults,
  collisions, logical identity beyond the tested process/thread/TLS sentinels,
  concurrency and target lifetime remain open. Obtain native Windows and i386
  observations, then cover those contracts in isolated increments before
  considering address-space-dependent exports.
- Select the Vanguard mode and obtain actual platform restrictions and verifier
  behavior. Linux acceptance remains unproven.
- Compare the ordinary Windows reference and selected mode's restrictions
  before using the Wine generic-driver run to make target-specific claims.
- Keep code signing, firmware state, accepted Vanguard session, League gameplay,
  and production deployment as separate claims requiring separate evidence.

## Next bounded implementation work

1. Extend A1b only for a specified next contract. The x64 VEH abort and
   three-frame table-unwind/native-cleanup steps and one Clang compiler-finally
   fixture passed for their bounded scopes; general compiler-boundary handling,
   migration of compiler frames, helper ranges, collisions, Wine attach
   semantics, broader logical identity, concurrency and target lifetime remain
   open. Keep memory exports gated until a coherent address-space model passes
   the tests those contracts require. The E05 result applies to the current
   Wine implementation only.
2. Obtain ordinary Windows x64 rundown reference results and independently build
   and execute the i386 path. The corrected FASTCALL declarations are reviewed
   source, not observed 32-bit conformance.
3. Select and observe the actual Vanguard mode and returned platform restrictions
   on a suitable Windows reference; record Linux verifier acceptance as unknown
   until directly established.
4. Define a coherent processor/execution and user-address model before adding
   processor-count or address-boundary data exports. Then continue small API
   families with native reference, lifetime, race, and failure tests.

The [roadmap](ROADMAP.md) maps these tasks to the preserved E00–E12 backlog and
G0–G6 gates. Record new source/build results here or in a linked experiment;
do not replace the initial comparison with results from different inputs.

### Publication checkpoint (2026-10-10)

The accumulated E05/A1b prerequisites are published in Wine commit
[`084fc093b4eaec9f66a942f5d902496318762abb`](https://github.com/erick-dsnk/wine/commit/084fc093b4eaec9f66a942f5d902496318762abb),
on `vanguard-attachment-prerequisites`, and was referenced by the Proton gitlink
at that checkpoint. The successive gitlinks are recorded in the later
publication checkpoints below.
A clean remote clone retrieved the component commit and matched all 28 source
hashes in the final [executor manifest record](evidence/2026-10-10-a1b-managed-executor.md#publication-provenance).
This publishes the tested source bytes; it adds no runtime or acceptance claim.
Actual attach/detach remains unimplemented and all eight E05 attachment todos
remain open.

### Private-backing matrix publication checkpoint (2026-10-10)

The matrix fixtures and experimental managed-view implementation are published
in Wine [`d262e37075efc5ce8c7be8e85a547fbb6c03ad3d`](https://github.com/erick-dsnk/wine/commit/d262e37075efc5ce8c7be8e85a547fbb6c03ad3d)
on `vanguard-a1b-private-backing`, and was referenced by the Proton gitlink at
that checkpoint. The current integration advances the gitlink to Wine
[`9c389578ccc8c7111047dbb826debc102a8ddf26`](https://github.com/erick-dsnk/wine/commit/9c389578ccc8c7111047dbb826debc102a8ddf26)
after clean-clone retrieval and committed-source validation.
A fresh remote clone retrieved the exact commit, matched all 22 changed source
files, and matched all 13 runtime source hashes in the frozen rebuild2
manifest. See the [publication provenance](evidence/2026-10-10-a1b-private-backing-matrix-and-live-view.md#publication-provenance-2026-10-10).

This publishes the existing tested source bytes and the unverified live-view
fixture scaffolding. It adds no new runtime evidence. The bounded phase-1
private-backing matrix passes; the ordinary TARGET to EXECUTOR pointer and
revocation proof was unverified at publication. The later
[live-pointer/revocation follow-up](evidence/2026-10-10-a1b-live-pointer-revocation/README.md)
passes the bounded memory proof after local repairs. Its follow-up
[publication and committed-source check](evidence/2026-10-10-a1b-live-pointer-revocation/integration-publication.md)
documents the later Wine commit and integration reruns. A1b remains
incomplete, and all eight E05 attachment todos remain open. Full Proton,
native Windows, i386 runtime, Vanguard acceptance, and gameplay remain
unverified.
