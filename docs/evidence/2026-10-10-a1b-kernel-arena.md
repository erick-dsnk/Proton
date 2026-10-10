# A1b process-local kernel allocation arena experiment

Date: 2026-10-10. Scope: x64 experimental kernel-allocation backing only.
This experiment does not implement process attachment or establish an executor
that aliases kernel state across processes.

## Result

With `WINE_SHARED_KERNEL_MEMORY=1` delivered to the service environment, the
x64 `ntoskrnl.exe` test fixture exercised a 64 MiB section-backed allocator in
the process hosting the driver. The fixture checked pool, IRP, device and
driver-object mappings; invalid allocation requests; zeroing and reuse;
alignment and page containment; executable versus NX allocation; bounded arena
exhaustion and recovery; and concurrent allocation/free activity. The
executable-pool control returned `0xdeadbeef`, and the protected execution
attempt on an NX allocation was caught and cleaned up. Native-map samples
confirmed that the allocator's mappings were backed by `memfd:wine-mapping`.

The same retained GCC baseline and candidate artifact produced:

| Run | Tests | Todos | Failures | Skipped | Exit |
|---|---:|---:|---:|---:|---:|
| `WINE_SHARED_KERNEL_MEMORY` unset | 34,593 | 169 | 21 | 1 | 21 |
| `WINE_SHARED_KERNEL_MEMORY=1` | 34,942 | 169 | 21 | 1 | 21 |

Both runs had the same 37 normalized failure lines and 25 unique diagnostics
as the retained baseline, with no candidate-only or baseline-only diagnostics.
The opt-in run added 349 checks. Its one skip is the existing GCC limitation
for the compiler-generated `__try`/`__finally` fixture. The unchanged E05
attachment test still has eight `todo_wine` expectations. This is generic
x64 Wine evidence; native Windows and i386 comparisons remain pending.

The host observation sampled five processes. Each had section-backed mappings
at the same guest addresses, but the memfd inode numbers differed between
processes. The capture did not record process ancestry or cross-process
read/write results. It therefore confirms real backing for each sampled
process and does **not** establish that one process can see another process's
kernel allocations.

An earlier arena run reported 186 failures. It did not exercise the enabled
allocator: the opt-in setting was present in the Unix process but absent from
the Windows service environment. The rebuilt `services.exe` now preserves
`WINE_SHARED_KERNEL_MEMORY` when constructing the driver host environment.
Treat the earlier 186-failure result as a harness/environment failure, not as
an allocator result.

## Inputs and artifacts

| Input | Value |
|---|---|
| Proton revision | `c3547256adf6801cb45299690ea96ce208be097c` |
| Wine revision | `2990a75de24c57ab0a8ff2dc3caab7d075d4df40` |
| SDK | `registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64@sha256:97526b794ce1a9bed5f891084462260b3a02399569f7438a3a57b5a253001db9` |
| Architecture/configuration | x86_64, `--enable-win64` |
| Build scope | Targeted `ntoskrnl.exe`, `services.exe`, driver resources and test PE from a copied-cache Wine tree; retained ntdll, wineserver and launcher; no complete Wine or Proton build |
| Build log / SHA-256 | `/home/eric/repos/proton-build-vanguard/a1b-kernel-arena-20261010T135429Z/wine-obj/arena-reviewed-build.log` / `13f0a17536498ea728335d92b1398dac78a45195c631ec40719b3c7419d8f9f8` |
| Manifest / SHA-256 | `/home/eric/repos/proton-build-vanguard/a1b-kernel-arena-20261010T135429Z/arena-runtime-evidence.json` / `1118ab2a78c2f21a08ab7a050de8b570d9df411e0d574badcdb290fac152e92c` |
| Exact command record / SHA-256 | `/home/eric/repos/proton-build-vanguard/a1b-kernel-arena-20261010T135429Z/arena-executed-commands-20261010.json` / `3fa88db351e8b72fc2aa36efa93b40c2bc6e1695b16162a60d021afc7e8ddb8b` |

The candidate source SHA-256 values were:

| File | SHA-256 |
|---|---|
| `dlls/ntoskrnl.exe/kernel_memory.c` | `bc5f890efb12a24a659c9fbc34ed80394612816d04e90d33909deee973a44e54` |
| `dlls/ntoskrnl.exe/ntoskrnl.c` | `33bd30c8ad040d6b308914b9398a401c8042169650852ef41b7fa9d69aa20103` |
| `dlls/ntoskrnl.exe/ntoskrnl_private.h` | `84e9d98225cbbcf4bce17a29480347b71b8361672e87c37d84a0c584304a76de` |
| `dlls/ntoskrnl.exe/Makefile.in` | `0a077518c4916406c82b90c98d91ca4ed519b27d8ff29abadbe515d95fd6b8bb` |
| `programs/services/services.c` | `373d18f3605809ebc29639e2535c861226a37303550c35bc52fa8c2f9a61e999` |
| `dlls/ntoskrnl.exe/tests/driver.c` | `60a4094e2d85bf8de7b62c503b094879c4ebfe2a783e08510c899dc46cb27903` |
| `dlls/ntoskrnl.exe/tests/driver.h` | `761b2c0c14931f76469711d91790cca4fd001e5ec9f1e59b0acfe29e9e0307e2` |
| `dlls/ntoskrnl.exe/tests/ntoskrnl.c` | `970383f9a2238364d6e2151c87a9842da69ced3c5606d964a4a681338fd3e114` |

