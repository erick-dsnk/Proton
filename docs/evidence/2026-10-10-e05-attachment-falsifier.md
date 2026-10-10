# 2026-10-10 — E05 process-attachment falsifier

Status: completed, test-only. Claim: observed for the tested x64 Wine A1
implementation. No Vanguard binary or target session was used.

## Question and scope

Can a benign driver perform ordinary pointer reads in the process address
space selected by `KeStackAttachProcess`, then restore the prior context on
detach? This is a falsifier for the current Wine implementation, not evidence
that Vanguard reaches this API and not a test of every possible user-space
architecture.

The fixture created two live child processes with different bytes at the same
virtual address (`0x18000000`) and a target-only mapping at `0x18010000`. It
checked a valid kernel-stack read (`0x7e`), caught a NULL-read access violation,
looked up both process objects, and checked child liveness before and after the
IOCTL. In all five direct-read phases around attach/detach, probes of the common
and target-only addresses available in that phase raised
`STATUS_ACCESS_VIOLATION`. The children remained alive afterward and exited
normally during cleanup. Eight attachment expectations are marked `todo_wine`;
no E05 assertion failed or skipped.

## Inputs and build

| Input | Value |
|---|---|
| Proton source | `c3547256adf6801cb45299690ea96ce208be097c` |
| Wine source/runtime | `2990a75de24c57ab0a8ff2dc3caab7d075d4df40` |
| Wine test-only overlay | `dlls/ntoskrnl.exe/tests/driver.c`, `driver.h`, `ntoskrnl.c`; hashes `fce8e004…`, `f6c980df…`, `2904bcd7…` |
| SDK | `registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64@sha256:97526b794ce1a9bed5f891084462260b3a02399569f7438a3a57b5a253001db9` |
| Host / architecture | Ubuntu 24.04.4, kernel `7.0.0-38-generic`, x86-64; Wine configured `--enable-win64` |
| Runtime module | SHA256 `718e7adb5accf155445c60dfb9426274ed6a232a5b4943d5a7577b25b03e85b1`, copied from the retained full `2990a75` runtime and verified with `cmp` |
| Test executable / `driver.dll` | `707ec9c6db1aaa4a5ae06a3687a669299b1cb5122ead414fdaaa833479981dc8` / `0aa14dc68ae4c60552f7ca90875ccf31be3e03d573d5b421d85b4aef485148fd` |

The three test-source SHA256 values are respectively
`fce8e00475d848322c3f2facdc9c735050f75088b7d064bb8ac36486e34eaaf3`,
`f6c980df543b3393ddb95f62277e3c61695d99d63fc8baae44790d60049e84dc`, and
`2904bcd7de6a89de137d10572971ce93cdb5b9da77e97d27a6a19c5871c66ffa`.
The test-only patch SHA256 is recorded in the local evidence directory listed
below. Focused target/test compilation completed with exit 0. A fresh full
`make -j8 all` was manually stopped after 7m31s while compiling unrelated
runtime modules; its exit 143 is incomplete evidence, not a build failure.
The experiment reused the retained full runtime module rather than treating
the interrupted build as a runtime build.

## Commands and result

Commands used the following values and the disposable build directory shown in
the local evidence path below:

