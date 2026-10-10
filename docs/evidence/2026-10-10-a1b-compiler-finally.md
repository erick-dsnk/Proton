# 2026-10-10 — A1b compiler-generated `finally` on the migrated stack

Status: bounded Clang x64 compiler-generated cleanup and native-host return
passed. This is a test-only fixture; Wine attach behavior and Vanguard
acceptance remain unproven.

## Question and scope

After the raw continuation resumes in process B, can a genuine compiler-generated
x64 `__try`/`__finally` scope fault on the migrated shared stack, run its
normal and abnormal termination funclets in order, unwind through the existing
mapped root frames with `RtlUnwindEx`, and return through B's current native
bridge with deterministic cleanup?

The compiled helper is entered only after caller → A → B migration. Its single
parent function contains nested compiler-generated finally scopes and two
outlined funclets. The finally-bearing compiler frames themselves are not
migrated. The mapped raw root/outer/inner frames continue to use the separately
registered dynamic function table. A normal return and an abnormal fault path
exercise the same compiler scopes.

## Inputs and provenance

| Input | Exact value |
|---|---|
| Proton source | `c3547256adf6801cb45299690ea96ce208be097c` |
| Wine source/runtime base | `2990a75de24c57ab0a8ff2dc3caab7d075d4df40` |
| Final test source SHA256 | `8cff2b91509c6b8ac7fa66d1a173c72a73051820cbf6ffd01cc6548e15c78d07` |
| E05 driver/header SHA256 | `driver.c` `fce8e00475d848322c3f2facdc9c735050f75088b7d064bb8ac36486e34eaaf3`; `driver.h` `f6c980df543b3393ddb95f62277e3c61695d99d63fc8baae44790d60049e84dc` |
| SDK base | `registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64@sha256:97526b794ce1a9bed5f891084462260b3a02399569f7438a3a57b5a253001db9` |
| Derived SDK | disposable image `vanguard-finally-lld19:20261010T122603Z`, image ID `sha256:823a4b678b63391a70935c5751de961183e9276e533b2ee1993a2c8814bab137` |
| Added linker | Debian `lld-19` `1:19.1.7-3+b1`, package SHA256 `756a805e8811d527dd2b5417f016c9342b8631fa9c1ddcd56265c13ae33bf3a4`; `lld-link` SHA256 `7a2fd87d82662beac4371a1a21067b37cd4b7d43777aa61c089d85c45f772f6e` |
| Clang | Clang 19.1.7; preprocessor confirmed `_MSC_VER=1933` and `USE_COMPILER_EXCEPTIONS` |
| Architecture/configuration | x64 Wine test build, configured with `--enable-win64 --with-mingw=clang` |
| Final Clang test PE SHA256 | `4b96da45fec500b9d5f9993122022dc3a9ef2a309e340225d162a39bea8ee449` |
| Final Clang test object SHA256 | `368f5eda8eb63a3aa12f45af033fe0ec435e1ff058a710ca827735973999388a` |
| Runtime module SHA256 | Clang-built `ntoskrnl.exe` `a7fd7ff04a4c42695214463b35662ee21e842a387784d20084c7584b69f6ae92` |
| Same-Clang baseline test PE SHA256 | `596148c4aa9030d419363d894b2f32b2ef6034eafba018a1879e238b8afdb675` |
| Retained runtime host artifacts | `ntdll.so` `e6d869346277c1ba49c11dbf9529e6cbedd494b7e6ebe22ddf574bfa75b12fb1`; `wineserver` `907e99fd0458f1ccfd4a20281d84c7a918b4412b09ba8155891448410ad9bb2e`; Wine launcher `f4882de048f35d8bcba4de36ac857bf99ae24554013227037e672d76a9e1728f` |

The disposable scratch directory is
`/home/eric/repos/proton-build-vanguard/a1b-finally-20261010T122603Z`.
The derived image adds only the matching Debian LLD 19 package to the pinned
SDK; its image recipe and package logs are retained there. The original SDK
image was not modified. A first autogen/configure attempt was interrupted
(exit 141); the first Clang configuration could not find `lld-link`. After
installing the pinned package in the disposable derived image, autogen/configure
completed (exit 0). These preflight attempts did not produce runtime results.

The test source and object tree were copied into this isolated scratch build.
The full Wine runtime was not rebuilt: the test executable and the `ntoskrnl.exe`
module were built with Clang, while the existing ntdll, wineserver and Wine
launcher were retained. This is a Wine test-harness run, not a full Proton
build.

## Compiler artifact review

The final linked PE contains the helper at `0x1400105f0–0x1400106f7`, two
outlined termination funclets at `0x140010700` (inner) and `0x140010720`
(outer), and compiler exception metadata with four scope records and zero jump
targets. Its `.xdata` describes the real prologue (`push rbp`, `sub rsp, 0x60`,
`rbp = rsp + 0x60`) and imports `_C_specific_handler`. The saved return address
`0x14001066b` is inside both finally protected ranges
`[0x140010652,0x14001067b)`; the adjacent outer cleanup range
`[0x14001067a,0x140010685)` excludes that address. Independent PE/object review
confirmed the helper, metadata and scope boundaries.

An earlier candidate exposed an important PC boundary: its call return PC
`0x14001066b` fell in the inner and outer protected ranges and also in an
adjacent outer cleanup range, so Wine's x64 `_C_specific_handler` dispatched
inner/outer/outer and the test correctly failed its once-only count. The final
fixture moves a normal side effect after the protected call and records
normal/abnormal progress independently. This closes the overlap for this
observed return PC. Scope-range boundaries still require review for any other
compiler output; this fixture does not establish a general boundary rule.

