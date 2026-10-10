# Architecture and decision boundaries

The initial implementation approach is **A1: extend Wine's user-space driver
host**, using generic NT-driver tests to improve real compatibility contracts.
This is the first research route, not a claim that it can run or obtain
acceptance for Riot Vanguard. The full source investigation and A1–A5 comparison
are in the [feasibility study](vanguard-linux-feasibility.md#4-architecture-options-and-falsification-experiments),
including the A1b controlled per-process hypothesis and A6 native Windows
reference/fallback outside the Linux outcome.

## Current execution path

Wine's services machinery requests driver startup; `winedevice` hosts the
driver, and `ntoskrnl.exe` supplies modeled NT interfaces. Wine's device/server
machinery transports device-control requests. The initial ordinary rundown
increment adds synchronization and lifetime semantics in
`wine/dlls/ntoskrnl.exe/sync.c`, declares the ABI in `wine/include/ddk/wdm.h`,
exports it in `ntoskrnl.exe.spec`, and exercises it through the generic test
driver. The [implementation register](vanguard-implementation-progress.md)
identifies the exact commit and observed x64 artifacts.

User-space modeling must define what it actually guarantees. A virtual IRQL
value does not mask Linux interrupts; a logical attached-process identifier
does not change the host thread's address space. Linux TPM measurements do not
establish Microsoft's Windows Secure Kernel identity. Each such boundary is a
test or an external acceptance question, not a name to emulate.

## Required early decisions

| Question | Experiment or evidence | Decision consequence |
|---|---|---|
| Can A1 provide direct attached-process memory access? | Target-only mapping; two target processes with same virtual address/different bytes; detach restoration | A bookkeeping-only attachment result fails the claimed contract; define a different design before memory expansion |
| Can required execution state be modeled coherently? | Benign tests of IRQL/context, processor callbacks, ordering, lifetime and teardown | A requirement for unavailable actual privileged state reopens G2 |
| Which platform identity does the selected Vanguard mode require? | Ordinary Windows observations, documented requirements, actual returned restrictions | Genuine Linux evidence needs a verifier that accepts its platform chain; G1 remains external until established |
| Is an API family compatible? | Native-reference success, failure, exception, race and ownership tests | Export presence and a successful return alone cannot close G3 |

## Current E05 result

The [x64 E05 test-only experiment](evidence/2026-10-10-e05-attachment-falsifier.md)
shows that the current A1 Wine build does not switch ordinary pointer access to
the attached process for the tested fixture: direct-read probes in all five
phases around attach/detach raised access violations, while the valid kernel-stack read,
NULL-fault guard, process lookups and child-lifetime controls behaved as
expected. [Microsoft documents `KeStackAttachProcess` as attaching the current
thread to the target process's address space](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntifs/nf-ntifs-kestackattachprocess);
the result therefore falsifies this implementation's modeled attach behavior.

This finding does not show that Vanguard calls the API, establish that every
user-space design is impossible, or decide that A2/A3 is necessary. Keep
address-space-dependent memory exports gated and treat A1b as a hypothesis.
The shared-region prerequisite below passed, followed by a bounded raw
continuation prototype through caller → A → B → A → caller. A remote-memory
copy or a target callback returning a copied value does not satisfy that
continuation test. The prototype does not implement Wine attachment semantics.
General fault recovery, logical identity, target exit/unmap, concurrency and
cleanup under those conditions remain open; the bounded VEH abort result below
does not close those broader gates.

The staged proposal in the [A1b attachment-backing decision record](evidence/2026-10-10-a1b-attach-backing-design.md)
starts with an opt-in wineserver backing primitive for eligible private
reservations, then requires a separate executor boot and ordinary E05 pointer
tests before enabling attach/detach. The bounded executor boot is now recorded
in its own experiment, while the mapped-continuation prototypes still do not
change Wine's public attachment behavior. Architecture review further narrows
the executor candidate to an
explicit managed process cohort: reserve a declared guest range and disjoint
host-runtime slots before ELF/TEB startup, then boot a canonical host RTL using
the real loader with strict collision rejection. This would trade full-range
application compatibility for a testable address-space contract. The
[managed TARGET layout experiment](evidence/2026-10-10-a1b-managed-target-layout.md)
validates strict target-side guest-range admission and a truthful reduced
user-address limit in the real Wine loader. The separate
[managed EXECUTOR experiment](evidence/2026-10-10-a1b-managed-executor.md)
then validated a clean Linux AMD64 Wine process with canonical real ntdll,
disjoint host bounds and declared low-page mappings. Together these results
validate physical process layouts only; they do not provide foreign aliases,
shared writable runtime state, logical attached-process identity or actual
attach semantics. E05 still faults on ordinary target pointer reads and keeps
all eight attachment expectations as todos.

A separate [process-local kernel allocation experiment](evidence/2026-10-10-a1b-kernel-arena.md)
now validates an opt-in section-backed allocator within the driver-hosting
process. Host maps show distinct backing in sampled processes, so this is not a
shared executor arena and does not supply a kernel-state alias for attachment.

## A1b shared-region gate result

The [A1b gate 1 experiment](evidence/2026-10-10-a1b-shared-regions.md)
established shared RX code, RW data/control and RW stack views at identical
addresses in the caller and two cooperative child processes. A 72-byte,
relocation-free x64 leaf executed serially in the order caller, A, B, A,
caller. Each fresh invocation reported RIP/RSP inside the shared regions,
observed the next shared-data sequence and stack value, loaded that process's
private same-address byte, and restored its native stack and RBX/RBP canaries.
An occupied-address mapping attempt preserved its sentinel. The unchanged E05
driver IOCTL then retained its eight attachment `todo_wine` expectations.

This closes only the shared-region prerequisite. These were five fresh calls
on three native processes, not one continuation migrated between address
spaces. It does not test real attach semantics, stack unwinding or faults on
the shared stack, TEB/TLS behavior, concurrent logical threads, target exit
during a call, native Windows or i386 behavior, Vanguard relevance, or Linux
verifier acceptance.

## A1b raw-continuation prototype result

The [same-continuation migration experiment](evidence/2026-10-10-a1b-continuation-migration.md)
passed its bounded x64 raw-code checks. The mapped root started once and
completed once. Four saved continuations resumed on the actual caller/A/B/A
hosting sequence, with PIDs `32/532/540/532/32`; they retained their nested
stack frames, cookies, direct private-memory reads and a mutable stack local.
All four live GPR/XMM/MXCSR/safe-flags snapshots and all 95 separate native
bridge-preservation checks passed. Invalid checkpoint and ownership controls
were rejected without dispatch. The unchanged E05 driver IOCTL then kept its
eight attached-read `todo_wine` expectations. The full suite remained at 21
failures and 169 todos, with the same normalized failure diagnostics as gate 1.

This closes only the bounded serial raw-continuation prototype. It does not
establish Wine `KeStackAttachProcess`/`KeUnstackDetachProcess` behavior or
Vanguard relevance. The prototype did not migrate OS thread identity or TEB/TLS,
support table-based synthetic-stack exception handling, exercise concurrent
logical continuations, or race target exit/unmap. A follow-up VEH experiment
now records a single caught-fault abort and native cleanup; it remains separate
from table SEH and unwind behavior. Native Windows and i386 checks remain
pending, as do broader G2 execution-context and platform-acceptance evidence.
G1 remains an independent dependency.

## A1b caught-fault recovery result

The [caught-fault experiment](evidence/2026-10-10-a1b-caught-fault-recovery.md)
induced a real read access violation at one mapped instruction after the
continuation resumed in process B. A narrowly armed process-local VEH checked
the fault and shared-stack context, consumed it once, and redirected to the
current native bridge. The native host returned with its tested ABI state; the
VEH was removed, the fault allocation released, and TEB stack bounds were
unchanged. An unrelated native access violation passed to a separate ordinary
catcher. Restart of the terminal faulted continuation was rejected, and a
fresh healthy continuation then completed. The unchanged E05 IOCTL still
reported eight expected attached-read `todo_wine` results.

The strict run reported 34,546 tests, 169 todos, 21 failures, no skips, and
runner exit 21. Its 37 normalized failure lines / 25 unique messages match the
retained continuation run. This observes VEH first-chance abort and native
cleanup on Wine; it does not demonstrate table SEH, stack unwinding, `finally`
or destructor execution, arbitrary fault recovery, continued execution of the
faulted instruction, or native Windows behavior. Logical thread/TLS identity,
concurrency, target lifetime, i386, actual Wine attach semantics and Vanguard
relevance remain open.

## A1b frame-based unwind result

The [frame-unwind experiment](evidence/2026-10-10-a1b-frame-unwind.md)
registers real x64 function-table metadata for the mapped root, outer and
inner frames. A read AV on B's shared stack ran table handlers in inner →
outer → root order. The root search handler invoked `RtlUnwindEx`; actual
unwind callbacks consumed all three frame resources, with the root receiving
target-unwind flags, and execution landed at the mapped root target. The
current native bridge returned to B with 57 ABI checks.

To let Wine validate each establisher frame, the test scoped the active TEB
`StackLimit`, `StackBase` and `DeallocationStack` to the actual shared mapping
during shared execution, then restored all three before native code resumed.
It verified function-table deletion and negative lookup, handler/page/TLS
cleanup, process/thread identity, and a TLS sentinel. A later healthy
continuation and the unchanged E05 IOCTL ran afterward; E05's eight attachment
expectations remain `todo_wine`.

The strict suite added 47 checks over the caught-fault run and retained its 37
normalized failure lines / 25 unique messages. This demonstrates only a
cooperative serial x64 table-handler and target-unwind path for the three
described mapped frames. The follow-up
[compiler-finally experiment](evidence/2026-10-10-a1b-compiler-finally.md)
then used Clang's real x64 scope metadata and outlined finally funclets in a
linked helper entered after migration to B. Normal and abnormal cleanup ran
once each, the abnormal path unwound through the mapped frames, and execution
returned through B's native bridge. The same-Clang suite added 57 checks with
the same 37 normalized failure lines / 25 unique messages; E05's eight
attachment expectations remain `todo_wine`.

The compiler result is limited to that linked helper and inspected PE scope
table. One candidate demonstrated that an exception control PC at an adjacent
scope boundary can select an extra termination funclet; the passing fixture's
recorded return PC is outside that adjacent range. This does not establish a
general boundary rule or that compiler-generated frames can themselves migrate.
Arbitrary helper-range faults, collision or stack-overflow handling,
asynchronous/concurrent switching, target-lifetime races, native Windows/i386,
Wine attach semantics and Vanguard acceptance remain unproven.

## Alternate routes require their own design

- **A2: Linux kernel broker.** A hypothesis for operations unavailable to A1.
  Before implementation, specify ABI, pointer and memory ownership, host/prefix
  scope, event delivery, isolation, deployment and teardown. Linux ring 0 is not
  the Windows kernel, and a broker's signature does not establish Riot trust.
- **A3: deeper NT execution substrate.** Requires explicit machine/address-space
  and kernel invariants rather than incremental success stubs. Its cost and
  accepted platform identity remain unestablished.
- **A4: actual Windows guest.** May support generic reference experiments when
  appropriate; the feasibility study records Riot's documented VM restriction.
  It has no demonstrated accepted gameplay route in this project.
- **A5: Riot-authored or accepted native Linux integration.** Could address the
  Linux platform boundary with genuine Linux coverage and verifier support.
  Required vendor components and acceptance are outside this fork's control.

No alternative is an implemented or accepted system today. Do not broaden the
architecture until a required contract and failed hypothesis justify it.

## Recording decisions

Use the [architecture-decision template](evidence/architecture-decision-template.md)
when a change affects execution, memory, privilege, trust, ABI or ownership.
Link the concrete experiment and distinguish proposed, accepted and superseded
decisions. Record the smallest coherent model, tests that would falsify it, and
what remains unknown. Ordinary bounded API patches can use a clear PR description
and test evidence without a separate decision record.
