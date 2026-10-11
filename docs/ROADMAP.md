# Implementation roadmap

The goal is an accepted Vanguard session and a connected League match on Linux
using unmodified Riot components. This is an experimental compatibility effort,
with no demonstrated target acceptance or gameplay. An API count is not a
percentage of that outcome, and the project has no evidence-based delivery date.

The [frozen feasibility study](vanguard-linux-feasibility.md#8-structured-implementation-backlog)
defines E00–E12 in detail. The [implementation register](vanguard-implementation-progress.md)
contains the current observed checkpoint. Each contribution should name its
epic, source ownership, prerequisites, and exit evidence.

## Current gates

| Gate | Current evidence | What closes it |
|---|---|---|
| G0: reproducible scope | Linux/source/vendor baseline and SDK digest recorded; mode and Windows reference missing | Exact inputs, selected mode, and ordinary Windows reference for each experiment |
| G1: authentic platform acceptance | Unknown; Linux acceptance has not been demonstrated | Genuine platform evidence accepted by the selected mode's verifier |
| G2: execution architecture | E05 falsified attach behavior in tested x64 Wine A1; A1b shared-region, serial raw-continuation, bounded VEH abort/native-cleanup, scoped three-frame table unwind, compiler-finally, live-pointer/revocation, and three queued MAP/REVOKE cancellation runs passed; four strict final-source runs of the opt-in concurrent buffered-dispatch experiment passed, including fail-closed same-KTHREAD admission; public attach semantics, broader lifetime and context gates remain open | Benign tests establish required attach/detach behavior and each required address-space/context/privileged-state contract |
| G3: generic conformance | First x64 rundown increment exercised; baseline has 21 failures; Windows/i386 comparisons pending | Required API families, loader and transport pass scoped native-reference and failure/race tests |
| G4: local Vanguard operation | Not demonstrated | Unmodified driver entry, stable service/driver lifecycle and real device communication |
| G5: session and gameplay | Not demonstrated | Accepted anti-cheat session and completed connected League match without anti-cheat disconnect |
| G6: sustained regression | Not reached | G4/G5 survive reboot, update, mode transition, teardown and repeat runs |

These gates are distinct claims. G1 is an external acceptance dependency; it
cannot be closed merely by implementing more Wine exports.

## Next work, in dependency order

1. **E00/E01: reference and platform scope.** Obtain a suitable ordinary Windows
   reference, select the Vanguard mode, and record actual configuration and
   restrictions. Keep generic driver development separate from observations of
   the unmodified installed product. Run this in parallel with bounded tests.
2. **E05/G2: follow up the attachment falsifier.** The current Wine A1 result
   and its limitations are recorded in the [experiment](evidence/2026-10-10-e05-attachment-falsifier.md)
   and [architecture guide](ARCHITECTURE.md#current-e05-result). Collision-safe
   shared regions passed in the [A1b gate 1 experiment](evidence/2026-10-10-a1b-shared-regions.md).
   A [bounded raw-continuation prototype](evidence/2026-10-10-a1b-continuation-migration.md)
   then resumed one nested stack through caller/A/B/A/caller with the supported
   register state preserved. A [caught-fault follow-up](evidence/2026-10-10-a1b-caught-fault-recovery.md)
   then caught one exact read AV with a process-local VEH, returned through the
   native bridge, cleaned up and passed a later healthy continuation. The
   [frame-unwind follow-up](evidence/2026-10-10-a1b-frame-unwind.md) then
   exercised registered frame handlers and actual `RtlUnwindEx` across three
   mapped frames, consumed their resources through unwind callbacks, landed at
   the root and returned through B's native bridge. A
   [compiler-finally follow-up](evidence/2026-10-10-a1b-compiler-finally.md)
   then ran Clang-generated nested cleanup scopes after arrival in B, through
   normal and abnormal exits, before the same mapped-frame cleanup and native
   return. It is specific to the inspected PE scope table; an earlier
   candidate exposed an adjacent scope boundary that dispatched an extra
   funclet. General compiler-boundary handling, compiler frames migrating
   between processes, helper ranges, collisions, Wine attach behavior, logical
   identity beyond tested sentinels, concurrency and target lifetime remain
   open. The proposed [attachment-backing decision](evidence/2026-10-10-a1b-attach-backing-design.md)
   gates opt-in wineserver private-mapping backing before any executor work.
   The follow-up [backing matrix and live-view record](evidence/2026-10-10-a1b-private-backing-matrix-and-live-view.md)
   completes the bounded Linux AMD64 private-memory matrix and authoritative
   owner-metadata lookup after a corrected fatal-decommit injection command.
   The current integrated source also passes an opt-in FD-lifetime observer
   for same-address parent/child mappings, child exit, and final release. The separate [kernel allocation experiment](evidence/2026-10-10-a1b-kernel-arena.md)
   also validates process-local arena behavior but does not establish shared
   kernel state across processes. These results do not implement or validate
   ordinary attached pointer access. E05
   also reads caller memory before the first attach and after detach, while
   preserving the compiled driver continuation and kernel-owned pointers.
   The [managed TARGET layout](evidence/2026-10-10-a1b-managed-target-layout.md)
   now reserves and enforces one declared guest range, rejects collisions
   before driver entry, and exposes the reduced address limit through the real
   loader. The separate [managed EXECUTOR bootstrap](evidence/2026-10-10-a1b-managed-executor.md)
   now boots canonical real ntdll in the disjoint host range, with two
   explicitly owned low-page mappings. This validates a physical executor
   layout only. The separate [live-pointer/revocation proof](evidence/2026-10-10-a1b-live-pointer-revocation/README.md)
   passes three 249-check Linux AMD64 runs on the published Wine component.
   A separate [publication integration check](evidence/2026-10-10-a1b-live-pointer-revocation/integration-publication.md)
   verifies clean retrieval and reruns from the committed source. The proof
   closes the bounded memory primitive for one readable NX private extent.
   Three further 52-check runs exercise queued MAP and REVOKE cancellation with
   trace-confirmed recipient identity, retry and native ACK; a 249-check
   tracing-only control also passes. The native SIGUSR1-mask/read barrier is a
   fixture scheduling control. Three strict x64 runs of the bounded serial
   dispatch chain and four strict final-source runs of the concurrent dispatch
   experiment have passed. A distinct peer thread can dispatch concurrently;
   a second outstanding request borrowing the same logical KTHREAD returns
   `STATUS_DEVICE_BUSY`. The default-off full suite retains the same 37
   normalized failure lines / 25 unique diagnostics as baseline. The next gates
   are target lifetime, address reuse, native Windows and
   i386. The immediate implementation under test is one
   real `winedevice` managed EXECUTOR running the normal buffered driver IOCTL
   path with declared read-only private mappings. It selects the executor with
   `WINE_EXPERIMENTAL_DRIVER_EXECUTOR=1` and the current ranges with
   `WINE_EXPERIMENTAL_ATTACH_RANGES=23000000:10000,24000000:10000`, alongside
   `WINE_MANAGED_LAYOUT=v1:target:400000000000`,
   `WINE_SHARED_PRIVATE_BACKING=1` and `WINE_SHARED_KERNEL_MEMORY=1`.
   Its intended assertion chain is caller → A → B → A → caller with ordinary
   same-VA pointer loads, a target-only mapping, stable creator identity,
   changing attached-process identity, and preserved driver/kernel state. The
   [experiment record](evidence/2026-10-10-e05-dispatch-chain.md)
   records the three runs, one unrelated SignerSign todo per run, and the
   baseline comparison. Native Windows and i386 remain unproven.
3. **E02/E03/G3: rundown reference and i386.** Compare the published x64 increment
   on ordinary Windows and execute its 32-bit calling conventions and lifetime
   cases. Preserve baseline failures and todos, even when the new block passes.
4. **E03/E04/E05: coherent model before exports.** Specify processor count,
   execution context and user-address boundaries together. Add synchronization,
   work-item and data exports in small tested families whose guarantees fit that
   model.

## Later increments

| Work | Dependency and exit evidence |
|---|---|
| E04: execution context/APCs/rendezvous | G2 model; callback ordering, identity, suppression, cancellation and unload safety |
| E05: memory/MDLs/probes | Attached-address-space decision; real protection, faults, mapping ownership and cleanup |
| E06: objects/files/time/queries | Reached classes and parameters; content, errors, rights and balanced lifetimes |
| E07: installer/SCM/loader/transport | Generic conformance and evidenced driver needs; actual entry, IOCTL exchange and teardown |
| E08: crypto/providers/platform evidence | Observed parameter requirements; real signature/provider results and separate G1 decision |
| E09: event/private-state extensions | Demonstrated target dependency; delivery/access effects, unregister/reentrancy races |
| E10: runtime evidence register | Runs throughout; distinguish imports from reached calls and promote claims only with observations |
| E11: Proton/client/session integration | G1–G4; complete pinned Proton build, client/graphics/network operation, then actual G5 |
| E12: regression | G5 first; repeat on scoped updates, reboot, sustained runs and uninstall |

Review upstream changes before starting an API family and avoid overlapping
write ownership in Wine's kernel/server code. An unsupported required contract
or unavailable authentic acceptance is a reason to revisit the architecture,
with a recorded decision, rather than return success without the behavior.
