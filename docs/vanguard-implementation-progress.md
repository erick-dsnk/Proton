# Vanguard Linux implementation progress

This file tracks implementation evidence after the feasibility study in
[`vanguard-linux-feasibility.md`](vanguard-linux-feasibility.md). It is a
working register, not a claim of Vanguard or League compatibility.

## First steps

1. **Freeze G0 inputs.** Keep the feasibility baseline pinned to Proton
   `bc896217ffcd67f892f952b010f898fe7bd0f0a1` and Wine
   `e60892cc2398b0a83c332a2078c7b85e47bdb42b`; retain the vendor hashes, host
   facts and SDK digest from the feasibility document. Select a Vanguard mode
   and obtain ordinary Windows reference evidence before interpreting runtime
   results. These last two pieces are still unavailable.
2. **Keep G1 explicit.** Record the selected mode's actual platform checks and
   returned restrictions. A Windows reference can establish normal Windows
   behavior; it cannot establish Linux acceptance. Genuine Linux verifier
   acceptance remains unresolved and is a dependency of any Vanguard session
   claim.
3. **Establish E02 with a generic driver.** Build this checkout's x64
   `ntoskrnl.exe`, the existing NT kernel test executable and its five driver
   fixtures in an isolated build directory. Compare failures with an ordinary
   Windows reference when available. Existing Wine `todo_wine` cases and
   attachment skips are recorded as gaps, not passes.
4. **Start E03 with ordinary rundown.** Implement acquire/release/wait
   semantics and test admission, in-flight references, waiting, rejection
   after rundown begins, and object release. Keep the first code increment
   narrow while the API contract is understood.
5. **Run E05's address-space falsifier before broad memory exports.** A benign
   driver must attach to another process and dereference a target-only mapping.
   Repeat with two processes mapping different bytes at the same virtual
   address; the implementation must observe each process's own bytes. Until
   that architecture is coherent, defer MDL/data-export expansion that
   depends on it. This is an architecture test, not a target-specific claim.

The implementation checkpoint now reaches E02 build and runtime evidence for
the first E03 x64 patch. A native Windows reference, i386 build,
process-attachment acceptance, genuine Linux verifier acceptance, and
Vanguard execution remain unresolved.

## Frozen build inputs

| Input | Value |
|---|---|
| Proton checkout | `/home/eric/repos/proton`, branch `research/vanguard-kernel-feasibility` |
| Proton SHA | `bc896217ffcd67f892f952b010f898fe7bd0f0a1` |
| Wine gitlink / checkout SHA | `e60892cc2398b0a83c332a2078c7b85e47bdb42b` |
| SDK image | `registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64:4.0.20260331.220802-0` |
| SDK manifest digest | `sha256:97526b794ce1a9bed5f891084462260b3a02399569f7438a3a57b5a253001db9` |
| SDK image ID | `sha256:97526b794ce1a9bed5f891084462260b3a02399569f7438a3a57b5a253001db9` |
| Isolated build directory | `/home/eric/repos/proton-build-vanguard/wine-obj` |
| Isolated source copy | `/home/eric/repos/proton-build-vanguard/wine-src` |
| Configuration | Wine `--enable-win64`, SDK container, x86_64 only |
| SDK toolchain | GCC 14.2.0; x86_64-w64-mingw32 GCC 14-win32; GNU make 4.4.1; GNU ld 2.44; Autoconf 2.72 |

The initial source copy excludes `.git` and is then updated with the changed
implementation/test files. Immediately before compilation, SHA256 values in
the checkout matched the copied versions:

| File | SHA256 |
|---|---|
| `wine/dlls/ntoskrnl.exe/ntoskrnl.exe.spec` | `01cc7d29995ce8eaacc18b5d65e3a6db9d27878fd2049eb4250e7e6f3dfab2a4` |
| `wine/dlls/ntoskrnl.exe/sync.c` | `93365168f4fdb52cea59270c1dd1c2591e737f2466dd88b03563d91e8a650dc2` |
| `wine/dlls/ntoskrnl.exe/tests/driver.c` | `f573e57207538dd0ea9ca5fde19152e303ddb8b26d8fb4d73a9a85eca1e29bf4` |
| `wine/include/ddk/wdm.h` | `480b18ddb41a3ce8ecac0dbfad935cfcaba77fd67ff6e6188aca3f642710a15d` |

The `driver.c` hash above includes the review fixes for FASTCALL declarations,
post-rundown rejection, bounded worker completion, unload safety, and immediate
free after rundown wait. The source SHA is pinned by the table, so a later edit
requires copying and verifying the file again before treating these artifacts
as built from that later edit.

## Commands and results

The SDK was pulled and configured with:

```sh
mkdir -p /home/eric/repos/proton-build-vanguard
cd /home/eric/repos/proton-build-vanguard
/home/eric/repos/proton/configure.sh --container-engine=docker --build-name=vanguard-baseline
```

This only generated Proton's external Makefile; it did not run the broad Proton
build. To avoid Proton's `module64` prerequisite that synchronizes every Proton
component, a Wine-only source copy was prepared and configured directly in the
same SDK:

