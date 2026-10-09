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