The compiled `ntoskrnl.exe` SHA-256 is
`77e317a7ac03f5b63503f8ed7f11a699ec424971a11446399e8ebf40d58f134b`;
`services.exe` is
`dd6a49d83e7f90fcc48a7606936c42df39e9f6aa71e5cb67829d3e8e3dd529e7`; the
test PE is
`8c95db77482173be91a351c366adb5126d2c836a8af0b786ee819a1edc7f4fd3`.
The retained runtime artifacts were ntdll
`b56593ef0933fec8cfd19c8c46a54a389b829db7186202c783f5968b8cfdbb65`,
wineserver
`34786b32962cf532767edd91835e21893a8d50cb4e7b43b9ef794a554f26bf5e`, and
launcher `f4882de048f35d8bcba4de36ac857bf99ae24554013227037e672d76a9e1728f`.

Runtime logs and their recorded hashes:

| Run | Local artifact | SHA-256 | Exit |
|---|---|---|---:|
| Baseline | `/home/eric/repos/proton-build-vanguard/a1b-finally-gcc-20261010T124212Z/final-source-strict.log` | `3557d41f8992ef9b140a3daab2e57f3ff5a9251e7d996f78d0a525eb741b6504` | 21 |
| Opt-in unset | `/home/eric/repos/proton-build-vanguard/a1b-kernel-arena-20261010T135429Z/wine-obj/arena-reviewed-off.log` | `fa89142f488a248df97185aac40a30cd0e537b64782ce84cd1e174a2fb64afd2` | 21 |
| Opt-in enabled | `/home/eric/repos/proton-build-vanguard/a1b-kernel-arena-20261010T135429Z/wine-obj/arena-reviewed-on.log` | `ea60f92ef84285c7707d925989a10504ed7988fd6ccfe0d3cb83ecf01a47d8a9` | 21 |
| Debug rerun | `/home/eric/repos/proton-build-vanguard/a1b-kernel-arena-20261010T135429Z/wine-obj/arena-reviewed-on-debug.log` | `993bae5f0a36b982847c0dcef2a5dd1057f95ff9c4efaec8fa10febe6c449d6e` | 21, incomplete log |

The exact quiet-mode run used a separate Wine prefix per mode and this command
inside the pinned SDK container:

```sh
for mode in off on; do
  export WINEPREFIX="/build/prefix-arena-reviewed-quiet-$mode-20261010T1440Z"
  if test "$mode" = on; then export WINE_SHARED_KERNEL_MEMORY=1; else unset WINE_SHARED_KERNEL_MEMORY; fi
  unset WINE_SHARED_PRIVATE_BACKING
  timeout --kill-after=15s 300s xvfb-run -a /src/tools/runtest -v -T /build -M ntoskrnl.exe -p /build/dlls/ntoskrnl.exe/tests/x86_64-windows/ntoskrnl.exe_test.exe ntoskrnl > "/build/arena-reviewed-$mode.log" 2>&1
  result=$?
  printf "%s\n" "$result" > "/build/arena-reviewed-$mode.exit"
done
```

The outer command mounted the recorded copied source and object directories,
used the pinned SDK, and set `HOME=/build/home`, `XDG_CACHE_HOME=/build/cache`,
`WINEARCH=win64`, `WINEDLLOVERRIDES=mscoree,mshtml=` and `WINEDEBUG=-all`.
The exact Docker argv and build/diagnostic commands are retained in the local
command metadata file above. The debug rerun has a normal summary at line
244318 (34,942 / 169 / 21 / 1) but interleaved trace output, so the quiet runs
remain the basis for normalized diagnostic comparison. The host observation file
is `/home/eric/repos/proton-build-vanguard/a1b-kernel-arena-20261010T135429Z/wine-obj/arena-reviewed-on-host-observation.jsonl`, SHA-256
`b426f02d9028f358bd8d8e4d1f5ae1b8c0f1ecce469dafdeea73cd3a555f0989`.

## Remaining boundary

The experiment gives the kernel allocator a section-backed mapping and
validates its local allocator behavior. The section handle, arena base and
initialization state remain owned by one `ntoskrnl.exe` process. It does not
publish the arena through wineserver, duplicate or lease views into an
executor, alias target-private mappings, or switch address spaces. It is a
prerequisite experiment only. The public `KeStackAttachProcess` and
`KeUnstackDetachProcess` behavior remains unchanged, and E05 remains open.