```sh
mkdir -p /home/eric/repos/proton-build-vanguard/wine-src
mkdir -p /home/eric/repos/proton-build-vanguard/wine-obj
rsync -a --delete --exclude=.git /home/eric/repos/proton/wine/ \
  /home/eric/repos/proton-build-vanguard/wine-src/
```

The source copy was mounted as `/src` and the object directory as `/build`.
The SDK was run as uid/gid 1000 with a writable `HOME` and `XDG_CACHE_HOME`;
without these, Wine's Vulkan generator attempted to create `//.cache` and
failed. After autogen and before the module build, the four changed files were
copied from the working checkout and their hashes checked with:

```sh
cd /home/eric/repos/proton
for f in \
  dlls/ntoskrnl.exe/ntoskrnl.exe.spec \
  dlls/ntoskrnl.exe/sync.c \
  dlls/ntoskrnl.exe/tests/driver.c \
  include/ddk/wdm.h; do
  cp "wine/$f" "/home/eric/repos/proton-build-vanguard/wine-src/$f"
done
sha256sum \
  wine/dlls/ntoskrnl.exe/ntoskrnl.exe.spec \
  /home/eric/repos/proton-build-vanguard/wine-src/dlls/ntoskrnl.exe/ntoskrnl.exe.spec \
  wine/dlls/ntoskrnl.exe/sync.c \
  /home/eric/repos/proton-build-vanguard/wine-src/dlls/ntoskrnl.exe/sync.c \
  wine/dlls/ntoskrnl.exe/tests/driver.c \
  /home/eric/repos/proton-build-vanguard/wine-src/dlls/ntoskrnl.exe/tests/driver.c \
  wine/include/ddk/wdm.h \
  /home/eric/repos/proton-build-vanguard/wine-src/include/ddk/wdm.h
```

Configuration then succeeded with:

```sh
docker run --rm \
  -v /home/eric/repos/proton-build-vanguard/wine-src:/src \
  -v /home/eric/repos/proton-build-vanguard/wine-obj:/build \
  -w /src --user 1000:1000 \
  -e HOME=/tmp/vanguard-home -e XDG_CACHE_HOME=/tmp/vanguard-cache \
  registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64:4.0.20260331.220802-0 \
  bash -lc 'mkdir -p "$HOME" "$XDG_CACHE_HOME" && ./autogen.sh && \
    cd /build && /src/configure --enable-win64'
```

The patch and current generic fixtures compiled successfully with:

```sh
docker run --rm \
  -v /home/eric/repos/proton-build-vanguard/wine-src:/src \
  -v /home/eric/repos/proton-build-vanguard/wine-obj:/build \
  -w /build --user 1000:1000 \
  -e HOME=/tmp/vanguard-home -e XDG_CACHE_HOME=/tmp/vanguard-cache \
  registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64:4.0.20260331.220802-0 \
  bash -lc 'make -j1 V=1 -C dlls/ntoskrnl.exe && \
    make -j1 V=1 -C dlls/ntoskrnl.exe/tests'
```

Artifacts produced:

- `wine-obj/dlls/ntoskrnl.exe/x86_64-windows/ntoskrnl.exe`
- `wine-obj/dlls/ntoskrnl.exe/tests/x86_64-windows/ntoskrnl.exe_test.exe`
- `wine-obj/dlls/ntoskrnl.exe/tests/x86_64-windows/driver.dll`
- `wine-obj/dlls/ntoskrnl.exe/tests/x86_64-windows/driver2.dll`
- `wine-obj/dlls/ntoskrnl.exe/tests/x86_64-windows/driver3.dll`
- `wine-obj/dlls/ntoskrnl.exe/tests/x86_64-windows/driver_netio.dll`
- `wine-obj/dlls/ntoskrnl.exe/tests/x86_64-windows/driver_pnp.dll`

The built target DLL SHA256 is
`718e7adb5accf155445c60dfb9426274ed6a232a5b4943d5a7577b25b03e85b1`; the
test executable SHA256 is
`bd0fe7ecd565908fcf0573fdebf178e36a561bee80c0136d2867b909242c83c6`.
The x64 PE export directory was inspected with the SDK's
`x86_64-w64-mingw32-objdump -p`; all eight rundown exports are present:

| Export | PE ordinal |
|---|---:|
| `ExAcquireRundownProtection` | 4 |
| `ExAcquireRundownProtectionEx` | 5 |
| `ExInitializeRundownProtection` | 6 |
| `ExReInitializeRundownProtection` | 10 |
| `ExReleaseRundownProtection` | 14 |
| `ExReleaseRundownProtectionEx` | 15 |
| `ExRundownCompleted` | 16 |
| `ExWaitForRundownProtectionRelease` | 17 |

The first limited runner attempts exposed missing transitive Wineboot modules.
The isolated x64 Wine runtime was therefore built fully, without installing it
or building Proton. `make -j8 all` completed successfully (log SHA256
`2a8b21cd0acd57738910bef663d5014adf465be443f43af56a21c1f060d68519`):

