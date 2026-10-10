# A1b live TARGET → EXECUTOR pointer and revocation proof

Date: 2026-10-10. This follow-up exercises the memory primitive left unverified
in the [private-backing matrix record](../2026-10-10-a1b-private-backing-matrix-and-live-view.md#phase-2-managed-target-to-executor-live-view).

**Observed:** the corrected Linux AMD64 fixture passed three independent runs
with **249 checks, zero failures and runner exit 0**. Ordinary executor loads
and stores at `0x23000000` access the same live TARGET backing at its original
address. Bidirectional write coherence, distinct same-address TARGET contents,
permissions, collision rejection, pending-acquisition cancellation, active
revocation, address reuse and process exit pass for the recorded cooperative
cohort. The proof covers a complete committed readable NX private extent of
64 KiB. It does not implement Windows process attachment or complete A1b.

The APC follow-up adds three separate **52 checks / 0 failures** queued
MAP/REVOKE runs and a **249 checks / 0 failures** tracing-only control, all
exit 0. Each queued run terminates the exact server-reported recipient before
APC dequeue, then observes MAP cancellation and REVOKE cancellation followed
by retry to a surviving thread and a native revocation acknowledgement. These
original runs used the same bounded Linux AMD64 cohort and a local Wine
candidate. The exact source is now published as Wine commit
[`9c389578ccc8c7111047dbb826debc102a8ddf26`](https://github.com/erick-dsnk/wine/commit/9c389578ccc8c7111047dbb826debc102a8ddf26).
See the [publication and committed-source integration record](integration-publication.md)
for clean-clone retrieval and the separate build/run performed from that
commit.

## Results

| Run | Checks / todos / failures / skips | Exit | Log |
|---|---|---:|---|
| Final proof 1 | 249 / 0 / 0 / 0 | 0 | [log](logs/final-proof-1.log) |
| Final proof 2, separate prefix | 249 / 0 / 0 / 0 | 0 | [log](logs/final-proof-2.log) |
| Final proof 3, input hashes checked before and after | 249 / 0 / 0 / 0 | 0 | [log](logs/final-proof-3.log) |
| Backing disabled in both managed children | 12 / 0 / 0 / 0 | 0 | [log](logs/backing-off-proof.log) |
| Existing VM suite, candidate default off | 2,423 / 104 / 0 / 0 | 0 | [log](logs/vm-off.log) |
| Existing VM suite, candidate backing enabled | 2,503 / 104 / 0 / 0 | 0 | [log](logs/vm-on.log) |
| Same VM PE, unmodified Wine baseline | 2,423 / 104 / 0 / 0 | 0 | [log](logs/vm-baseline.log) |
| Queued APC cancellation, MAP and REVOKE | 52 / 0 / 0 / 0 | 0 | [log](logs/cancel-queued-4-1925.log) |
| Queued APC cancellation repeat 1 | 52 / 0 / 0 / 0 | 0 | [log](logs/cancel-queued-5-1927.log) |
| Queued APC cancellation repeat 2 | 52 / 0 / 0 / 0 | 0 | [log](logs/cancel-queued-6-1928.log) |
| APC tracing only, ordinary fixture | 249 / 0 / 0 / 0 | 0 | [log](logs/apc-trace-cooperative-1925.log) |

The standalone fixture has no todo or skip mechanism; each assertion reports
PASS or FAIL. All seven final runners exited 0. Candidate default-off and
baseline VM summaries match and both have empty unexpected-failure payloads.
Their entire logs are not byte-identical. The 104 existing VM todos remain.

The backing-disabled admission run keeps the managed layout enabled but clears
`WINE_SHARED_PRIVATE_BACKING` in both Unix and Windows environments. Admission
returns `STATUS_NOT_FOUND`; executor reads and writes fault, and the target's
ordinary allocation remains usable. The ordinary unmanaged parent separately
receives `STATUS_NOT_SUPPORTED` when requesting a managed alias.

## What the pointer and revocation checks establish

- Actual `movzbl (%rcx),%eax` and `movb %dl,(%rcx)` instructions run in the
  executor at the target VA. Only the deliberate single-instruction fault
  sites have a narrow exception catcher. No remote-copy helper supplies their
  values. First and final extent bytes are checked.
- TARGET A and B hold different bytes at that same VA. Executor writes reach
  only the selected target; later target stores are immediately visible through
  the executor pointer. Switching leases selects B's independent contents.
- Read-only leases deny stores, target no-access and sparse extents reject
  admission, and heterogeneous readable pages preserve read-only restrictions.
  Insufficient target process handle rights and stale lease tokens/generations
  are rejected without changing the live lease. Executor commit/reset,
  executable protection, overlapping section, dirty-state reset, free,
  decommit and unmap requests cannot mutate the foreign view.
- A benign native collision sentinel survives rejected acquisition and cleanup.
  One injected alias `mmap` ENOMEM returns `STATUS_NO_MEMORY`, restores the
  inaccessible reservation and preserves the owner bytes. A later retry works.
- While native revoke and its acknowledgement are withheld, owner protection
  remains pending and the executor continues successful ordinary reads. Once
  released, the active reader faults and no read begun after observed mutation
  completion succeeds. Protection, decommit and release have active-reader
  checks; explicit lease release makes both direct reads and writes fault.
- With MAP withheld, an authoritative owner fence becomes visible before MAP
  resumes. The mutation remains pending. Releasing MAP yields a revoked lease
  with `STATUS_CANCELLED`, never an acknowledged live lease, and neither a
  readable nor writable residual alias.
- Recommit zeroes prior bytes. Exact-address reuse leaves the old lease revoked;
  new admission has a fresh identity or generation and sees only new contents.
  TARGET exit revokes an active reader before Wine-observable exit completes.
  EXECUTOR exit drains its lease only after native death; target mutation and
  release remain usable. Injected native revoke failure terminates a disposable
  executor, and a real target-held Linux pidfd confirms native death before
  the owner mutation completes. No successful stale-view acknowledgement is
  substituted for failed revoke.

## Repairs and excluded attempts

The published fixture needed real bootstrap and synchronization repairs:

1. Its Windows-only role setting did not configure the native preloader.
   Both environments now receive the role and backing opt-in; the role is
   cleared after launch. A diagnostic timed out before alias proof because the
   executor was actually unmanaged.
2. The executor needs its fixture image inside its host allocation domain.
   The same executable filename is built in an `executor/` subdirectory with
   image base `0x400002000000` and dynamic-base selection disabled. The
   preloader's address checks remain intact. A rejected out-of-domain image is
   retained as a failed attempt.
3. The helper DLL lacked a genuine relocation directory required by executor
   admission. A volatile pointer to its real `DllMain` supplies a DIR64 fixup;
   `DllMain` validates the relocated pointer. Admission checks remain intact.
4. In the initial pointer-proof repair phase, the alias mapping path converted ENOMEM through a file-oriented error
   converter, yielding `STATUS_UNSUCCESSFUL`. The local runtime change maps
   this allocation failure to `STATUS_NO_MEMORY`, consistent with the private
   backing allocation path. This describes that repair phase only; the later
   APC follow-up also adds opt-in server diagnostics and changes the reservation
   observer to `/proc/thread-self/maps`.
5. Pipe I/O from an owner thread can block behind the VM lock held by a mutation.
   The former observer commands consumed the native gate window. Target-owned
   observation threads now publish the authoritative fence and completion in
   shared state; workers begin only after their command response is received.
   MAP initiation likewise uses an acknowledged asynchronous worker so the
   acquisition response cannot consume the native MAP gate.
6. Wine-observable consumer termination alone does not mean its native address
   space is gone. A real target mutation drains the prior lease and checks the
   pidfd before another executor is admitted.

One intermediate run reported 254 checks and two failures because its
acquisition response arrived after the two-second native gate expired. The
historical suspended-recipient/asynchronous-acquisition attempt then stalled
after `CMD_SUSPENDED_KILL` returned and before `CMD_END_ACQUIRE` returned; it was
stopped with exit 143 and no summary. Its preserved log is
[asynchronous-proof-stalled.log](logs/asynchronous-proof-stalled.log), SHA256
`4adc0a320c2e309a5f1e38f74acc79ac72fdef50f4c70c79f411ff71f9093107`. The
`CMD_BEGIN_ACQUIRE` response only acknowledged creation of an asynchronous
worker; acquisition and APC queueing happened afterward. A suspended Wine
thread can run system APCs, and process-wide routing selects an eligible thread
rather than the fixture's intended auxiliary thread. The old log has no route,
dequeue, delivery or cancellation events, so the exact recipient and blocking
frame cannot be recovered. These race and suspend assumptions explain why the
attempt was not a valid cancellation test; they do not establish the historical
blocking frame.

The first instrumented MAP cancellation runs exposed a separate issue in the
subsequent healthy acquisition. After the native group leader exited,
`/proc/self/maps` returned zero rows from the surviving executor thread, even
though it retained the same address space. The reservation guard therefore
rejected a later MAP as `STATUS_CONFLICTING_ADDRESSES` before mapping. The
fixture records both paths: `/proc/self/maps` has zero rows while
`/proc/thread-self/maps` shows the live guard and probe mappings. The local
repair reads `/proc/thread-self/maps` and preserves the existing full-range,
permission, memfd identity, offset, registered-view and
`MAP_FIXED_NOREPLACE` checks. This fixes an independent observer defect; it is
not the explanation for the earlier suspended-thread stall.

The final deterministic fixture uses a labelled scheduling control: a native
SIGUSR1 mask and blocked native read hold the actual selected main thread after
queue insertion, while a separate survivor handles observation. It does not
change server routing. The fixture waits for the server trace to report the
selected recipient before terminating it. For MAP, APC ID 1 is queued to
executor TID `0164`, then removed from that thread's queue before any
dequeue/delivery event; the lease count drains from one to zero, status becomes
`STATUS_CANCELLED`, the lease is revoked and readiness is signalled. The
process survives, direct reads/writes fault, and a healthy later MAP succeeds.

For REVOKE, APC ID 5 is queued to TID `0170` after the owner mutation fence is
visible. Terminating that recipient cancels the queued APC without a native
acknowledgement. The server retries as APC ID 6 to surviving TID `0174`; that
APC is dequeued and delivered, and only its later native revoke ACK (sequence
33) allows the owner mutation to complete. The alias then faults on reads and
writes. A later MAP and acknowledged cleanup REVOKE also pass. The result
manifest validates these event relationships. Three runs passed the same
semantic trace checks; together they total 156 assertions across independent
prefixes. `delivered` means the server
supplied the APC handle, not that the callback ran; `completed` means the
client returned an APC result. A native revoke ACK is separate and required
before owner mutation completion. The tracing-only control passed the ordinary
fixture without the cancellation hold.

Earlier diagnostic and fixture failures are listed, with exit status and log
hashes, in [results.json](results.json) and [runs/](runs/). Their captured logs
remain in this bundle. A diagnostic whose binaries changed while it was still
running is excluded from evidence. Final queued-cancellation and tracing-only
runs verify source and artifact hashes before and after execution.

## Source and build provenance

| Input | Identity |
|---|---|
| Proton source | `9eeee70bd91be64eaf050544b0a9a94ee9d0f4a3` |
| Wine component base | `d262e37075efc5ce8c7be8e85a547fbb6c03ad3d` |
| Published component | Wine [`9c389578ccc8c7111047dbb826debc102a8ddf26`](https://github.com/erick-dsnk/wine/commit/9c389578ccc8c7111047dbb826debc102a8ddf26), branch `vanguard-a1b-apc-cancellation`, based on `d262e37075efc5ce8c7be8e85a547fbb6c03ad3d`; contains the MAP/REVOKE diagnostics, fixture scheduling control and `/proc/thread-self/maps` observer repair |
| Historical experiment source | The original runs used a local candidate whose exact seven source files match the published commit; the patch and source manifests remain for independent inspection |
| Unmodified Wine baseline | `e60892cc2398b0a83c332a2078c7b85e47bdb42b` |
| SDK tag | `registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64:4.0.20260331.220802-0` |
| SDK digest | `sha256:97526b794ce1a9bed5f891084462260b3a02399569f7438a3a57b5a253001db9` |
| Architecture / configuration | Linux AMD64, `--enable-win64` |
| Local scratch | `/home/eric/repos/proton-build-vanguard/a1b-live-proof-20261010T184236Z` |
| Local component worktree | Scratch `wine-component/`, detached at the component base with the local delta |
| Server build | `wineserver` SHA256 `3fbe5722d30ce68d61137fcdb3b3002f75ccbdf6ee72298a930702bc8d43001f`; `thread.c` `7c91498fcbb9a7ce554470d3ff0180ce6e610c56fd8a35c67b354333eae8381`; `mapping.c` `ea9d2823361f28c560304f1d8ccb2d73df9552d44e576d66e84faea29f1ca292` |
| Native runtime build | `virtual.c` `1111733983515b792d9100389102f5a0bdf51189c28c98db85978981056d8281`; `ntdll.so` SHA256 `f7b8fbceda8dd3d728eb49b89591d3a943c038edf66d45a2886aa38ff1a3043e` |
| Fixture sources | PE `651a5c4ada49b1d6b8333f57fb9376938979e33d6857ac7b67dbe7e72a7fca14`; Unix `d40a30e65364bb1be8cf3d0a8f9fba0b2818e88af4906a79a3b2e1f34d584d8b`; runner `7aff8f1a8c217f8ca2564a78cedd44da59a04cd1b0814b9913a4f6c2b048955f` |

The runtime was copied into an isolated scratch from the retained rebuild2
source/object tree. The server and corrected native `ntdll.so` were rebuilt
with the pinned SDK; both PE variants, helper DLL/native companion, injector
and runner were freshly built. Other compatible runtime modules were retained.
This is an assembled Wine-only experiment, **not a fresh full Wine or Proton
build**. Both final component build steps and fixture compilation exited 0.

The original experiment ran before the new component commit existed, using a
local candidate based on Proton's `d262e370` gitlink. The published commit is
available from a clean HTTPS clone; the integration record names the exact
retrieval and verification steps. The separate ENOMEM-status repair is
retained in the patch and is not attributed to the APC diagnostics or
`/proc/thread-self/maps` change. The original repository Wine checkout at
`2990a75d` was preserved during the historical experiment.

[results.json](results.json) and [runs/](runs/) contain exact Docker argv,
timestamps, per-run exit statuses, source/artifact hashes, APC controls,
baseline identities and failed/excluded attempts. The queued APC attempt and
trace-only control retain their command, result and control files.
[SHA256SUMS](SHA256SUMS) checks the bundled evidence files. Build invocations
and logs are included beside the final runtime logs.
The evidence-local `.gitattributes` exempts only captured logs, stdout files,
and the raw source patch from whitespace warnings so their byte-for-byte
contents and hashes remain intact; documentation and source files retain the
repository's normal whitespace checks.

## Reproduce the recorded scope

Start with the documented [Wine-only build recipe](../../BUILDING.md#isolated-x64-wine-conformance-build)
for this component base, apply the component patch to that source and rebuild
the changed native ntdll. The recorded scratch reused compatible artifacts;
a fresh complete source build is an additional validation gate.

The runner expects `A1B_PROOF_ROOT` containing `wine-src/`, a configured built
`wine-obj/`, `fixture/`, and the supplied `runtime-source-verification.json`.
It uses the pinned SDK and the invoking user's UID/GID. For example:

```sh
export A1B_PROOF_ROOT=/path/to/disposable-proof
mkdir -p "$A1B_PROOF_ROOT/fixture"
python3 proof-runner.py runtime-build
python3 proof-runner.py build
python3 proof-runner.py run unique-live-proof
python3 proof-runner.py run backing-off-unique-proof
python3 proof-runner.py run cancel-queued-unique-proof
python3 proof-runner.py run apc-trace-unique-proof
python3 proof-runner.py vm vm-off
python3 proof-runner.py vm vm-on
export A1B_BASELINE_OBJECTS=/path/to/unmodified-baseline-objects
python3 proof-runner.py vm vm-baseline
```

Use new names/prefixes per attempt. Keep source and object files frozen while
a runner is active. The script records actual commands and hashes, uses bounded
native gates and an outer timeout, and cleans up the disposable wineserver.
Names beginning `backing-off` select the explicit negative admission fixture.
The exact recorded commands in the manifest supersede illustrative paths.

## Remaining gates

This closes the bounded ordinary-pointer/live-revocation and queued APC
cancellation experiments only. Arbitrary native mapping calls bypassing the
managed VM lock, multiple simultaneous leases, arbitrary driver execution,
shared kernel/driver state, logical attached identity and complete execution
context remain outside this proof. Public `KeStackAttachProcess` and
`KeUnstackDetachProcess` were not changed or exercised by this fixture; all eight
E05 attachment expectations remain open. Native Windows, i386 runtime, a full
Proton build, Vanguard call-path relevance, accepted sessions and gameplay have
no new evidence from this experiment.

Repository validation passed with disposable Python 3.13 venv and
`PyYAML==6.0.3`: `python scripts/check_repository.py` checked 48 first-party
Markdown files, links/anchors, project files and GitHub YAML; `bash -n
configure.sh`; and parent/component `git diff --check` all exited 0. The source
patch passed both `git apply --check` against a clean archive of component base
`d262e370` and reverse-application checking against the frozen component
worktree. The runner passed Python AST parsing, and every bundled file passed
`sha256sum -c SHA256SUMS`. These checks complement the runtime evidence rather
than establish attachment conformance.
