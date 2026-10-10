# ADR 001 — staged Wine process attachment through shared memory backing

Date: 2026-10-10. Status: proposed, phase 1 under experiment.
Related: E05 / G2; prior [E05 attachment falsifier](2026-10-10-e05-attachment-falsifier.md), [A1b shared-region experiment](2026-10-10-a1b-shared-regions.md), and [A1b continuation experiment](2026-10-10-a1b-continuation-migration.md).

## Context and evidence

**Observed:** the x64 E05 fixture created two target processes with different
bytes at the same virtual address, plus a target-only mapping. The current Wine
`KeStackAttachProcess` and `KeUnstackDetachProcess` implementations did not
switch ordinary pointer access: all eight attached-read expectations remain
`todo_wine`. See the [E05 record](2026-10-10-e05-attachment-falsifier.md).

**Observed:** separate A1b fixtures demonstrated equal-address shared regions
and serial migration of a small, relocation-free continuation through caller,
process A, process B, process A and caller. Bounded fault recovery, mapped-frame
unwinding and one Clang `__finally` fixture also returned through the native
host with scoped cleanup. These experiments use purpose-built code and
cooperative mappings. They do not run an ordinary Wine driver continuation
with `KeStackAttachProcess`, and they do not establish a general execution
context for arbitrary driver code. See the linked A1b experiment records.

**Design constraint:** an attached access must observe the target process's
ordinary mapping at the requested address. A copied value, a remote-memory
read/write helper, or an attach-state flag is not equivalent. The logical
creator/requestor process can differ from the process whose address space is
currently attached, so a creator-PID shortcut is insufficient.

The E05 fixture also exposes a prerequisite before attachment: its first
common-address read runs on entry to the buffered IOCTL, before the first
`KeStackAttachProcess`, and its last read runs after final detach. Both must
observe the original caller mapping. In addition, the compiled driver stack,
input/output buffers, `KAPC_STATE` objects, referenced process objects, code,
globals and pool allocations currently belong to the separate `winedevice`
host. A complete design must preserve these kernel-owned pointers while
changing which user address space ordinary loads and stores see. Therefore,
changing only the attach routine cannot satisfy this fixture.

## Decision

Proceed in separately falsifiable stages. This ADR proposes the direction; it
does not accept the end-to-end architecture or enable the public attachment
APIs.

**Phase 1 — private mapping backing primitive.** Add an explicitly opt-in,
Linux x64 experimental wineserver path, selected by
`WINE_SHARED_PRIVATE_BACKING=1`, for eligible Wine-owned `MEM_PRIVATE`
reservations. The wineserver owns the backing object and authoritative mapping
metadata. Mappings retain their Windows-visible `MEM_PRIVATE` classification,
reservation boundaries, protection behavior, zero-on-first-commit semantics,
decommit/recommit behavior and release lifetime. Mapping generations prevent
stale metadata from referring to a reused range. Defaults remain unchanged.
The first phase does not export arbitrary foreign mappings: until revocation
acknowledgement and lease lifetime are defined, foreign-process export fails
explicitly with `STATUS_NOT_SUPPORTED`.

This phase establishes a storage and mapping-coherence prerequisite only. It
does not change `KeStackAttachProcess`/`KeUnstackDetachProcess`, switch the
Wine host thread's address space, or establish that direct driver pointers
observe attached target memory.

**Candidate end-to-end model:** if phase 1 passes its isolation and lifetime
tests, investigate per-logical-kernel-thread execution state, a shared kernel
arena for driver code and kernel-owned globals, objects, pool and stack, and
authoritative backing for supported user mappings. Dispatch must begin with
the requestor's address space available before the first attach. Nested
attach/detach then changes the user-address view and restores the previous
view, while preserving the same kernel stack, `KAPC_STATE` storage, driver
globals and requestor identity. The executor must preserve logical thread
identity independently of host PID/TID. These are requirements to test, not
proof that process migration or an isolated executor can provide them.

## Architecture binding after executor review

**Design review, not runtime evidence:** the executor cannot safely inherit an
ordinary Wine process's full application address range and then overlay target
memory. The current x64 layout can use nearly the entire Linux user range; its
Unix runtime, ntdll data, TEBs, stacks and other native mappings may occupy
addresses that an attached target also uses. A shared kernel arena does not
resolve those collisions. The original raw continuation fixture did not
start a separate Wine executor or establish a canonical runtime; the later
[managed EXECUTOR experiment](2026-10-10-a1b-managed-executor.md) addresses
that narrower prerequisite.

The candidate is therefore narrowed to an **explicit managed process
cohort**. Before the ELF interpreter, Wine executable or first TEB is mapped,
the preloader must validate and reserve a declared guest range and disjoint
host-runtime slots. Managed target processes use the same guest range and
truthfully expose its reduced application-address limit. The executor role's
Unix runtime, private RTL, TEB/PEB, heaps and its own native/PE stacks stay in
the host range; a managed target's Windows TEBs and stacks can remain in the
guest range. Shared kernel code and state occupy separately reserved canonical
slots. Each allocation class must be measured and assigned by role; the design
does not claim that all native stacks live outside the guest range. No address
may be overwritten to force admission: a collision, missing preloader,
unsupported architecture, malformed layout or insufficient space must fail
startup before driver entry. The first executor milestone is now validated:
the real Wine loader boots two clean executors with canonical ntdll at the
same PE address while their physical runtime state and private dispatchers
remain process-local. The experiment also covers threads, PE loading,
exception search and unwind. These observations do not establish a shared
driver/import closure or actual process attachment.

### Managed TARGET layout result

