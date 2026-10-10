# 2026-10-10 — A1b frame-based unwind on a migrated shared stack

Status: bounded x64 table-handler search, `RtlUnwindEx`, unwind cleanup and
native-host return passed.
Claim label: Observed. This does not implement general Windows exception
handling, Wine process attachment, Vanguard acceptance or gameplay.

## Question and scope

Can the cooperative caller → A → B continuation take a real read access
violation in B's mapped inner frame, use registered x64 function-table
metadata for real search and unwind dispatch, run per-frame unwind handlers,
land at a mapped root target, and return through B's current native bridge
with deterministic cleanup?

This experiment exercises three deliberately described mapped frames (root,
outer and inner) and their real unwind callbacks. It switches the active TEB
stack interval to the mapped shared stack only while executing that stack, then
restores `StackLimit`, `StackBase` and `DeallocationStack` before native code
resumes. Process/thread identity and a TLS sentinel are checked across the
fault and return. The existing VEH abort is a separate earlier result; it does
not consume the fault in this experiment.

## Inputs

| Input | Exact value |
|---|---|
| Proton source | `c3547256adf6801cb45299690ea96ce208be097c` |
| Wine source/runtime | `2990a75de24c57ab0a8ff2dc3caab7d075d4df40` |
| Changed test source | `dlls/ntoskrnl.exe/tests/ntoskrnl.c`, SHA256 `e741dc0ed4ebcc98da06b2427caaa6af3d8494441d868918b1aef39a201f1101` |
| E05 driver/header | `driver.c` SHA256 `fce8e00475d848322c3f2facdc9c735050f75088b7d064bb8ac36486e34eaaf3`; `driver.h` SHA256 `f6c980df543b3393ddb95f62277e3c61695d99d63fc8baae44790d60049e84dc` |
| SDK | `registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64@sha256:97526b794ce1a9bed5f891084462260b3a02399569f7438a3a57b5a253001db9` |
| Configuration | Wine x64 (`--enable-win64`); focused `ntoskrnl.exe` test build |
| Test PE | SHA256 `8eb29a8c3fa936618592c13b4195894dc33ec78ace770acd8cce7b197039c9fb` |
| Test object | SHA256 `99530d014916865d463a1d622959db69b7b5724aa7d21f44c90ad4c2ad96f655` |
| Reused Wine runtime | `ntoskrnl.exe` SHA256 `718e7adb5accf155445c60dfb9426274ed6a232a5b4943d5a7577b25b03e85b1`; `ntdll.so` SHA256 `e6d869346277c1ba49c11dbf9529e6cbedd494b7e6ebe22ddf574bfa75b12fb1` |

The isolated scratch directory is
`/home/eric/repos/proton-build-vanguard/a1b-frame-unwind-20261010T114437Z`.
The copied source omitted `.git`; the object tree was copied with
`cp -a --reflink=never` and has no external hardlinks. These outputs are local
and are not distributed with the repository.

Independent source/object/PE review confirmed the 1,431-byte copied code blob
has no text relocations. Its registered ranges are root `0x100–0x18c`, outer
`0x1ae–0x22d`, and inner `0x22d–0x2b6`, with truthful prologue lengths of
8/4/4 bytes and unwind descriptions for each actual `0x28` stack allocation.
The snapshot/check/yield helper ranges are excluded. The mapped handler thunk
uses dispatcher `ImageBase` to reach current process-local authority; it does
not rely on migrated R15. The linked root handler calls `RtlUnwindEx` at
`0x140003ad2`.

## Commands and artifacts

The scratch source was regenerated and configured for x64; the command exited
0. The retained log `autogen-configure-frozen.log` has SHA256
`ef4f073f716b1a9fadf596423b75ea16139ea6036a2ba1ae7188fcc693439a38`. The
focused test build exited 0:

```bash
make -j1 V=1 -C dlls/ntoskrnl.exe/tests
```

Its log `focused-build.log` has SHA256
`10385a505674e2dfc4d97414248ea4f14f62607dfeb77f33554df934db16cc54`.
The strict suite used a fresh win64 prefix with the unused CLR/HTML installers
disabled. Its runner exited 21:

```bash
timeout --kill-after=15s 300s xvfb-run -a \
  /src/tools/runtest -v -T /build -M ntoskrnl.exe \
  -p /build/dlls/ntoskrnl.exe/tests/x86_64-windows/ntoskrnl.exe_test.exe \
  ntoskrnl
```

