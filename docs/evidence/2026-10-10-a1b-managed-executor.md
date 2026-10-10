# A1b managed EXECUTOR layout

Date: 2026-10-10. Scope: an opt-in Linux AMD64 Wine process role that places
the host-side Windows runtime outside a managed TARGET address range. This is
a clean physical-process bootstrap prerequisite. It does not implement
cross-process attach, foreign memory aliases, a shared kernel arena, or
Vanguard compatibility.

## Source contract

The executor setting is
`WINE_MANAGED_LAYOUT=v2:executor:400000000000:410000000000`. It is a private
preloader-to-ntdll startup ABI, not a Windows interface or a general process
admission mechanism. Its 96-byte descriptor has a common version/role/guest
bounds prefix and an executor extension with `size`, `layout_id`, the host
range, the canonical ntdll range, and the two low-page exceptions. The
extension is read only after the common prefix identifies version 2 and the
EXECUTOR role; ntdll validates the exact size, layout ID and fixed bounds.
The existing version-1 TARGET descriptor remains unchanged.

The guest range is `[0x10000, 0x400000000000)`. The physical host runtime has
the disjoint range `[0x400000000000, 0x410000000000)`. Wine reserves the host
range with non-replacing semantics before loading ELF or PE images. The first
16 MiB of the host range is reserved for the real AMD64 ntdll image, which is
mapped at its canonical address; ordinary host allocations begin after that
slot. The real loader applies validated AMD64 relocations when the image's
preferred base differs. Unsupported image types or relocation forms fail
admission instead of claiming a successful boot.

Two declared mappings remain below the guest boundary. The Windows
`KUSER_SHARED_DATA` page at `[0x7ffe0000, 0x7ffe1000)` is read-only. A separate
private RW/NX Wine syscall-dispatcher page occupies
`[0x7ffe1000, 0x7ffe2000)`. Wine tracks both by internal mapping purpose so
ordinary allocation, protection, decommit, release and unmap operations
cannot discard or replace them. The dispatcher pointer is process-private;
the shared canonical ntdll address does not make its writable state shared.
These lifetime checks define the experimental mapping contract and do not
claim protection against arbitrary writes by code already running in the same
process.

The physical process remains its own Wine process throughout this bootstrap.
The descriptor and startup role persist through the real loader even if the
Unix and Windows environment variables are cleared before a child is created.
This does not yet give the process a logical attached-target identity, nor
does it make any target memory visible in the executor.

## Runtime evidence

The current **96-byte, layout-ID-2** sources were copied to the isolated build
tree and matched by SHA-256 before building. The pinned SDK was
`registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64@sha256:97526b794ce1a9bed5f891084462260b3a02399569f7438a3a57b5a253001db9`
(image ID matched). The Proton parent was `c3547256adf6801cb45299690ea96ce208be097c`
and Wine was `2990a75de24c57ab0a8ff2dc3caab7d075d4df40`. `config.status`
SHA-256 was `109eddd17d099f8aed74ab7dcb3ff4ff50c977f6e8ae9ce79e910bf336ff64f5`.
The build recompiled the loader/preloader and native `ntdll.so` with `-j1`
and rebuilt the two executor fixtures. Other compatible PE/runtime/test
artifacts came from the retained TARGET, backing and arena trees. This was not
a full current-tree Wine build or a Proton build.

The exact command argument vectors and environment, every retained run/result,
all source and artifact hashes, observer snapshots, failure chronology and
baseline comparison are in the frozen local manifest
`/home/eric/repos/proton-build-vanguard/a1b-managed-executor-20261010T/managed-executor-runtime-evidence.json`
(SHA-256 `0a1acaa4c6d50509fdf0ac6e9e766acb85315e35de68a5cacc73d6e474d8f910`,
mode `0444`). The tested dirty Wine source archive is
`executor-recovery-current-sources.tar.gz` (SHA-256
`f8fd6ca3ea4d4645821b2722173cd817791693bda19eb13735a4a431b688f469`); its
patch is `executor-recovery-current-wine.patch` (SHA-256
`f9245978748ff3a7d398ab99f04f98a97ca71c0ac694874b33b1ca0ae0269d43`). These
are local build-host records, not repository artifacts. The manifest lists
SHA-256 for every source and output and preserves the exact JSON command
records. The targeted build command was:

```sh
make -j1 V=1 -C loader && make -j1 V=1 dlls/ntdll/ntdll.so && \
  gcc -O2 -Wall -Wextra -fPIE -pie -I/src/include \
    -Wl,--export-dynamic -o /build/managed-executor \
    /src/loader/tests/managed-executor.c -pthread -ldl && \
  tools/winegcc/winegcc -o /build/managed-executor-pe.exe \
    --wine-objdir /build -b x86_64-w64-mingw32 -mconsole \
    -D_MSVCR_VER=0 -D__WINESRC__ -I/src/include -I/src/include/msvcrt \
    -I/build/include -Wl,--large-address-aware \
    /src/loader/tests/managed-executor-pe.c -lmsvcrt -lntdll -lkernel32
```

The build exited 0. The preloader admission matrix passed **16/16** malformed
setting, unsupported role, reservation-collision, ELF-format and descriptor
cases (exit 0). The native Linux fixture exited 0 with no failures. The real
PE fixture ran the Windows process as the actual parent and child: **209
parent checks and 201 child checks, zero failures**, runner exit 0. It checked
canonical ntdll and real dispatcher pointers, physical TEB/PEB/heap/image and
thread-stack placement, ordinary allocation and mapping rejection, a real
`MEM_IMAGE` view, exception-table search/cleanup and `RtlUnwindEx`, returned
through a native host syscall, and then used a healthy thread and syscall.
The denied-protection fixture was corrected to expect Wine's established
`PAGE_NOACCESS` failure output; it still checks that the protected dispatcher
pointer, mapping and later syscall remain valid. The separate managed TARGET
regression passed its **28 parent and 3 child checks**, exit 0. The default-off
`ntdll` virtual suite reported **2,340 tests / 104 todos / 0 failures / 0
skips**, exit 0.

The read-only `/proc` observer ran as uid 1000 in the test container against
two real Wine processes with Linux PIDs **124 and 126** and Wine PIDs **344 and
352**. Both ran the same real command and held independent byte values **65**
and **66** at the same ordinary private VA `0x400021000000`. It recorded four
complete snapshots (allocated and released in each process), including live
main/worker TEBs, native stack and syscall-frame bounds, guest coverage,
canonical ntdll `0x400000000000`, host bounds, and both declared low pages.
KUSER was `r--s`; the separately owned private syscall-dispatcher page was
`rw-p` and non-executable. The fixed dispatcher pointed into each process's
own relocated native `ntdll.so`; the first process alone ran the real
instrumentation-callback A → B → clear sequence. After `NtFreeVirtualMemory`,
the released allocation range was again inaccessible (`---p`). No target
process mapping was acquired or dereferenced by either executor. The observer
exited 0, and both fixture processes exited 0.

Four intermediate observer reads raised `AssertionError` with empty
diagnostics; their causes remain **unlocalized**. They are retained in the
manifest separately from the four complete snapshots and passing fixture
exits, and are not silently reclassified as passes. The earlier ABI-80/layout-
ID-1 strict observer failure on an undeclared RW dispatcher page is also
retained; it prompted the reviewed ABI-96/layout-ID-2 descriptor and explicit
dispatcher slot. Two first E05 retries exited 5 before printing a test summary
because the recovered prefixes lacked `system.reg` and the crypto-provider
setup failed. The records are preserved. Normal prefix update then exited 0;
the initialized E05 runs below produced complete summaries. A later
prefix-scoped server wait exited 0 for both prefixes, and no Wine process
remained in the private container PID namespace.

The generic E05 comparison used the real unchanged attachment fixture, with
the executor layout off for the baseline-style run and TARGET, backing and
arena enabled for the candidate run. Both used separate initialized prefixes
and the pinned SDK. The command inside each container was:

```sh
timeout --kill-after=15s 300s xvfb-run -a /src/tools/runtest -v -T /build \
  -M ntoskrnl.exe \
  -p /build/dlls/ntoskrnl.exe/tests/x86_64-windows/ntoskrnl.exe_test.exe \
  ntoskrnl
```