```sh
docker run --rm \
  -v /home/eric/repos/proton-build-vanguard/wine-src:/src \
  -v /home/eric/repos/proton-build-vanguard/wine-obj:/build \
  -w /build --user 1000:1000 \
  -e HOME=/build/home -e XDG_CACHE_HOME=/build/cache \
  registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64:4.0.20260331.220802-0 \
  bash -lc 'make -j8 all'
```

The first fresh-prefix run then stalled in Wineboot because Wine's optional
Mono installer opened a modal `Wine Mono Installer` window under Xvfb. This
was an environment setup prompt, not a test hang. That attempt was stopped
deliberately and its log retained as
`wine-obj/ntoskrnl-test-final.log` (SHA256
`9a70c6c42b68998d694947bce3e644eaceb57d0d1cd5c016cc16ba9212a262ec`). Setting
`WINEDLLOVERRIDES=mscoree,mshtml=` suppresses that optional CLR/HTML setup; the
Wine test wrapper adds `ntoskrnl.exe=b` to the override list. This does not
disable any of the generic driver fixture imports.

The checkout-built test was then run directly with a fresh win64 prefix,
headless Xvfb, and a five-minute timeout:

```sh
docker run --rm \
  -v /home/eric/repos/proton-build-vanguard/wine-src:/src \
  -v /home/eric/repos/proton-build-vanguard/wine-obj:/build \
  -w /build --user 1000:1000 \
  -e HOME=/build/home -e XDG_CACHE_HOME=/build/cache \
  -e WINEPREFIX=/build/vanguard-test-prefix-no-mono \
  -e WINEARCH=win64 -e 'WINEDLLOVERRIDES=mscoree,mshtml=' \
  registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64:4.0.20260331.220802-0 \
  bash -lc 'timeout --kill-after=15s 300s xvfb-run -a \
    /src/tools/runtest -v -T /build -M ntoskrnl.exe \
    -p /build/dlls/ntoskrnl.exe/tests/x86_64-windows/ntoskrnl.exe_test.exe \
    ntoskrnl'
```

The patched run completed with `34156 tests executed (161 marked as todo, 0 as
flaky, 21 failures), 0 skipped.` The eight rundown exports were available, and
the new rundown block emitted no assertion, worker timeout, or skip diagnostic.
It includes the zero-reference and held-reference waits, concurrent acquire
and rundown rejection, reinitialization, bulk references, and eight
immediate-free-after-wait lifetime rounds. The run log SHA256 is
`0e9907ea8bd25032734f3fdff2888b2f8b831e93e2412e9a2bc1542f8ce334e7`.

To separate the changed block from existing generic-driver behavior, a
baseline source and object tree was copied from the same configured checkout.
Only the four files listed in the source-hash table were restored from Wine
HEAD (`e60892cc2398b0a83c332a2078c7b85e47bdb42b`) in the baseline source; the
baseline `ntoskrnl.exe` and tests were cleaned and rebuilt with the same SDK.
A unique, clean baseline prefix then ran the same direct test command and
environment. Its summary was `26023 tests executed (161 marked as todo, 0 as
flaky, 21 failures), 0 skipped.` After stripping filename/line-number prefixes
from `Test failed:` diagnostics, both runs have the same 37 diagnostic lines
(25 unique messages): no patch-only or baseline-only failure. The patched run
executes 8,133 additional rundown assertions and worker/lifetime checks, with
no new failure or skip. The clean baseline test log SHA256 is
`b40167b0d2c6b36e54ec0c8896ec5d2a22fc3603b20a7f35a89f81d2b27e447c` and its
target build log SHA256 is
`e4f7c2c13d81f0c47d256d52e7994d5176413a6f1eacc4a5bf0de8420899748b`.

One preliminary baseline invocation was excluded: the object-tree copy
included the patched run's already initialized prefix, and that attempt
reported six crypto-provider failures without a suite summary. The valid
comparison above uses a different, previously nonexistent prefix.

No installed system Wine is used as evidence. The isolated object tree keeps
the compile, full-runtime, bootstrap, patched-run, and baseline-run logs under
`/home/eric/repos/proton-build-vanguard/`.

During compilation, WIDL/WRC reported five shift/reduce conflicts in the
existing `/src/tools/wrc/parser.y`; assembly emitted an indirect-jump warning,
and the existing `ntdll/unix/virtual.c` emitted a const-qualifier warning.
The changed `ntoskrnl.exe` source and test driver compiled without a diagnostic.

## Evidence still required

- Build and test on ordinary x64 Windows to provide the reference behavior.
- Validate x86/i386 calling conventions and data exports independently.
- Run the E05 same-virtual-address/different-bytes negative control before
  expanding address-space-dependent exports.
- Select the Vanguard mode and obtain actual platform restrictions and verifier
  behavior. Linux acceptance remains unproven.
- Compare the ordinary Windows reference and selected mode's restrictions
  before using the Wine generic-driver run to make target-specific claims.
- Keep code signing, firmware state, accepted Vanguard session, League gameplay,
  and production deployment as separate claims requiring separate evidence.