## Commands and runtime

The same-Clang baseline was freshly configured and built from the unmodified
test source. Candidate test builds used:

```bash
make -j1 V=1 -C dlls/ntoskrnl.exe/tests
```

The strict suite ran in a fresh x64 prefix with the retained Wine runtime and
the Clang-built test module:

```bash
timeout --kill-after=15s 300s xvfb-run -a \
  /src/tools/runtest -v -T /build -M ntoskrnl.exe \
  -p /build/dlls/ntoskrnl.exe/tests/x86_64-windows/ntoskrnl.exe_test.exe \
  ntoskrnl
```

The final-source focused Clang build exited 0; log
`final-source-focused-build.log` SHA256
`1c749b75d28692d96bee73eefeeb54b5d3bf186839460cd088127e7d074c2299`. The
strict run exited 21; log `final-source-strict2.log` SHA256
`b0b78ca11a0f5329d29fac0872eb7990cc901365775bfc58451ea865214727f5`.
The Clang baseline strict log SHA256 is
`ce4df7c390e91afbfdc4b5b97a1d9664ede1380248496aa8fc3e74c138e18d68`.

The final trace records a real read AV in process B (PID 516, TID 520) at RIP
`0x180206b1`, RSP `0x1804feb8`, on the mapped shared stack. The two compiler
funclets each ran once on normal return and once with
`AbnormalTermination()==TRUE` on unwind. Normal/abnormal progress was `1/0`,
both resource locals were zeroed before reuse, and compiler cleanup error count
and mask were zero. The mapped raw frame handlers then ran search and cleanup
through inner/outer/root, with three search callbacks, three cleanup callbacks,
one root target and one landing, with zero errors. The landing reached
`0x1802016d` at RSP `0x1804ffc0` and preserved root local `0x1bc`.

Execution returned through B's current native bridge at RIP `0x140001795`,
RSP `0x10e9b0`, with 57 native ABI checks across three dispatches. The test
verified one TEB bound switch and restoration, process/thread identity, dynamic
table removal and absent lookup, handler removal, fault-page release, TLS
cleanup, and the subsequent healthy continuation. The original E05 IOCTL then
ran: all eight attached-read expectations remained `todo_wine`, with ordinary
pointer reads still raising access violations. No Vanguard driver acceptance
or game behavior was tested.

## Results and limits

| Run | Tests | Todos | Failures | Skipped | Exit | Interpretation |
|---|---:|---:|---:|---:|---:|---|
| Fresh same-Clang baseline | 34,593 | 169 | 21 | 0 | 21 | Unmodified test source, same Clang configuration |
| Final compiler-finally candidate | 34,650 | 169 | 21 | 0 | 21 | 57 additional checks; all new assertions passed |
| Final GCC default-path check | 34,593 | 169 | 21 | 1 | 21 | Focused GCC build passed; compiler-finally case explicitly skipped |

The 37 normalized failure lines (25 unique diagnostics) were identical as a
multiset between the same-Clang baseline and candidate. This suite remains
non-green; the unchanged baseline failures are not passes. Three earlier
candidate snapshots are retained locally: source hashes `65e6b3a5…`,
`25bfad6d…`, and `6c58093d…` each had two additional assertions and suite
results of 34,650 / 169 / 23 / 0 (exit 23). Each produced two new assertions
from the real extra funclet dispatch caused by the scope-boundary overlap.
They are preserved rather than replaced by the final passing run.

The final GCC run compiled the same source and explicitly skipped only this
compiler-finally case because its native `__try`/`__finally` support is
unavailable in that compiler configuration. Focused build log SHA256
`f2c1a2fb35d8f23feaafe47ea75282a1b78d37af8f415cee39099511853f5f2f`; test PE
SHA256 `f1b225e13be4042d96add3b4c9b48900b9218eeb2c8e358acb9cf66f8624d344`,
test object SHA256 `6c7640e757388be93b0648878235c875be356f1c666ac1c4a245a217447a7bb2`;
strict log `final-source-strict.log` SHA256
`3557d41f8992ef9b140a3daab2e57f3ff5a9251e7d996f78d0a525eb741b6504`. An
earlier GCC guard used `win_skip`, which Wine counts as a failure (34,594 /
169 / 22 / 0, exit 22). The final source uses unconditional `skip`; that
failed guard attempt remains retained locally and is excluded from the final
GCC result.

The evidence is limited to compiler-generated cleanup in the linked helper
after arrival in B, on this x64 Wine test runtime and exact PE scope table. It
does not establish that compiler-generated frames migrate between processes,
that all compiler PC-boundary arrangements are safe, or that arbitrary faults,
collisions, helper ranges, asynchronous switching, concurrency, native Windows,
i386, or target-exit races are handled. Wine `KeStackAttachProcess` remains
unimplemented in the tested runtime; E05 still falsifies its ordinary pointer
read behavior. Vanguard acceptance and gameplay remain unknown.

## References

- [Microsoft: x64 exception handling](https://learn.microsoft.com/en-us/cpp/build/exception-handling-x64?view=msvc-170), accessed 10 October 2026.
- [Wine x64 `_C_specific_handler`](https://github.com/erick-dsnk/wine/blob/084fc093b4eaec9f66a942f5d902496318762abb/dlls/ntdll/unwind.c) contains the runtime scope-table dispatch exercised by this fixture.
- [Previous mapped frame-unwind experiment](2026-10-10-a1b-frame-unwind.md) documents the raw parent frames and `RtlUnwindEx` landing.
- [E05 attachment falsifier](2026-10-10-e05-attachment-falsifier.md) documents the separate unimplemented attachment contract.