| E05 run | Results (tests / todos / failures / skipped) | Runner exit | Log SHA-256 |
|---|---:|---:|---|
| Managed layout and backing/arena options unset | 34,593 / 169 / 21 / 1 | 21 | `7deb4110455444e127c68be0bb6e893f6f64caa25e09a674fe14a958186b49dc` |
| TARGET + private backing + kernel arena enabled | 34,942 / 169 / 21 / 1 | 21 | `c5fef42ac8516c6c632c8e73e88067a4d21b7edf678750724bbdcfee7368269a` |

Each run had the same **ordered 37 failure payloads and 25 unique messages**
as the retained GCC baseline (SHA-256
`3557d41f8992ef9b140a3daab2e57f3ff5a9251e7d996f78d0a525eb741b6504`); the
counter comparison also had no baseline-only or candidate-only diagnostics.
Each run retains all **eight attachment todos**. The 21 suite failures and
existing GCC `__try`/`__finally` skip remain; matching baseline diagnostics
does not turn the suite into a pass.

The principal current-source hashes are `include/wine/managed_layout.h`
`66a07f9558ba6830c6ef7dd02e77723c2851351ef5111474d32d628b008df29d`,
`loader/preloader.c`
`6c5cfb468442c2c670d73c4f0019d056c8b669a5396b6b354a22dd6d67b442aa`,
`dlls/ntdll/unix/loader.c`
`432726ab3fca7e6f8c82aa685d4fae4393db36e5335c5e326799f3cdc0df37f9`,
`dlls/ntdll/unix/virtual.c`
`190c0a5acf147fe3e87a683572edf62f56f94fb3b1b6fd3e2aac454f62477f66`,
`dlls/ntdll/unix/signal_x86_64.c`
`edf6ff8a5343a10661016218697eaeccbc0b895ee15da466346f9272c71e7203`, the
native fixture `loader/tests/managed-executor.c`
`5b3c3ff1d86480896599095bf3c387730c3094a42bf728e54cbf52a24331c850`, and
the PE fixture `loader/tests/managed-executor-pe.c`
`234c66c309eb8e71519f0e17de851085b34bda855270622f367443f1515d6ef3`. The
manifest lists all remaining source hashes. The built `loader/wine` SHA-256
was `a058d5dba834a9bc61fd581e86587440e742512000051280e39dd22706d3d431`,
`loader/wine-preloader` was
`d596acd8d481c0e072f18b834adb960980ce09320da33246abc79a1079784e1f`, native
`ntdll.so` was
`9277e1c801420eb5e57fb6273e695129cd5ec494f65a12a0f02a7515cb72e0e0`, and
the PE fixture was
`4e6fb61d6d2f8c018ce6816af53d2be724b70387b9313ea790411b50529711f3`.

## Boundary and next gate

Even a successful executor boot would establish only a clean physical process
with the declared host layout. It would not prove the same native runtime
address contains a live target mapping, share writable ntdll state, or provide
the cross-process kernel state needed to resume an actual E05 driver
continuation. The next gate is to implement and validate revocable live views
of eligible private mappings, then exercise ordinary pointer loads through
the unchanged attachment fixture with correct kernel-thread and attached-
process identities. `KeStackAttachProcess` and `KeUnstackDetachProcess`
remain unimplemented until those semantics are demonstrated. Native Windows,
i386, accepted Vanguard sessions and gameplay remain unproven.

## Publication provenance

The tested source changes were committed after the recorded runtime runs as
Wine commit [`084fc093b4eaec9f66a942f5d902496318762abb`](https://github.com/erick-dsnk/wine/commit/084fc093b4eaec9f66a942f5d902496318762abb)
and published on `erick-dsnk/wine:vanguard-attachment-prerequisites`.
An isolated clean HTTPS clone of that branch retrieved the exact commit and
matched all **28 source hashes** in the frozen manifest. Its Git tree is
`6b58306aef6fbd92db5aab5ecf70eae8cc10c429` and the clone's worktree was clean.
The historical manifest's `dirty_unpublished_sources` field describes the
state at test time; publication did not change the tested source bytes or rerun
the assembled-artifact runtime. The Proton gitlink now references this
accessible component commit. Repository checks remain separate from the
recorded runtime evidence and unresolved attachment gates.
