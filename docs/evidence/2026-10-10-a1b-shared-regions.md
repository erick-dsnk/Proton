# 2026-10-10 — A1b shared execution-region prerequisite

Status: completed, test-only prerequisite. Claim label: observed for the
recorded x64 Wine runtime and benign cooperative fixture. This does not
implement process attachment or establish Vanguard call-path relevance.

## Question and scope

Can the caller and two cooperative child processes map the same executable code,
read/write data/control, and read/write stack sections at identical virtual
addresses, then execute a position-independent leaf in each process while
retaining distinct private mappings and coherent shared state?

The fixture makes five serial fresh calls in the order caller, A, B, A, caller.
The E05 driver IOCTL follows unchanged while both children remain live. This is
A1b gate 1 only. Each process starts a new leaf invocation and returns to its
own native continuation; the fixture does not migrate one continuation between
processes and does not change Wine's `KeStackAttachProcess` implementation.

## Inputs

| Input | Exact value |
|---|---|
| Proton source | `c3547256adf6801cb45299690ea96ce208be097c` |
| Wine source/runtime | `2990a75de24c57ab0a8ff2dc3caab7d075d4df40` |
| Test-source overlay | Only `dlls/ntoskrnl.exe/tests/ntoskrnl.c` changed for A1b; SHA256 `91bd79cb04c45dda502a05b94ca7c133409aa26b1ca5b6fd7aedd3ca3f7464d6`. E05 `driver.c` and `driver.h` stayed at `fce8e00475d848322c3f2facdc9c735050f75088b7d064bb8ac36486e34eaaf3` and `f6c980df543b3393ddb95f62277e3c61695d99d63fc8baae44790d60049e84dc`. |
| SDK | `registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64@sha256:97526b794ce1a9bed5f891084462260b3a02399569f7438a3a57b5a253001db9` |
| Toolchain | GCC 14.2.0; MinGW x86_64 GCC 14-win32; GNU make 4.4.1; GNU ld 2.44; Autoconf 2.72 |
| Host / architecture | Ubuntu 24.04.4, kernel `7.0.0-38-generic`, x86_64; Wine configured `--enable-win64` |
| Source-copy check | A1b `ntoskrnl.c` source and copied build source had the same SHA256 above; the two E05 test files also matched their E05 hashes. |

## Commands and artifacts

The isolated scratch directory was
`/home/eric/repos/proton-build-vanguard/a1b-gate1-20261010T104651Z-110452`.
The run used `RUN_DIR` for that path, `BUILD_USER=1000:1000`, and `SDK` for
the pinned digest above. Build command exit files and complete logs remain in
the local evidence directory; they are not committed or publicly retrievable.

```bash
docker run --rm -v "$RUN_DIR/wine-src:/src" -v "$RUN_DIR/wine-obj:/build" -w /src --user "$BUILD_USER" -e HOME=/build/home -e XDG_CACHE_HOME=/build/cache "$SDK" bash -lc 'mkdir -p "$HOME" "$XDG_CACHE_HOME" && ./autogen.sh'
# exit 0

docker run --rm -v "$RUN_DIR/wine-src:/src" -v "$RUN_DIR/wine-obj:/build" -w /build --user "$BUILD_USER" -e HOME=/build/home -e XDG_CACHE_HOME=/build/cache "$SDK" bash -lc 'mkdir -p "$HOME" "$XDG_CACHE_HOME" && /src/configure --enable-win64'
# exit 0

docker run --rm -v "$RUN_DIR/wine-src:/src" -v "$RUN_DIR/wine-obj:/build" -w /build --user "$BUILD_USER" -e HOME=/build/home -e XDG_CACHE_HOME=/build/cache "$SDK" bash -lc 'make -j1 V=1 -C dlls/ntoskrnl.exe/tests'
# exit 0

docker run --rm -v "$RUN_DIR/wine-src:/src" -v "$RUN_DIR/wine-obj:/build" -w /build --user "$BUILD_USER" -e HOME=/build/home -e XDG_CACHE_HOME=/build/cache -e WINEPREFIX=/build/prefix-a1b-shared-20261010T105413Z-118995 -e WINEARCH=win64 -e 'WINEDLLOVERRIDES=mscoree,mshtml=' "$SDK" bash -lc 'timeout --kill-after=15s 300s xvfb-run -a /src/tools/runtest -v -T /build -M ntoskrnl.exe -p /build/dlls/ntoskrnl.exe/tests/x86_64-windows/ntoskrnl.exe_test.exe ntoskrnl'
# runner exit 21
```

The full test log is retained locally at
`/home/eric/repos/proton-build-vanguard/a1b-gate1-20261010T104651Z-110452/evidence/a1b-shared-20261010T105413Z-118995.log`, SHA256
`ac59a580bf15079264e55a65b46d2530e651dbfd209d4ec2de196c426ab4d03b`. The
focused build log is `evidence/build-tests.log`, SHA256
`f2c1a2fb35d8f23feaafe47ea75282a1b78d37af8f415cee39099511853f5f2f`, exit 0.
The normalized-failure comparison is `evidence/failure-comparison.json`, SHA256
`80ea13e24d892d36b20260ef89295caba6bb37ef2452a368233e5093b0369fb7`.

