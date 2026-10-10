# 2026-10-10 — A1b same-continuation migration prototype

Status: bounded x64 test-only prototype passed its raw continuation checks.
This does not implement `KeStackAttachProcess` or `KeUnstackDetachProcess`,
establish Vanguard call-path relevance, or close G2.

## Question and scope

Can one cooperative raw x64 continuation start once in the caller, suspend and
resume on the same shared stack through caller → A → B → A → caller, preserve
its live nested call frames and supported register state, read each host's
private mappings directly, and return through its real nested return chain?

The continuation fixture runs after the unchanged shared-region gate 1 and
before the original E05 driver IOCTL. The root starts once and completes once.
Four saved post-yield checkpoints resume in the next process. The mapped probe
uses three nested stack-local cookies, accumulates each directly loaded common
private byte in a live local (`0x2b6`), and returns through the actual root
return address to a mapped finish thunk. At each resume it validates the saved
register snapshot before continuing. The native bridge has its own separately
saved state.

## Inputs

| Input | Exact value |
|---|---|
| Proton source | `c3547256adf6801cb45299690ea96ce208be097c` |
| Wine source/runtime | `2990a75de24c57ab0a8ff2dc3caab7d075d4df40` |
| Continuation test source | `dlls/ntoskrnl.exe/tests/ntoskrnl.c`, SHA256 `8bdb1cfb65733199564cf1d92b5a369703ebfe736a31b754a09f59f7e09ceba0` |
| E05 test driver/header | `driver.c` SHA256 `fce8e00475d848322c3f2facdc9c735050f75088b7d064bb8ac36486e34eaaf3`; `driver.h` SHA256 `f6c980df543b3393ddb95f62277e3c61695d99d63fc8baae44790d60049e84dc` |
| SDK | `registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64@sha256:97526b794ce1a9bed5f891084462260b3a02399569f7438a3a57b5a253001db9` |
| Configuration | Wine x64 (`--enable-win64`); focused tests target built with `make -j1 V=1 -C dlls/ntoskrnl.exe/tests` |
| Built test PE | SHA256 `d486ea3bf021c22aa3246a7c3cba1abb91f4f08191ac9e344e60fd83f28cdcf7` |
| Runtime module | SHA256 `718e7adb5accf155445c60dfb9426274ed6a232a5b4943d5a7577b25b03e85b1`; reused from the retained full Wine runtime, not rebuilt by this focused test build |

The scratch directory is
`/home/eric/repos/proton-build-vanguard/a1b-continuation-20261010T110620Z`.
The complete run log is retained locally at
`evidence/continuation-strict-20261010T111725Z-147747.log`, SHA256
`269d01aaeb0bec6ca8a0f7cef8bfbdb452262f73dc85a5ae14e07d89a5b34be1`.
The normalized failure comparison is `evidence/failure-comparison.json`,
SHA256 `80fec6a352e6db3a3044e248a87e5d491e90b1afa07cfa44ca5104bcc0b1f320`.
These raw logs/artifacts are local and are not part of this repository.

Focused build command (exit 0):

```bash
make -j1 V=1 -C dlls/ntoskrnl.exe/tests
```

Strict generic driver suite command (exit 21):

```bash
timeout --kill-after=15s 300s xvfb-run -a \
  /src/tools/runtest -v -T /build -M ntoskrnl.exe \
  -p /build/dlls/ntoskrnl.exe/tests/x86_64-windows/ntoskrnl.exe_test.exe \
  ntoskrnl
```

The run used a fresh win64 prefix and the retained `2990a75` Wine runtime in
the pinned SDK. It was a focused test build and x64 runtime test, not a fresh
full Wine build or complete Proton integration build.

## Results

The runner recorded one root start, one completion, and hosting PIDs
caller/A/B/A/caller = `32/532/540/532/32`. Four saved continuation checkpoints
resumed at approved instruction pointers and supported stack positions. The
live GPR/XMM/MXCSR/safe-flags checks passed on all four resumes (4/4); the
separate native-bridge preservation checks passed on all five dispatches
(95/95). There were zero continuation errors. The mapped continuation's
accumulator reached `0x2b6`, consistent with the common private bytes
`0x59 + 0xa1 + 0xb2 + 0xa1 + 0x59`; a separate shared accumulator reached
`0x2a6`. The stack-local cookies and actual nested return chain survived
through the mapped finish thunk, which completed once.

Admission controls rejected invalid instruction pointer, out-of-range and
misaligned stack pointer, corrupted call return, trap flag, invalid control
pointer, corrupted outer return, cancellation, invalid state, wrong owner or
generation, and a terminal restart without dispatch. The reviewer also
confirmed that the mapped probe is confined to its intended blob with no
relocations and that the native bridge has unwind metadata.

The unchanged original E05 fixture then ran: its valid stack-read and guarded
fault controls remained intact, while the eight direct attached-process
expectations remained `todo_wine` with the existing access violations. The
full suite reported **34,388 tests, 169 todos, 21 failures, 0 skipped; runner
exit 21**. It is not a green suite. Comparing normalized `Test failed:`
diagnostics with the gate 1 run produced 37 lines / 25 unique messages in each,
with no new, missing, or count-mismatched diagnostic.

## Conclusion and remaining gates

This observes that a cooperative raw x64 continuation can preserve the tested
stack frames and supported register state while resuming serially in the
caller's and two child processes' distinct address spaces. It completes the
next bounded A1b prototype step. It is not Wine process-attachment behavior:
the driver thread, TEB/TLS and OS thread identity did not migrate, and synthetic
stack exceptions/unwinding were not exercised.

Native Windows reference, i386 ABI/layout/runtime coverage, fault recovery and
exception/unwind behavior, logical thread/TLS identity, concurrency, target
exit/unmap races, non-cooperative targets, ordinary Wine attach semantics,
Vanguard dependency evidence, authentic Linux acceptance, and gameplay remain
open. The result does not establish that Vanguard uses this contract.