The retained log is
`frame-unwind-strict-20261010T115927Z.log`, SHA256
`bbccf264623d285c9ffe55ba291602523ab8edf5a8dc42e0cc13dcec5e7d0aa1`. This
was a focused fresh test-PE build against the retained runtime, not a fresh
complete Wine or Proton build.

## Results

The real `STATUS_ACCESS_VIOLATION` (`0xc0000005`) was a read (`0`) from
`0xc00000` at mapped instruction `0x18020282`, with shared-stack RSP
`0x1804ff60`, in process B (PID 544, TID 548). The active TEB bounds were the
actual shared mapping `0x18040000–0x18050000`, with
`DeallocationStack=0x18040000`. Three registered frame entries resolved to
the expected root/outer/inner code ranges; the helper ranges were excluded.

The table-based search handlers ran in inner → outer → root order (frame IDs
2, 1, 0), at establisher addresses high−`0xa0`, high−`0x70`, and high−`0x40`;
all search flags were zero. `RtlUnwindEx` then invoked actual unwind handlers
in the same order. They consumed three frame-owned resource tokens exactly
once, with flags `0x2`, `0x2`, and `0x22`; the root callback carried the target
unwind flag. The observed counts were three search callbacks, three cleanup
callbacks, one root-target callback and one landing, with zero recorded
errors. The root landing was RIP `0x1802016d`, RSP `0x1804ffc0` (high−`0x40`),
and retained the captured root local `0x1bc`.

The landing returned through B's current native bridge at RIP `0x140001775`
and native RSP `0x31edc0`. The three dispatches passed 57 native ABI checks.
The shared TEB bounds were restored before native execution (one switch and
one restoration), actual process/thread identity was preserved, and the TLS
sentinel was checked during handler execution and native return. The dynamic
function table was removed and lookup confirmed it absent; the fault handler
was removed, the fault page released, the allocated TLS slot cleaned, and
shared authority pointers cleared. A terminal restart was rejected.

A later healthy continuation completed, as did the native-stack fault control
path. The unchanged E05 IOCTL still showed its eight attachment
`todo_wine` expectations: ordinary pointer reads for caller/A/B phases remain
access violations in this Wine runtime. This does not implement
`KeStackAttachProcess` semantics.

The strict suite reported **34,593 tests, 169 todos, 21 failures, 0 skipped;
runner exit 21**. It adds 47 checks over the caught-fault run (34,546 / 169 /
21 / 0). All 37 normalized `Test failed:` lines and 25 unique diagnostics
match that baseline as a multiset; there were no added or removed failures.
The full suite is not green. In the retained run, the unwind trace is at lines
64–67, E05's unchanged results are at lines 83–97, and the summary is at line
378.

## Conclusion and remaining gates

This observes table-based search through three registered mapped frames,
actual `RtlUnwindEx` to a root target, one-time resource cleanup through real
unwind callbacks, and return through the current native host bridge. The
active TEB stack bounds were scoped to the shared mapping and restored before
native code resumed; process/thread identity and a TLS sentinel were checked.
The result is specific to this cooperative, serial, fully committed x64
fixture.

It does not establish compiler-generated C++ destructors or `__finally`,
unwinding arbitrary helper ranges, exception collisions, stack-overflow
handling, asynchronous or concurrent switching, target-exit races, native
Windows or i386 behavior, Wine attachment semantics, Vanguard relevance,
authentic Linux acceptance, or gameplay. E05's eight attachment expectations
remain unmet.

## References

- [Microsoft: x64 exception handling](https://learn.microsoft.com/en-us/cpp/build/exception-handling-x64?view=msvc-170), accessed 10 October 2026.
- [Microsoft: `RtlAddFunctionTable`](https://learn.microsoft.com/en-us/windows/win32/api/winnt/nf-winnt-rtladdfunctiontable), accessed 10 October 2026.
- [Microsoft: `RtlUnwindEx`](https://learn.microsoft.com/en-us/windows/win32/api/winnt/nf-winnt-rtlunwindex), accessed 10 October 2026.
- [Microsoft: `RtlDeleteFunctionTable`](https://learn.microsoft.com/en-us/windows/win32/api/winnt/nf-winnt-rtldeletefunctiontable), accessed 10 October 2026.
- [Wine dynamic-function-table tests](../../wine/dlls/ntdll/tests/exception.c) provide benign registration and target-unwind examples.
- [Previous caught-fault record](2026-10-10-a1b-caught-fault-recovery.md) documents VEH abort and cleanup, a separate mechanism.
