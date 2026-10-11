# 2026-10-11 — E05 concurrent buffered-dispatch experiment

Status: **bounded concurrent independent-view gate passed on final source**.
Four strict runs passed after the same-logical-`KTHREAD` guard and its negative
fixture were added. The serial regression passed, and the default-off full-suite
diagnostics exactly match the retained baseline. No Vanguard binary or target
session is used.

The Wine component changes were published in
[Wine PR #1](https://github.com/erick-dsnk/wine/pull/1), merged to `main` as
[`ddf378e30bd26570821751b10b201ec546b5df18`](https://github.com/erick-dsnk/wine/commit/ddf378e30bd26570821751b10b201ec546b5df18).
The tested source commit `4e39c53f67f1c9f1d2f02432957e6cd07ec92c07` and the
merge commit have the same tree (`04b11422beb428b4690db95b896c9757d81d39b9`).
The retained runtime runs preceded publication; publication did not change the
source tree or trigger another runtime run.

## Question and bounded model

Can two simultaneous normal buffered IOCTL dispatches maintain independent
attached-process memory views while using the same shared driver code, writable
driver data and pool arena? The planned fixture keeps two dispatches outstanding
at barriers, has each logical lane read the same virtual addresses with distinct
bytes, and injects a fault into one lane while checking that the peer still
completes a healthy read and retains its kernel state.

The prototype uses separate physical worker processes as execution hosts for
two distinct logical caller threads. The workers adopt the shared driver
writable pages and kernel arena, while each lane receives its own mapping
aliases. The dispatch path retains per-request IRP/SystemBuffer ownership, with
the coordinator responsible for final completion and destruction. Worker
address admission and imports must resolve at the owner's canonical address;
an IAT mismatch rejects the request rather than patching a pointer or
fabricating a result. A logical `KTHREAD` cannot have two outstanding requests
at once: attachment changes its current process, so the second borrow now
fails closed with `STATUS_DEVICE_BUSY`. Distinct logical caller threads can run
on the two worker slots simultaneously.

The runtime provider's writable global data has not been proven coherent across
workers for arbitrary imported providers. The bounded driver root uses an
ordinary compiled C bridge and per-worker arena stacks, but does not establish
asynchronous dispatch/callback behavior, stack growth, general Wine
`KeStackAttachProcess` semantics, native Windows or i386 behavior, full Proton
integration, Vanguard operation or acceptance.

## Inputs and resource limits

| Input | Value |
|---|---|
| Proton parent revision | `c0a06aa7c4d5258413acf4edf5c179027e6fd1f0` before current uncommitted work |
| Wine component base | `9c389578ccc8c7111047dbb826debc102a8ddf26`; source tree has concurrent-dispatch changes |
| Published Wine component | PR #1 merged commit `ddf378e30bd26570821751b10b201ec546b5df18`; its tree matches the tested source commit |
| SDK | SteamRT4 x86_64 SDK, `registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64@sha256:97526b794ce1a9bed5f891084462260b3a02399569f7438a3a57b5a253001db9` |
| Target | Linux AMD64 host, x64 Wine tests |
| Scratch workspace | `/home/eric/repos/proton-build-vanguard/e05-concurrent-20261011T060000Z` |
| CPU scheduling | Build scripts used Docker `--cpus=2 --cpu-shares=256`, `nice -n 15`, `ionice -c2 -n7`, and `make -j2` |
| Windows reference | Not run |

Build attempts were limited to the touched runtime/test components. The
retained build and test logs are in the scratch evidence directory. Build
scripts cap Docker at two CPUs and 256 CPU shares, use `nice -n 15`,
`ionice -c2 -n7`, and `make -j2` to limit interference with the user's work.
The complete runtime/test-component build passed before the same-thread guard.
After that guard and its test were added, the changed runtime and test targets
were rebuilt successfully (`build-runtime-7.log`, `tests-build-5.log`).
Subsequent strict runs 10–13 used those final artifacts.

## Failed runtime attempts retained

The first concurrent runs are evidence of implementation defects and safe
rejections, not a pass. Strict runs 1 and 2 each reached 54 tests and failed
two assertions with Win32 error 487 (`ERROR_INVALID_ADDRESS`): the worker
could not admit the required image/import address layout. Strict run 2 logged
an imported `fltmgr` IAT address mismatch between worker and owner. The
implementation retains an address-integrity guard; the follow-up change is
intended to load the actual dependency closure at the owner's address before
worker entry.

An earlier wrong-root image rejection then exposed invalid IRP/SystemBuffer
frees: the worker completed an IRP before it had entered `IoCallDriver`, while
the coordinator still owned final completion. The repair parks pre-dispatch
failure and leaves single-owner completion/destruction with the coordinator.
Allocator review traced the double-free to this premature completion path, not
to shared-arena allocator corruption.

Strict run 3 is also retained and failed with exit 8 after 74 tests. It reported
lane 0 request result 1 / zero bytes / error 0, lane 1 result 0 / zero bytes /
error 170, then failed the injected-fault and healthy-peer recovery assertions.
Runs 4–6 reached the simultaneous pointer reads and exposed fixture assertions
about lane-local kernel storage and admission rejection. Run 6 logged correct
overlap masks and opposing values, but the negative admission assertion still
failed. Preserve all attempt logs rather than replacing them with later passes.

| Attempt | Log SHA256 | Result |
|---|---|---|
| `concurrent-strict-1.log` | `bf038afd9a706e362aac96a3d56855ac06d7d5e463f1611c76771b91da0e83c3` | Exit 2; 54 tests, 1 TODO, 2 failures; safe address-admission rejection |
| `concurrent-strict-2.log` | `690896566d278dda8e6070a1672528d0f417efccfbbbe5ac80c9c11a1af846cc` | Exit 2; 54 tests, 1 TODO, 2 failures; imported `fltmgr` IAT mismatch |
| `concurrent-strict-3.log` | `2c824dc2e9a99c4009c6f09564ee062611532670ecee2423fb78409edbd9c31b` | Exit 8; 74 tests, 1 TODO, 8 failures; lane and fault-recovery assertions failed |
| `concurrent-strict-4.log` | `264a588de654709bb40c317b75b580a984180d0263e88b6fd6abc21ee6cf044f` | Exit 2; pointer views passed; stack and injected-fault fixture assertions failed |
| `concurrent-strict-5.log` | `106418dd474f28d8aca7c7f86d81d33d8905c5d8a539db7313e077843f338374` | Exit 2; pointer views passed; storage and admission fixture assertions failed |
| `concurrent-strict-6.log` | `91d8ad096d0f26e1e87c44460082eedd52dcb6c4ca55ba6705eefb0a0072624a` | Exit 1; overlap and pointer assertions passed; admission fixture assertion failed |
| `concurrent-strict-7.log` | `8f4ea350dc585e3e7ffd21cc1a77f165b32f4b9d59356fb1f2887dc13a402375` | Exit 0 on pre-guard source; 467 tests, 1 TODO, 0 failures, 0 skips |
| `concurrent-strict-8.log` | `37249c67da32bd5ce14b67a63416a99ad371a8373cb8176c8daee52775e815d5` | Exit 0 on pre-guard source; 467 tests, 1 TODO, 0 failures, 0 skips |
| `concurrent-strict-9.log` | `e41574902d32272ac21010fcb877ccbbe7bb0020f054259d09026628e25fee29` | Exit 0 on pre-guard source; 467 tests, 1 TODO, 0 failures, 0 skips |
| `concurrent-serial-1.log` | `cebe320871e4ab287fa9af57049fc93a7cb57de8541146f80091a01e414d6f49` | Exit 0 on pre-guard source; 173 tests, 1 TODO, 0 failures, 0 skips |
| `concurrent-strict-10.log` | `f8a5ca4a6586d901d973597ea02b4eeafdf08fe0e409113ef79e1ed75a60d57c` | Final-source exit 0; 482 tests, 1 TODO, 0 failures, 0 skips |
| `concurrent-strict-11.log` | `dcd48e726a18cc495a957606f97b20680551d7a952e17f8e55f3014b243d42d7` | Final-source exit 0; 482 tests, 1 TODO, 0 failures, 0 skips |
| `concurrent-strict-12.log` | `1a7ae587495a37fd69606d990e5ac6f054b2395627aeeecfd7e4febb60f5f2a3` | Final-source exit 0; 482 tests, 1 TODO, 0 failures, 0 skips |
| `concurrent-strict-13.log` | `a62f7e5f4e66eda56cf721f0324c2235c2c431ed9c4ad34812b96ab10a2610ad` | Final-source exit 0; 482 tests, 1 TODO, 0 failures, 0 skips |
| `concurrent-serial-final.log` | `3d466097ba291b5e186fdbd269dd145c20e6ad334b6a2b98ab8f0e65258667db` | Final-source exit 0; 173 tests, 1 TODO, 0 failures, 0 skips |
| `concurrent-defaultoff-final.log` | `e94bd22602a4345e8d60af43afe1dd00afcd094ac8911163db760c5fe483ae3b` | Exit 21; full suite 34,593 tests, 169 TODOs, 21 failures, 1 skip; exact baseline diagnostics |
| `lease-concurrency-3.log` | `fc1d2ff908d0bf0673191289846fbc40c4e1f3bee3cb81fe34693479b144d00c` | Exit 0; 46 lease checks, 0 failures |
| `a1b-default-final.log` | `370a609dd100378b8dd44e2e467f3324f3eda4f7084e88cafed821f36b365bc8` | Exit 0; 249 live-private-view checks, 0 failures |

## Final-source concurrent result

Strict runs 7–9 passed before the same-logical-`KTHREAD` guard was added. Each
reported 467 tests, one existing `SignerSign` TODO, zero failures and zero
skips. These runs established the initial concurrent memory-view path and led
to an additional logical-thread reuse audit. The guard was added afterward and
was rebuilt before strict runs 10–13; those final-source runs each reported 482
tests, the same one TODO, zero failures and zero skips.

The current implementation detects an active request with that same `KTHREAD`
and parks the duplicate dispatch with `STATUS_DEVICE_BUSY`, retaining
single-owner IRP completion. The negative test submits a second IOCTL from the
same caller thread while a distinct peer request is outstanding, then checks
that both distinct logical threads still complete with independent views. The
final logs explicitly show duplicate lane 2 returning `ERROR_BUSY` while lane 0
remains pending, followed by the peer completing the shared barrier pair.

In the final-source healthy pairs, both lanes reached overlap mask `0xff`.
Ordinary reads observed opposing values (`0xa1/0xc3` and `0xb2/0xd4`) at the
same addresses and the peer lane's crossed values. The two concurrent lanes
reported distinct logical TIDs, `KTHREAD`s, IRPs, SystemBuffers, IO stacks,
`KAPC_STATE`s and stack locals. The harness also injected an uncaught fault into
one lane, confirmed the other lane continued, and passed another healthy pair.

Independent source/object review of the shared-stack bridge confirmed
that the worker bridge enters an ordinary compiled C root with AMD64 alignment
and home space, uses separate 256 KiB NX stacks with lower inaccessible guard
pages, restores native register context and TEB stack/exception-list fields,
and preserves normal `.pdata`/`.xdata` unwind metadata. Worker stack storage is
freed only after join. The review also confirmed fail-stop behavior for an
unexpected root fault. The same-thread guard was separately reviewed to reject
an active duplicate borrow before allocating a worker and to preserve
coordinator-only IRP completion. Independent final review approved the complete
17-file Wine diff and matched all 17 repository source hashes and all three
runtime/test artifact hashes in the completion manifest. It inspected the
generated code and unwind data. The disassembly was reviewed during the audit,
but no portable disassembly excerpt was retained as a separate file.

The prior [serial buffered-dispatch experiment](2026-10-10-e05-dispatch-chain.md)
passed three strict runs and a default-off full-suite baseline comparison for
its serial source. `concurrent-serial-final.log` passes the serial path on the
final concurrency source (173 tests, one TODO, zero failures/skips). The
default-off full suite reports 34,593 tests, 169 TODOs, 21 failures and one
skip. Its 37 normalized failure lines / 25 unique diagnostics exactly match
the retained baseline, with no candidate-only or baseline-only messages. The
standalone lease-concurrency fixture passes 46 checks and the default live
private-view fixture passes 249 checks, both with zero failures.

The final-source concurrency and serial builds and runs are complete. The
default-off candidate retains the same baseline failures. Preserve every
earlier failed attempt and the pre-guard passes in the evidence bundle. The
machine-readable final manifest at
`/home/eric/repos/proton-build-vanguard/e05-concurrent-20261011T060000Z/evidence/concurrent-dispatch-final-manifest.json`
has SHA256 `9dee8c5ac27dac7dabad60a51713e00b163f86c23d21566a647c502572f13ea8`.
The baseline comparison at
`/home/eric/repos/proton-build-vanguard/e05-concurrent-20261011T060000Z/evidence/defaultoff-baseline-comparison.json`
has SHA256 `128dd7911bfb6317f1156a35b9052267921b1534f1753fecaaaab49993d82161`.

The manifest records the pinned SteamRT4 x86_64 SDK digest, targeted build and
test commands, two-CPU/256-share Docker limit, `nice -n 15`, `ionice -c2 -n7`,
test UID, 17 modified-source hashes, artifact hashes, run hashes and statuses.
The final strict invocation used
`timeout --kill-after=15s 300s xvfb-run -a /src/tools/runtest -v -T /build -M /build/dlls/ntoskrnl.exe -p /build/dlls/ntoskrnl.exe/tests/x86_64-windows/ntoskrnl.exe_test.exe ntoskrnl`
with the strict environment values recorded in the manifest. The changed
`ntoskrnl.exe` runtime and tests were rebuilt; the full Wine and Proton builds
were not run.

At the four passing final-source runs, SHA256 was
`fbbdc1d40ffded64352b8b1ff39ef1ba12d34e1e224f48c61545fd25d4237e9d` for
`dlls/ntoskrnl.exe/ntoskrnl.c` and
`918a07f13d3bc380179f0b2cec39fe96f5bfd899785dc08d301dbd44b063d5d9` for
`dlls/ntoskrnl.exe/tests/ntoskrnl.c`. Runtime PE SHA256 is
`8d43ccc81e4200d7b96a8dbfebedbcfc136b39ef41cbbffeb6eb02e7d9c1689a`, the
test PE is `6c1227208d60f7cfe0c948ffd0efebb758506ecd88f4c00312f8d47c32a9ddac`,
and the benign driver fixture is
`7cd2084c928573e175e1205e92939d222854c8b8855b1da3d786ccf2c1eba3ec`. The
manifest records the full source and artifact hash set.

Next gates after this experiment remain imported writable-provider-global
coherence, broader native stack/address-space lifetime behavior, protection and
unmap/address reuse, process exit, i386/native Windows comparison, full Proton
integration, and genuine Vanguard session acceptance. These are separate from
this bounded concurrency result.