```bash
RUN_DIR=/home/eric/repos/proton-build-vanguard/e05-20261010-NIl3Zd
SDK='registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64@sha256:97526b794ce1a9bed5f891084462260b3a02399569f7438a3a57b5a253001db9'
BUILD_USER="$(id -u):$(id -g)"

docker run --rm -v "$RUN_DIR/wine-src:/src" -v "$RUN_DIR/wine-obj:/build" -w /src --user "$BUILD_USER" -e HOME=/build/home -e XDG_CACHE_HOME=/build/cache "$SDK" bash -lc 'mkdir -p "$HOME" "$XDG_CACHE_HOME" && ./autogen.sh && cd /build && /src/configure --enable-win64'

docker run --rm -v "$RUN_DIR/wine-src:/src" -v "$RUN_DIR/wine-obj:/build" -w /build --user "$BUILD_USER" -e HOME=/build/home -e XDG_CACHE_HOME=/build/cache "$SDK" bash -lc 'make -j1 V=1 -C dlls/ntoskrnl.exe && make -j1 V=1 -C dlls/ntoskrnl.exe/tests'

docker run --rm -v "$RUN_DIR/wine-src:/src" -v "$RUN_DIR/wine-obj:/build" -w /build --user "$BUILD_USER" -e HOME=/build/home -e XDG_CACHE_HOME=/build/cache -e WINEPREFIX=/build/prefix-e05-strict-20261010T103549Z-98926 -e WINEARCH=win64 -e 'WINEDLLOVERRIDES=mscoree,mshtml=' "$SDK" bash -lc 'timeout --kill-after=15s 300s xvfb-run -a /src/tools/runtest -v -T /build -M ntoskrnl.exe -p /build/dlls/ntoskrnl.exe/tests/x86_64-windows/ntoskrnl.exe_test.exe ntoskrnl'
```

The strict run `e05-strict-20261010T103549Z-98926` completed before the 300s
timeout. The runner exited **21**: 34,185 tests, 169 todo, 21 failures, 0
skipped. The 8 new E05 assertions were todos. After removing only the leading
file/line prefix from failure diagnostics, this run and the retained prior
patched run had the same 37 lines / 25 unique messages, with no new, missing,
or count-mismatched diagnostics. The prior patched log is published at
[`2026-10-10-rundown-protection/patched.log`](2026-10-10-rundown-protection/patched.log),
SHA256 `0e9907ea8bd25032734f3fdff2888b2f8b831e93e2412e9a2bc1542f8ce334e7`.
This is not an unpatched-baseline or Windows comparison.

The successful kernel-stack and NULL-fault controls show that the access
routine and exception guard were reached. Both process lookups returned
success. Probes during all five attach/detach phases raised access violations;
Wine logged the existing attach/detach fixmes. The two children passed liveness
checks before and after the IOCTL and exited normally during teardown. No new
unexpected assertion, skip, timeout, or child-cleanup failure was observed.

Sanitized trace excerpt from the retained strict log:

```text
attachment common 0x18000000, target-only 0x18010000, valid 0/0x7e,
    fault 0xc0000005, lookups 0/0
attachment caller: common status 0xc0000005; target status 0xc0000005
attachment A: common status 0xc0000005; target status 0xc0000005
attachment nested B: common status 0xc0000005; target status 0xc0000005
attachment restored A: common status 0xc0000005; target status 0xc0000005
attachment restored caller: common status 0xc0000005; target status 0xc0000005
```

## Conclusion and next action

The tested Wine A1 implementation does not provide the required ordinary
pointer-access behavior for this fixture. This supports only that bounded
implementation finding. It does not establish a Vanguard runtime dependency,
rule out every user-space architecture, or close G2 for other designs.

Keep address-space-dependent memory exports gated. Before a larger prototype,
test collision-safe shared code/data/stack/control mappings between cooperative
targets. Then test resumption of the same logical continuation through nested
A/B attach and detach, preserving stack, registers, identity, fault recovery,
target lifetime and cleanup. A remote-memory copy or a callback returning a
copied value is not a substitute. See the current result and proposed A1b gate
in [ARCHITECTURE](../ARCHITECTURE.md#current-e05-result).

Native Windows behavior, i386 execution, alternative A1b feasibility, target
call-path relevance, platform acceptance, Vanguard entry, accepted session,
and gameplay remain unknown or untested.

## Retained local evidence

Raw logs and build materials remain outside the repository under
`/home/eric/repos/proton-build-vanguard/e05-20261010-NIl3Zd/evidence/` and are
not committed. The strict log SHA256 is
`3894e79b512e951834254d2d06a379e459054cbe016a186a1baecb7793798c35`;
the fixture patch SHA256 and per-file source-copy hashes are in
`e05-fixture.patch` (SHA256
`b6801bc51f34409ace3e07e68760b43c335cf7414b7310b3ac9de777fd4f15c3`) and
`source-copy-hashes.txt` there. These hashes identify
local bytes; they do not make the artifacts publicly retrievable.
