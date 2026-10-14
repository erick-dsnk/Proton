# 2026-10-13 — first full Proton build and unmodified vgk.sys driver entry

Status: completed. Claim label: Observed, except where a line says otherwise.

This record has two results from one host and one build.

1. This is the first recorded full Proton build of this fork. The x86_64 Wine
   tree built clean under `--enable-werror`. The i386 tree needed 12 local
   type fixes in `dlls/ntdll/unix/virtual.c`, plus the preloader guard fix.
2. This is the first observed entry of the unmodified Vanguard 1.19.1.18
   kernel driver in a full Proton session, with all fork options off.
   `vgk.sys` was mapped and relocated, and its entry point ran. In the same
   millisecond as the relocation, `DriverEntry` returned the non-standard
   status `0xD4494E49`. Nothing in the image called an unimplemented import
   first.

The run used a host that is new to this project, a Linux desktop with Secure
Boot enabled. There is no Windows reference run (G0/E00).

## Question and scope

- **Question.** Does the integrated build run, and where does the unmodified
  `vgk.sys` first fail in a full Proton session with the fork's opt-in modes
  off? The pre-run plan, kept in local notes outside the repository,
  predicted that a call to a missing import (K01–K06) would raise
  `EXCEPTION_WINE_STUB`.
- **Related gates.** G2 (execution architecture) and outcome stages 1 and 3
  in [TESTING.md](../../TESTING.md#record-distinct-outcomes).
- **Negative control.** None was run. No Proton Experimental control run
  exists for this account and prefix.
- **Limits.**
  - Stage 2, the generic conformance suite, was not run for this build.
  - Stages 4 and 5 were not reached.
  - A Riot Client login and a rendered client window do not establish any
    later stage.

## Inputs

| Input | Exact value |
|---|---|
| Proton SHA | `3c6f9578a31dd8763bf58b782a4ee889a32cdc28`, working tree clean apart from the `wine` gitlink |
| Wine SHA | `ddf378e30bd26570821751b10b201ec546b5df18`, plus the working diff [`wine-i386-build-fixes.diff`](wine-i386-build-fixes.diff) (sha256 `f1318d90…e7d9d`, 2 files, +19/−15). The diff is identical to `git diff ddf378e30bd baed3097392` on [zergberg/wine `fix/i386-werror-build`](https://github.com/zergberg/wine/tree/fix/i386-werror-build): commits `a50c3070d1eb2bcdf8b55d0b88ac52b79b6e4ae6` (loader) and `baed30973924a54f368ef28b4c65f259cb7e70e6` (ntdll), proposed to erick-dsnk/wine. The Proton `wine` gitlink is unchanged until that lands. |
| Other gitlinks | unchanged from Proton `3c6f9578` (`git submodule status`, 23 entries) |
| SDK | `registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64@sha256:97526b794ce1a9bed5f891084462260b3a02399569f7438a3a57b5a253001db9`: gcc 14.2.0-19 (Debian), ninja 1.13.1, meson 1.7.0 |
| Build configuration | `configure.sh --enable-ccache --container-engine=docker --build-name=proton-vanguard-experimental --docker-opts='--cpuset-cpus 0-7 --memory 18g --memory-swap 18g'`; `make J=8`. Wine always gets `--enable-werror --with-mingw=gcc --disable-tests` (`Makefile.in:614-617`). |
| Installed tool | `compatibilitytools.d/proton-vanguard-experimental`, version `1791952896 proton-11.0-2e-12-g3c6f9578`. Key binary sha256 values are listed under Commands and artifacts. |
| Host | Ubuntu 24.04.5 LTS, kernel `7.0.0-38-generic`, x86_64, AMD Ryzen 7 3800X, NVIDIA RTX 5090 with driver 595.91.07, UEFI with **Secure Boot enabled** (shim → signed GRUB → signed kernel), kernel lockdown `integrity`, firmware TPM 2.0 present |
| Runtime | Steam Linux Runtime 4.0 (`depot 4.0.20260928.262390`), pressure-vessel `0.20260925.0` |
| Prefix | Fresh, created by this tool on first launch through a non-Steam shortcut. All `WINE_*` fork options were unset. |
| Vendor | Installer sha256 `cc897ef385ff3ae1481106c251a86ac7382f2b736053e9e577aada327cabeb54` (75,831,040 bytes). Vanguard 1.19.1.18. `vgk.sys` sha256 `8ba32cfbc4a07fd41a082344e23e312515ffafef0e568ba72e7d33e83b558f13` and `vgc.exe` sha256 `c8f330a77351f36e1112d0b94972a735a7747fc33a4aa4735d95f43f01637c51` are **identical** to the [frozen audit](../../vanguard-linux-feasibility.md). League client `16.20.8248524`. |
| Account | A dedicated test account. Its identifiers are not recorded. |
| Windows reference | None, which is the G0/E00 gap |

## Commands and artifacts

### Build

`$SRC` is the Proton checkout. `$BUILD` is an out-of-tree build directory.
`CCACHE_DIR` was set for every make invocation.

| Step | Command | Exit | Wall time | Notes |
|---|---|---:|---:|---|
| 1 | `$SRC/configure.sh …` (see Inputs) | 0 | <1 s | |
| 2 | `make J=8 wine-i386` | 2 | 693 s | Excluded attempt. `virtual.c`: 14 `-Werror` diagnostics in i386-unix code (int-to-pointer casts of 64-bit `executor_layout` fields, 48-bit `WINE_MANAGED_*` constants overflowing 32-bit `ULONG_PTR`/`SIZE_T`, `%lx` used with `size_t`, and a `size_t*` passed as `SIZE_T*`) |
| 3 | `make -k J=8 wine-i386` | 2 | 487 s | Error survey only. Same 14 diagnostics, no other source file failed. The ~99 `.res` failures (`unable to load locale.nls`) come from build order, see the note below the table. The status file recorded `rc=0` because of a script bug. The real exit code was 2. |
| 4 | `make J=8 wine-x86_64` | 0 | 527 s | Clean under `-Werror` |
| 5 | `make J=8 wine-i386` | 2 | 3 s | Excluded attempt, fixes not yet applied |
| 6 | Apply the fixes, then `make J=8 wine-x86_64` | 0 | 12 s | The patched `virtual.c` was recompiled and `ntdll.so` relinked |
| 7 | `make J=8 wine-i386` | 0 | 28 s | The patched `virtual.c` was recompiled and `ntdll.so` relinked |
| 8 | `make J=8 install` | 0 | 861 s | Installed to `~/.steam/root/compatibilitytools.d/proton-vanguard-experimental` |

**Build-order constraint.** The `.res` failures in step 3 come from build
order, not from the fork.
- `wine-i386` runs the x86_64 tree's `tools/wrc/wrc`.
- That `wrc` resolves its NLS directory relative to its own binary, as
  `obj-wine-x86_64/nls/locale.nls` (`tools/tools.h` `get_nlsdir`).
- Only the x86_64 Wine build creates that symlink.
- So run `wine-x86_64` before `wine-i386`.

**The i386 fixes** are in [`wine-i386-build-fixes.diff`](wine-i386-build-fixes.diff).
- All of the affected code is unreachable on i386. The managed layout is
  admitted only under `#if defined(__linux__) && defined(__x86_64__) &&
  defined(_WIN64)`, in `virtual_init`.
- The fixes are casts through `ULONG_PTR`, `(SIZE_T)` casts of constants,
  one scoped `#pragma GCC diagnostic ignored "-Wtype-limits"`, and
  `SIZE_T returned`.
- On x86_64 every change is an identity. A sandboxed compile of a
  line-number-preserving variant of the patched file produced an object
  byte-identical to the unpatched one.
- Two independent review passes confirmed each fix. The real builds in steps
  6–8 then confirmed them as well.

**Installed key binaries** (sha256):

| Binary | sha256 |
|---|---|
| `files/lib/wine/x86_64-unix/ntdll.so` | `b4f57983f6f42d4502a83407cf9cff340cb520182f67908b86c446dfe70437c7` |
| `files/lib/wine/i386-unix/ntdll.so` | `6164aec5aa978dae857406bd3e7fb7bd5c0942442c8ec51e8e444da93a6e1d85` |
| `files/lib/wine/x86_64-windows/ntoskrnl.exe` | `075593d492453efe131bea0b5f73f0fcaea57eacd4c9bb55623803d07a508214` |
| `files/lib/wine/i386-windows/ntoskrnl.exe` | `349707d5f7d88b6c7f5f316e3766f7511f6fd1b862b5f622b2df6d313f5cebaf` |

These builds include the fork's rundown exports in both `ntoskrnl.exe`
variants, and the fork's managed-admission strings in `ntdll.so`.

### Run

1. Add the installer to Steam as a non-Steam game. Force the compatibility
   tool to `proton-vanguard-experimental` **before** the first launch.
   `compat_log` shows `Mapping AppID … to tool "proton-vanguard-experimental"`.
2. Set the launch options:
   `PROTON_LOG=warn+module,+service,+ntoskrnl,+plugplay,+tbs,+int PROTON_LOG_DIR=$HOME/vanguard-logs/lol %command%`.
   Proton also adds its default `+timestamp,+pid,+tid,+seh,+unwind,+loaddll`
   and related channels.
3. Install to the default `C:\Riot Games`. The installer pulled League and
   Teamfight Tactics, and installed Vanguard as part of that.
4. Start Vanguard. No restart was requested, and the prefix was not
   restarted. In the Riot Client, press **Play** for League.
5. Close the client and capture with a read-only script.

### Artifacts

| Artifact | Where | sha256 |
|---|---|---|
| [`vgk-driver-entry-excerpt.log`](vgk-driver-entry-excerpt.log). 155 lines, unfiltered: the `StartServiceW` request, every line of the `vgk` driver-host process (pid `0b1c`) from start to exit, including exception register dumps and the 28 `MajorFunction` lines, and the service-manager lines for that start. Contains no account data. | committed | `7abed53487e7004045c07c40cbfd83390d9b5cbe40fb01cff4258a056d276fb4` |
| [`wine-i386-build-fixes.diff`](wine-i386-build-fixes.diff) | committed | `f1318d907f706b4e248efad5f2913ea31d5fda3fc50ecf898fc348edb0ca7e9d` |
| Full Proton log `steam-<SteamGameId>.log` (293,783,634 bytes, 3,244,152 lines by `wc -l`) | retained locally, because it contains account data | `6f60bd41420aa8d35a648acbba10d799fb5f6fecd66b890a64f2f5df279700db` |
| Steam `compat_log.txt` | retained locally | `bde83d9e0f619c8c83e72ebdf8ef876bfe16fa0eecf647f4ea5aad9d0cd3f1c8` |
| Service registry export (`vg-services.txt`) | retained locally | `d066564e46696e07976a3407c4746b5e8ec257cdd6cc8538e71be3eca64face0` |
| Riot Client and League client logs | retained locally, because they contain account identifiers and tokens | not published |

Contributors can't reproduce the run from local paths. The committed excerpt
is the public evidence for the driver-entry claim.

The capture ran while `RiotClientServices.exe` was still idle in the prefix,
so the capture script wrote a warning file. The driver-host process had
exited earlier (`process_monitor_thread_proc pid 0b1c exited`), so its window
is complete. Only the tail of the full log may be incomplete.

## Results

### Outcome stages

| Stage | Result |
|---|---|
| 1. Source/build identity | **Observed.** Build steps 6–8 exited 0. The tool is installed and registered by Steam on SLR 4. |
| 2. Generic conformance | Not run for this build (Unknown) |
| 3. Unmodified driver entry | **Observed failure.** `DriverEntry` returned `0xD4494E49`. Service and device readiness were not reached. |
| 4. Accepted session | Not reached |
| 5. Gameplay | Not reached |

### Sequence (Observed, in the committed excerpt and local logs)

1. The Riot Client logged two things about Vanguard:
   - `Vanguard phase transition: Install -> Succeeded`.
   - `Per-product vanguard check for league_of_legends: restartRequired=false, restartWaivedReason=NEW_INSTALL`.
     The same check returned `restartRequired=true` for `valorant` and
     `lion`.
   - So no restart prompt appeared for League.
2. Installed services:
   - `vgk` is `Type=1` (kernel driver), `Start=1` (system), with ImagePath
     `C:\Program Files\Riot Vanguard\vgk.sys`.
   - `vgc` is `Type=0x10`, `Start=3`.
   - The installer created both services without starting `vgk`.
3. On **Play**, the client called `StartServiceW` on `vgk`.
   - `services.exe` started a new `winedevice.exe` (group `Winedevice3`).
   - The call chain was `ZwLoadDriver` → `IoCreateDriver(\Driver\vgk)` →
     `load_driver`.
4. Wine's loader bound `cng.sys`, `bcrypt.dll` and `HAL.dll` as builtins.
   It reported **14 unimplemented imports**, each bound to a stub thunk in
   `0xD20000–0xD201D4`:
   - `KeAcquireGuardedMutex`, `KeReleaseGuardedMutex`
   - `ExInitializePushLock`, `ExAcquirePushLockExclusiveEx`,
     `ExReleasePushLockExclusiveEx`
   - `KeGetCurrentIrql`, `KeIpiGenericCall`, `KeQuerySystemTimePrecise`
   - `ExAllocateCacheAwareRundownProtection`,
     `ExFreeCacheAwareRundownProtection`,
     `ExAcquireRundownProtectionCacheAwareEx`,
     `ExReleaseRundownProtectionCacheAwareEx`,
     `ExWaitForRundownProtectionReleaseCacheAware`
   - `IoInitializeWorkItem`

   These are the K01–K06 families from the audit. K09–K12 (rundown
   protection) resolved.
5. `vgk.sys` was loaded as native at `0x0000000100300000`, relocated from its
   preferred `0x140000000–0x1467F2000`. Its imports resolve to builtin
   modules at user-space addresses such as `0x00006FFFF…`.
6. Between the relocation and the return of `init_driver`, two reads of the
   `KUSER_SHARED_DATA` kernel alias faulted. `ntoskrnl.exe/instr.c` emulated
   both and execution continued.
   - These reads came from `DriverEntry` or from a TLS callback. Wine runs a
     TLS callback inside the image load, before `DriverInit`, and logs it
     only under `+relay`, which was off.
   - `USD offset 0x320` (`TickCount`), at image offset `0x64810A4`. The
     emulated value was Wine's live tick count, `0x467E87` ms, which matches
     the log clock.
   - `USD offset 0x4` (`TickCountMultiplier`), at image offset `0x64817F7`.
   - Both exception dumps show `cs=0033 ss=002b`. The code ran at CPL 3 on
     the driver-host's service-dispatcher thread.
7. No `EXCEPTION_WINE_STUB` was raised. **No unimplemented import was
   called.**
   - No privileged-instruction exception was logged, so no control-register,
     MSR or port instruction executed in this window.
   - No `SIGSYS` occurred on the thread, so there were no direct system calls.
   - No other traced `ntoskrnl` activity appears between the load and the
     return.
   - Several imports are invisible to these channels: `Zw*` aliases
     implemented in ntdll, Rtl/CRT routines, untraced ntoskrnl functions,
     data imports, and unprivileged instructions such as `cpuid` and
     `rdtsc`. Their use is Unknown.
8. `DriverEntry` (`DriverInit = 0x1064C213C`, image offset `0x61C213C`)
   returned **`0xD4494E49`**.
   - It left `DriverStartIo`, `DriverUnload` and all 28 `MajorFunction`
     entries at Wine's `IoCreateDriver` default. No dispatch routine was
     installed.
   - Wine logged `err:ntoskrnl:ZwLoadDriver failed to create driver …vgk: d4494e49`,
     deleted the driver object and stopped the service group.
   - `services.exe` returned 317 (`ERROR_MR_MID_NOT_FOUND`) for the start
     request. Winedevice reports `RtlNtStatusToDosError(ZwLoadDriver())`
     (`programs/winedevice/device.c`). For a status missing from its table,
     that function returns 317 (`dlls/ntdll/error.c`).
   - `0xD4494E49` is not a conforming NTSTATUS. It sets the reserved N bit,
     its facility is `0x449`, and Wine's headers don't define it.
   - Timing: the image load began at 4619.820 and the image was mapped at
     4619.909. The relocation and the return both fall in the 4619.911 log
     millisecond.
9. `vgc` then started.
   - It opened the `vgk` *service* with query access (`0x5`) and read its
     configuration.
   - About 31 ms later it stopped itself with `SetServiceStatus`: state
     STOPPED, controls `0x105`, Win32 exit 1.
   - The service-specific field was `0xCE`. The service manager ignores that
     field unless the Win32 exit code is `ERROR_SERVICE_SPECIFIC_ERROR`.
10. The Riot Client launched the League client regardless.
    - `LeagueClientUx` then failed to connect to its local backend
      (`UX connect to Foundation failed {attempts: 2228}`, SSL connect reset).
      It exited and left a blank window.
    - This failure is separate from Vanguard and is not analysed here
      (Unknown).

The pre-run plan's top prediction, a fatal unimplemented-import call,
**did not hold**. The `KUSER_SHARED_DATA` emulation gap that WineHQ bug 48988
describes for `cmp` instructions was also not hit. These two accesses were
emulated.

### Wine emulation divergence found in this run (Observed)

The emulated 32-bit read at offset `0x4` changed `r9` from
`814b3907474eb601` to `814b390701000000`. The low half got the value, and
the upper half was left unchanged.
- An x86-64 CPU writing a 32-bit destination register zero-extends it. On
  hardware the result would be `0000000001000000`.
- The cause is `store_reg_word()` in `dlls/ntoskrnl.exe/instr.c`. For a 4-byte
  operand it copies 4 bytes into the 8-byte register slot. Its OR and XOR
  paths, and the other callers that use 32-bit destinations, behave the same
  way.
- This is a generic Wine emulation bug, independent of Vanguard. Whether it
  contributed to this failure is Unknown.

### Third-party report (Documented, not independently verified)

[nicolasdesenv/valorant-linux-compatibility](https://github.com/nicolasdesenv/valorant-linux-compatibility)
(`docs/compatibility-matrix.md`, accessed 2026-10-13) reports the same
sequence for VALORANT on Fedora 44 with kernel 7.1.8 and a different Proton
build: both shared-data faults (`+0x320`, `+0x004`), `d4494e49`, then 317.
That repository publishes no raw logs and records no Vanguard build.

## Conclusion and next action

**Established**
- The fork builds and installs as a Steam compatibility tool on this host,
  given the i386 type fixes and the build-order constraint.
- Under the default (non-managed) driver-hosting model, the unmodified
  `vgk.sys` reaches `DriverEntry` in a full Proton session.
- `DriverEntry` rejects the environment early, with a vendor-specific status,
  before it uses any K01–K06 import.
- Implementing those imports alone therefore can't advance stage 3 from this
  state. This is consistent with G2 being the first gate.

**Not established**
- Why `DriverEntry` returns `0xD4494E49`. This record makes no claim about
  Vanguard's internal checks. The project does not reverse-engineer or patch
  Riot code.
- Whether the result is deterministic across launches. The next prefix start
  should auto-start `vgk` (`Start=1`), and that is not yet observed.
- Whether any of the fork's opt-in modes change this result.
- What a Windows reference does.

**Fork options.** None of the fork's opt-in modes changes the CPL, the
kernel-alias emulation path, the stub data exports, or the thread that runs
`DriverInit`. The managed layout also refuses the 32-bit children the
installer launched (DirectX setup and the Vanguard setup). So no mode
justifies another vendor run yet. `WINE_EXPERIMENTAL_DRIVER_CONCURRENCY=2`
would refuse this image before `DriverEntry`.

**Next**, all without Riot software:
1. Run a benign probe in the existing ntoskrnl test driver. It records the
   observables listed above under the default and managed modes, and
   reproduces the zero-extension divergence.
2. Fix 32-bit destination zero-extension in `instr.c`, upstreamable to
   WineHQ.
3. Make the `KeNumberProcessors`, `MmHighestUserAddress` and
   `SystemBasicInformation.KeMaximumIncrement` values truthful and
   consistent. Today they are stubbed or zero.

Any further vendor run waits until one of these produces a difference that
a fix or mode actually changes.

## References

- [Feasibility study](../../vanguard-linux-feasibility.md): frozen Vanguard
  1.19.1.18 hashes and the K01–K18 import audit.
- [Implementation register](../../vanguard-implementation-progress.md) and
  [ROADMAP](../../ROADMAP.md): gates G0–G5.
- [TESTING.md](../../TESTING.md): outcome stages.
- WineHQ bug 48988: `KUSER_SHARED_DATA` emulation of `cmp`.

