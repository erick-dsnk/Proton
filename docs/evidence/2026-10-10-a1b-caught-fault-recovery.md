# 2026-10-10 — A1b caught-fault recovery on a migrated stack

Status: bounded x64 test-only VEH recovery and native-host cleanup passed.
Claim label: Observed. This does not implement Windows table SEH, generic stack
unwinding, or Wine process attachment.

## Question and scope

Can a migrated continuation in process B take a real, deliberately induced
read access violation on its shared stack, have a narrowly armed process-local
vectored exception handler (VEH) validate and consume that event, abandon the
faulted continuation through the current bridge's native return path, clean up
the handler and fault allocation, and leave the dispatch machinery usable for
a later healthy continuation?

The fixture also raised an unrelated native access violation while the recovery
handler was armed. The recovery handler passed it to an ordinary catcher. After
the handled fault, the fixture rejected restart of the terminal continuation,
ran a fresh healthy continuation, and then ran the unchanged E05 driver IOCTL.
The synthetic continuation's TEB stack bounds were observed unchanged.

## Inputs

| Input | Exact value |
|---|---|
| Proton source | `c3547256adf6801cb45299690ea96ce208be097c` |
| Wine source/runtime | `2990a75de24c57ab0a8ff2dc3caab7d075d4df40` |
| Changed test source | `dlls/ntoskrnl.exe/tests/ntoskrnl.c`, SHA256 `5c1d126dec5e8cbc40c33ae5a5da1b3899fd30f7f65eee029f3668874c368d72` |
| E05 driver/header | `driver.c` SHA256 `fce8e00475d848322c3f2facdc9c735050f75088b7d064bb8ac36486e34eaaf3`; `driver.h` SHA256 `f6c980df543b3393ddb95f62277e3c61695d99d63fc8baae44790d60049e84dc` |
| SDK | `registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64@sha256:97526b794ce1a9bed5f891084462260b3a02399569f7438a3a57b5a253001db9` |
| Configuration | Wine x64 (`--enable-win64`); focused `ntoskrnl.exe` test build |
| Test PE | SHA256 `e5ff750fdc3b75aab59b6d262b10dd2422ff4c35d480ad068e07c2aeff6e6909` |
| Test object | SHA256 `0338961fad40921c009456f19dc93fd527a4f9bfd637cb6dbc96760a6ad1a8ac` |
| Reused Wine runtime | SHA256 `718e7adb5accf155445c60dfb9426274ed6a232a5b4943d5a7577b25b03e85b1`; not rebuilt in this focused test build |

The isolated scratch directory is
`/home/eric/repos/proton-build-vanguard/a1b-fault-recovery-20261010T112641Z`.
The complete final run log is retained locally at
`fault-strict-final-20261010T113551Z.log`, SHA256
`d7fe244f568a54002f1a9f256c6b5df90498ddee9e8c0b9958c287589a61af64`.
These build outputs and logs are local and are not included in this repository.

## Commands and artifacts

The scratch source copy was regenerated and configured for x64 with
`cd /src && ./autogen.sh && cd /build && /src/configure --enable-win64`
(exit 0). The final focused test build exited 0:

```bash
make -j1 V=1 -C dlls/ntoskrnl.exe/tests
```

The strict generic driver suite ran in a fresh prefix with the retained Wine
runtime and the newly built test PE. Its runner exit was 21:

```bash
timeout --kill-after=15s 300s xvfb-run -a \
  /src/tools/runtest -v -T /build -M ntoskrnl.exe \
  -p /build/dlls/ntoskrnl.exe/tests/x86_64-windows/ntoskrnl.exe_test.exe \
  ntoskrnl
```

The test used the pinned Steam Runtime 4 SDK above. It was a focused x64 test
build against a retained runtime, not a fresh complete Wine build or Proton
integration build.

## Results

The real fault was `STATUS_ACCESS_VIOLATION` (`0xc0000005`), a read (`0`) from
address `0xc00000`, at mapped instruction `0x18020224` with shared-stack RSP
`0x1804ff60`. It occurred in process B (PID 540, TID 544). The recovery
handler recorded its local stack address `0x1804efd8`, accepted the event once,
and redirected execution to that dispatch's native bridge return (`RIP
0x1400016cc`, `RSP 0x31eec0`). The native bridge completed three dispatches
with 57 ABI checks. The handler was removed, the fault allocation released,
and TEB stack bounds remained unchanged (1/1/1 recorded checks).

The unrelated native access violation passed the armed recovery handler and
reached the ordinary catcher. A restart attempt against the faulted terminal
continuation was rejected. A fresh healthy continuation then completed its
caller/A/B/A/caller sequence with 95 native ABI checks and four live-state
resumption checks. Both target processes remained available for the original
E05 IOCTL, which retained its eight attachment `todo_wine` expectations.

The final full suite reported **34,546 tests, 169 todos, 21 failures, 0
skipped; runner exit 21**. That is 158 checks above the retained continuation
run (34,388). All 37 normalized failure lines and 25 unique diagnostics match
that run exactly; no failure was added or removed. This is not a green suite.

An earlier candidate run was superseded after its test oracle expected the
wrong continuation accumulator/local values. It reported 34,546 tests, 169
todos, 22 failures, no skips, exit 22; the one additional failure was this
oracle error. The expected values and diagnostics were corrected before the
final build and run. Its local log is `fault-strict-20261010T113333Z.log`,
SHA256 `3091c9222b5a1ad6a365e963770ab194b0ffffb3517daa8170160f7c44736e2d`.
It remains excluded from the final comparison.

## Conclusion and remaining gates

This observes a narrow VEH first-chance recovery path that recognizes one real
access violation on the migrated shared stack, aborts that continuation, and
returns through the matching native host bridge with deterministic handler and
fault-allocation cleanup. It also observes that the handler passes an unrelated
native fault to the ordinary catcher and that a later healthy continuation
still succeeds. The original E05 fixture still shows the current Wine attach
implementation's eight direct-read expectations unmet.

VEH dispatch and redirection are not table-based SEH or stack unwinding. This
result does not show language `finally`/destructor execution, unwind cleanup of
the faulted continuation's frames, arbitrary-fault recovery, resumption of the
faulted instruction, recovery when the handler itself faults, or stack-overflow
handling. It is an x64 Wine test experiment; native Windows and i386 validation,
Wine `KeStackAttachProcess` semantics, logical thread/TLS identity, concurrency,
target-exit/unmap races, Vanguard relevance, authentic Linux acceptance, and
gameplay remain open.

## References

- [Microsoft: Vectored Exception Handling](https://learn.microsoft.com/en-us/windows/win32/debug/vectored-exception-handling), accessed 10 October 2026.
- [Microsoft: AddVectoredExceptionHandler](https://learn.microsoft.com/en-us/windows/win32/api/errhandlingapi/nf-errhandlingapi-addvectoredexceptionhandler), accessed 10 October 2026.
- [Wine exception dispatch](../../wine/dlls/ntdll/exception.c) runs vectored handlers before table-based exception dispatch.
- [Previous A1b continuation record](2026-10-10-a1b-continuation-migration.md) describes the serial migration fixture and its supported register state.
