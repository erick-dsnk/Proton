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
| G2: execution architecture | Wine user-space driver host is the initial model; attached-pointer behavior unresolved | Benign tests establish every required address-space/context/privileged-state contract |
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
2. **E05/G2: process-attachment falsifier.** A benign driver must directly read a
   target-only mapping after attachment. Two processes must map different bytes
   at the same virtual address and yield their own bytes; detach must restore
   context. Record a failing architecture result before proposing a bridge.
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