The [managed TARGET layout experiment](2026-10-10-a1b-managed-target-layout.md)
now validates the admitted guest span and strict startup contract for a
managed target process. It does not support the executor role. The real Wine
loader successfully booted a target with the reduced address limit, and the
combined E05 run observed the preloader descriptor and complete guest-span
coverage in six driver-host processes. The final admission matrix passed
14/14; collision and boundary/injection checks passed as recorded in that
experiment. This advances the target-side layout prerequisite only. The
separate managed EXECUTOR experiment now validates the canonical host-RTL
bootstrap, but a shared driver/import closure, cross-process kernel aliases
and ordinary E05 attach behavior remain unimplemented.

This is a bounded experimental ABI for a controlled process cohort, not a
claim that arbitrary existing Wine processes or applications retain the full
Windows x64 address range. During the initial design review, a guest boundary
near `0x400000000000` was only an example. The bounded TARGET implementation
has since selected that exclusive guest end and validated its preloader
reservation against startup mappings. The executor experiment selected the
host bounds and slots; wider allocation classes, architectures and application
compatibility remain outside its validated scope.
Preloader reservations must remain protected from later native allocations,
and guest allocation/image paths must enforce the declared limit rather than
silently consuming host slots.

The successful executor boot closes only the host-layout gate. Before E05 can
run through real attach/detach, the model still needs authoritative
image/COW and section backing, revocable alias leases, a canonical initialized
driver image and import closure, shared kernel objects and dispatch stack,
separate physical-executor and logical-kernel-thread identity, caller-view
setup before `IoCallDriver`, and safe nested view changes across protection
updates, unmap, process exit and concurrent operations. Public attachment
APIs remain unsupported until the implementation can admit that complete
chain atomically. E05 must continue to read the caller mapping before its first
attach and after its final detach.

## Alternatives and consequences

- **Keep attachment as bookkeeping:** already falsified by the E05 target-only
  pointer probe.
- **Copy memory through process APIs:** can transfer bytes but cannot make
  ordinary driver pointer instructions execute against the attached mapping;
  it does not satisfy E05.
- **Migrate arbitrary execution stacks among existing processes:** the A1b
  raw prototype is a feasibility result, but its custom continuation, exception
  handling, shared stack and TEB manipulation are not a general Wine driver
  execution mechanism. E05 also requires caller context before attach and
  kernel-owned pointers to remain valid across all contexts. Expanding this
  prototype alone leaves code/data ownership, OS thread identity, concurrency
  and target lifetime unresolved.
- **Introduce a Linux kernel broker now:** no required contract yet shows that
  server-owned mapping primitives are insufficient. A broker adds privilege,
  deployment and maintenance costs and still would not provide Windows trust
  or accepted Vanguard attestation.
- **Use a complete NT guest:** this changes the host/runtime model and still
  does not by itself let a Windows guest driver dereference native Proton
  process addresses.

Phase 1 changes mapping representation only when explicitly enabled. It may
consume file descriptors and virtual memory resources, and its failure paths
must never silently fall back to incoherent success. Its design is falsified
if same-process private mappings alias across unrelated processes, protection
or decommit is not authoritative, committed pages fail zeroing rules, stale
generations access reused mappings, or ordinary Wine memory behavior changes
when the option is unset. A passing phase-1 fixture does not validate the
candidate executor model.

## Validation and follow-up

Validate phase 1 first with a Linux x64 wineserver fixture covering separate
same-address private contents, eligible mapping publication and lookup,
commit/decommit/recommit, read/write/execute protection changes, release,
zero-on-first-commit, stale generation rejection, unsupported foreign export,
process exit, injected creation/update failures, and the default-off path.
Compare the same fixture with the option unset and against the unmodified Wine
baseline. Record exact server/ntdll source SHAs, SDK digest, commands, runtime
status, artifact and log hashes, failures, skips and local-versus-committed
artifacts. This evidence is not a native Windows comparison.

The managed-launch and executor host-RTL boot gate described above is covered
by the TARGET and managed EXECUTOR records. Their default-mode, collision,
ownership, canonical placement, independent process state, thread, PE,
exception and unwind observations establish the constrained physical layout
contract only; they do not implement attachment.

Only after both prerequisites pass, build a bounded execution prototype that
covers caller context on dispatch and attached contexts during the same
compiled driver continuation. Test ordinary driver loads/stores—not helper
copies—at the same address in caller and two targets with different bytes,
target-only mappings, kernel-stack/local validity, nested attach/detach
restoration, per-logical-thread identity, two simultaneous logical threads,
protection changes, target unmap/exit and deterministic teardown. Then connect
the actual Wine APIs and rerun E05; remove its
`todo_wine` expectations only when ordinary attached reads and writes, errors,
nested restoration and lifetime/fault cleanup pass. Add a native Windows
reference and i386 ABI/runtime comparison before claiming the broader contract.

Stop or revise the model if ordinary execution cannot see the target mapping,
if unrelated private mappings alias, if an attach can outlive or race target
unmap/exit unsafely, if logical state leaks between concurrent kernel threads,
or if the design requires executing arbitrary Wine driver code through
unbounded custom stack migration. Keep G1 platform acceptance independent:
neither this design nor a Linux backing primitive supplies Windows Secure
Kernel identity, Riot verifier support, an accepted Vanguard session, or
gameplay.

The focused implementation and current x64 result for eligible private
mapping backing are recorded in the [dated experiment](2026-10-10-a1b-private-backing.md).
That result does not complete the broader phase-1 matrix or validate foreign
aliases. The phase remains under experiment, and the proposal does not claim
that the public attach APIs or end-to-end E05 behavior are implemented.