Final artifacts:

| Artifact | SHA256 |
|---|---|
| Runtime `ntoskrnl.exe` | `718e7adb5accf155445c60dfb9426274ed6a232a5b4943d5a7577b25b03e85b1` (copied from the retained full Wine runtime; byte-identical, not rebuilt by this focused test build) |
| `ntoskrnl.exe_test.exe` | `9d3e123ce0829d8821b901e9c5ef8b5585ad88020e382b3aa79e081b3d45cb74` |
| `driver.dll` | `0aa14dc68ae4c60552f7ca90875ccf31be3e03d573d5b421d85b4aef485148fd` |
| A1b test-source delta | `48dbd30229b7baa2d68ed52e32a0e8481b0c79d4e6ecf135f764340cb9c45a43` |

The full A1b source delta is retained outside the repository and includes the
unchanged E05 test overlay; it is not a Proton/Wine commit.

## Results

The fixture mapped the 72-byte relocation-free shared code leaf as RX at
`0x18020000`, shared RW data/control at `0x18030000`, and a 64 KiB RW stack at
`0x18040000` in caller, A and B. `VirtualQuery` checked expected addresses,
mapped backing and protections. The negative control attempted an RX section
mapping over an occupied private address; the mapping was rejected and its
sentinel stayed intact. Children reported readiness and remained alive until
the unchanged E05 IOCTL completed.

The strict log observed these serial calls:

| Owner | Sequence / prior stack value | Shared RIP / RSP | Private common / target load | Native stack restored | RBX/RBP mask |
|---|---|---|---|---|---|
| Caller | 1 / 0 | `0x18020011` / `0x1804ffc8` | `0x59` / not read (target-only address absent) | yes | `3` |
| A | 2 / 1 | same | `0xa1` / `0xc3` | yes | `3` |
| B | 3 / 2 | same | `0xb2` / `0xd4` | yes | `3` |
| A again | 4 / 3 | same | `0xa1` / `0xc3` | yes | `3` |
| Caller again | 5 / 4 | same | `0x59` / not read | yes | `3` |

Shared data and mapped-stack values advanced coherently from 1 through 5;
stack-boundary canaries stayed intact. The leaf did not call APIs or raise
faults while on the synthetic stack, and that stack has no unwind metadata.
The wrapper ran on each process's native stack and reported it restored after
the leaf. The `registers=3` mask confirms both full-width RBX and RBP sentinels.

The unchanged E05 driver fixture then passed its valid kernel-stack read,
caught NULL fault, both process lookups, and child-liveness controls. Its eight
attachment expectations remained `todo_wine`; all five direct pointer-read
phases still raised access violations. The suite summary was **34,267 tests,
169 todos, 21 failures, 0 skipped, runner exit 21**. That is 82 additional
checks versus E05's 34,185. Normalizing only the source-file/line prefix from
`Test failed:` diagnostics produced 37 lines / 25 unique messages for each
run, with no added, missing, or count-mismatched message.

The runner was not green: its 21 suite failures remain. The comparison shows
that this test-only increment added no new normalized failure or skip against
the retained E05 run. It is not an unpatched Wine or Windows comparison.

## Conclusion and next action

The experiment passed the **shared-region prerequisite**: three cooperative
processes could execute a fresh leaf using identically mapped shared code,
data/control and stack while seeing coherent shared writes and their own
private bytes, and returning to their native stack with the checked nonvolatile
registers restored. This supports testing whether a single suspended logical
continuation can next resume in caller → A → B → A → caller address spaces.

It does not establish that a thread or continuation migrated. Each process
started a fresh invocation from its own event handler and returned on its own
native continuation. Actual `KeStackAttachProcess` behavior is unchanged and
still fails the E05 direct-read probes. Fault recovery/unwinding on the shared
stack, TEB/TLS and thread identity preservation, concurrent logical threads,
target exit/unmap during a call, native Windows, i386, Vanguard call-path
relevance, genuine Linux verifier acceptance, accepted sessions and gameplay
remain untested or unknown. Keep address-space-dependent memory exports gated.

The next bounded gate is a benign same-continuation migration prototype that
preserves one logical stack and registers while switching through A and B,
performing ordinary loads and restoring the original continuation. Failure to
preserve exceptions, thread identity, target lifetime or cleanup should be
recorded before choosing another execution substrate. G1 remains independent.

## References

- [Architecture gate](../ARCHITECTURE.md#current-e05-result)
- [E05 falsifier](2026-10-10-e05-attachment-falsifier.md)
- [Testing and evidence requirements](../TESTING.md)
