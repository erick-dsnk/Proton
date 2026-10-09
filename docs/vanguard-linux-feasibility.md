# Vanguard Linux feasibility: frozen research baseline

Research baseline: **9 October 2026**. Target: **Ubuntu 24.04.4 LTS (Noble), x86-64, installed kernel 7.0.0-38-generic**, on the laptop described below. Target vendor artifacts: **Vanguard 1.19.1.18**. This document lives in the [erick-dsnk/Proton fork](https://github.com/erick-dsnk/Proton) and describes compatibility engineering for unmodified Vanguard and League of Legends.

This is the preserved research snapshot that founded the **Proton Vanguard
compatibility effort**, an open source attempt to bring League of Legends back
to Linux through genuine Vanguard compatibility. Its source inventories and
"not performed" statements describe the research baseline, not current project
status. Subsequent work is recorded in the [implementation register](vanguard-implementation-progress.md),
with contributor priorities in the [roadmap](ROADMAP.md) and architecture
decisions in the [architecture guide](ARCHITECTURE.md). No accepted Vanguard or
League session has been demonstrated by this effort.

## Contents

1. [Engineering conclusion and the first decision](#1-engineering-conclusion-and-the-first-decision)
2. [Frozen target and reproducibility](#2-frozen-target-and-reproducibility)
3. [Platform and trust requirements](#3-platform-and-trust-requirements)
4. [Architecture options and falsification experiments](#4-architecture-options-and-falsification-experiments)
5. [Existing Wine execution path](#5-existing-wine-execution-path)
6. [Confirmed static interface gaps](#6-confirmed-static-interface-gaps)
7. [Lifecycle, platform and conditional gaps](#7-lifecycle-platform-and-conditional-gaps)
8. [Structured implementation backlog](#8-structured-implementation-backlog)
9. [Research snapshot validation and handoff state](#9-research-snapshot-validation-and-handoff-state)
10. [Complete static import inventory](#appendix-a-complete-static-import-inventory)

## 1. Engineering conclusion and the first decision

The inspected Wine already loads some Windows drivers into a user-space driver host, invokes their entry points, manages device objects, and carries device-control requests. The inspected Vanguard driver requests 129 static interfaces: **14 are missing exports, 12 are explicit export stubs, and additional implemented exports lack required behavior**. These give a concrete compatibility backlog. The user service requests 357 interfaces, all with matching Wine exports; their behavior has not been validated.

Completing that backlog does **not** establish a complete route to Vanguard on Ubuntu. The harder questions are whether the driver's runtime uses Windows address-space or privileged-machine semantics that the chosen architecture cannot supply, and whether its authentic platform evidence is accepted by Vanguard's session verifier. Resolve those questions early, in parallel with a small generic driver test harness. Do not spend a full implementation campaign assuming they disappear after import resolution.

There is currently **no demonstrated accepted Vanguard session or playable League session on this target**. The technically concrete proposal is a staged feasibility project with explicit gates, followed by implementation only where the required contract and architecture are understood. This document inventories all gaps established by the investigations, tracks plausible conditional gaps separately, and defines how to discover the remaining unknowns. It cannot enumerate every hidden runtime/backend requirement from static metadata alone.

### 1.1 Evidence labels

- **Observed:** host state, encoded PE imports, or the implementation at the pinned source revision.
- **Documented:** a contract or requirement published by Microsoft, Riot, Valve, or Canonical.
- **Hypothesis:** a proposed compatibility design requiring tests; it is not a delivered implementation.
- **Conditional:** a confirmed limitation whose relevance depends on the actual runtime call, parameter, mode, or returned restriction.
- **Unknown:** a dependency or behavior not established by this investigation.

An import establishes that a binary requests an interface. It does not establish that a particular execution path calls it. Conversely, absence from static imports does not establish non-use: both binaries import dynamic resolvers.

### 1.2 Early gates

| Gate | Question and required evidence | Consequence |
|---|---|---|
| **G0 — Freeze scope** | Exact Ubuntu/kernel/GPU/userspace, Wine and Proton SHAs, vendor hashes, selected Vanguard mode, and an ordinary Windows reference are recorded. | Do not mix system Wine 9 with this Wine revision or silently switch Ubuntu kernels. |
| **G1 — Platform acceptance** | Determine the chosen mode's actual required properties and whether this architecture can produce genuine evidence for them. A native Windows reference establishes normal behavior; it does not establish Ubuntu acceptance. | If a required Windows Secure Kernel identity cannot be supplied by the architecture, park that playability route. Linux-specific trusted integration requires a verifier that accepts Linux. |
| **G2 — Execution architecture** | A benign test driver demonstrates every required address-space, execution-context, and privileged-state contract the proposed architecture claims. Target-specific use remains separately established. | Ordinary pointer access after process attachment or coherent privileged state may force a larger architecture than user-space Wine patches. |
| **G3 — Generic conformance** | Loader, SCM, device transport, and each implemented API family pass Windows-reference comparisons, including failure/race cases. | No fake-success implementation qualifies. |
| **G4 — Genuine local operation** | Unmodified target artifacts reach DriverEntry, stable driver/service state, and correct device communication under the documented environment. | Report these milestones individually; local readiness alone is insufficient. |
| **G5 — Genuine session and gameplay** | The environment obtains an accepted anti-cheat session and completes a connected League match without anti-cheat disconnect. | This is the actual requested outcome. No prior investigation passed it. |
| **G6 — Regression** | Reboot, mode transition, package/client update, stop/uninstall, and sustained operation preserve G4/G5. | A one-time startup is not a usable implementation. |

The first sprint should start G0/G1 and a minimum G2/G3 harness. G1 must remain an explicit dependency of G5, rather than being scheduled as an ordinary missing-API fix.

## 2. Frozen target and reproducibility

### 2.1 Research host snapshot

Read-only observations on 9 October 2026; these are measured host facts, not evidence that Vanguard or a custom Proton build works.

| Component | Observed baseline | Scope or uncertainty |
|---|---|---|
| Distribution | Ubuntu **24.04.4 LTS**, `VERSION_ID=24.04`, codename `noble` | Only this release is the initial Linux target. |
| Kernel/architecture | **7.0.0-38-generic**, **x86_64** | The installed kernel was observed; its being a stock or supported Noble/HWE kernel was not established. Pin this actual kernel and headers in experiments. |
| CPU/memory | Intel Core i5-11320H, 4 cores / 8 logical CPUs; 15 GiB RAM, 4 GiB swap | Available RAM was 1.9 GiB during collection and changes with workload. Bound build/test concurrency. |
| Repo filesystem | Approximately 196 GiB free at collection | No actual full-build space requirement measured. |
| Graphics | Intel Iris Xe using `i915`; NVIDIA RTX 3050 Mobile using `nvidia`, loaded version **595.58.03** | Hybrid graphics/device selection and rendering are untested. |
| Vulkan packages | Loader `1.3.275.0-1build1`, Mesa Vulkan `25.2.8-0ubuntu0.24.04.2`, Intel/NVIDIA ICD descriptors present | `vulkaninfo` absent; no instance, device/extension enumeration or rendering test. Installed packages are not runtime proof. |
| EFI/Secure Boot | EFI interface present; `mokutil`: **SecureBoot disabled**, **Platform is in Setup Mode** | No firmware change made. Enabling Secure Boot requires actual firmware/provisioning investigation and does not make Wine a Windows attestation environment. |
| TPM | `/dev/tpm0` and `/dev/tpmrm0` present | TPM 2.0 capability, provisioning, PCR state, keys and verifier acceptance untested; `tpm2_getcap` absent. |
| IOMMU | 17 exposed groups | Device isolation/passthrough suitability untested. |
| Virtualization | VT-x reported; `/dev/kvm` accessible; QEMU 8.2.2, libvirt 10.0.0 installed | No guest created; actual guest/firmware/TPM/graphics configuration untested. |
| Build runtime | Docker client and reachable daemon **29.4.3**; git 2.43.0, make 4.3, GCC/G++ 13.3.0, CMake 3.28.3, Ninja 1.11.1 | No SDK image pulled and no Proton/Wine build run. |
| Python | PATH Python is Miniconda 3.13.12; `/usr/bin/python3` is 3.12.3 | Use explicit isolated tooling; avoid accidental interpreter/environment mixing. |
| System Wine | Ubuntu package `9.0~repack-4build3` | Distinct from this fork's Wine. Its execution cannot validate this checkout. |

Observations used `/etc/os-release`, `uname`, selected `lscpu` fields, `free`, `df`, `mokutil --sb-state`, TPM/KVM/IOMMU sysfs/node presence, selected GPU `lspci` and package/module versions, and `docker info`. No serials, MAC addresses, hostnames, firmware changes, installation, or vendor execution were needed.

### 2.2 Repository and build baseline

| Item | Pinned value |
|---|---|
| Repository | `https://github.com/erick-dsnk/Proton`, fork of `ValveSoftware/Proton` |
| Local checkout/branch | `/home/eric/repos/proton`, `research/vanguard-kernel-feasibility` |
| Proton commit | `bc896217ffcd67f892f952b010f898fe7bd0f0a1` |
| Wine gitlink/checkout | `e60892cc2398b0a83c332a2078c7b85e47bdb42b` (`proton-wine-11.0-2e`) |
| Wine fetch origin | `ValveSoftware/wine`, using a local submodule URL override because the fork-relative URL would target a missing user Wine fork |
| Initial cleanliness | Both Proton and Wine clean before this document; no compatibility patch exists |
| Submodules | Wine initialized; **22 other submodules uninitialized** |
| Proton SDK image tag | `registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64:4.0.20260331.220802-0` |

The [pinned README](https://github.com/ValveSoftware/Proton/blob/bc896217ffcd67f892f952b010f898fe7bd0f0a1/README.md#L48) describes the container build; the [pinned Makefile](https://github.com/ValveSoftware/Proton/blob/bc896217ffcd67f892f952b010f898fe7bd0f0a1/Makefile.in#L30) selects the SDK image. Resolve and record its digest when pulling it. Host clang, bison, flex and MinGW were absent, but SDK toolchains can supply build dependencies; their absence is not automatically a Proton host blocker. Start with the Wine driver harness and a minimal required toolchain. Fetch all other pinned Proton submodules when a complete Proton integration build becomes necessary.

### 2.3 Vendor package

Riot's [unqualified public client configuration](https://clientconfig.rpg.riotgames.com/api/v1/config/public), retrieved **2026-10-09 21:20:23 UTC**, advertised [Vanguard installer 1.19.1.18](https://riot-client.secure.dyn.riotcdn.net/channels/public/rccontent/vanguard/1.19.1.18/setup.exe). Download completed at **21:20:39 UTC** without redirects. This identifies the public-channel package at retrieval, not every regional/account/platform delivery.

| Artifact | Bytes | SHA256 |
|---|---:|---|
| `setup.exe` | 143,828,768 | `a39fe534395740f7cadec38cb387f3bc508983004e217e53bc7541345e732087` |
| `vgk.sys` | 109,721,528 | `8ba32cfbc4a07fd41a082344e23e312515ffafef0e568ba72e7d33e83b558f13` |
| `vgc.exe` | 107,505,544 | `c8f330a77351f36e1112d0b94972a735a7747fc33a4aa4735d95f43f01637c51` |

7-Zip 23.01 extracted the two files from the installer's embedded solid 7z archive. Both are x64 PE images with resource version `1.19.1.18` and string version `1.19.1-18+20261001.143443`. Certificate metadata names Riot Games, Inc. / DigiCert. **Authenticode digest, chain, trust and revocation were not verified.** No installer, driver or service was executed, installed, memory-unpacked or patched.

The static parser used `pefile 2024.8.26`. A benign Wine `zlib1.dll` fixture yielded 44 imports independently corroborated by GNU objdump. The final exact DLL/name/encoded-ordinal multisets of both Vanguard files also matched independently parsed GNU objdump output. A parser correction preserves encoded ordinals instead of treating pefile's standard-name hints as imported names. The analysis establishes interface metadata and selected source behavior, not a complete code-path or security-check inventory.

## 3. Platform and trust requirements

### 3.1 Mode-specific requirements

[Riot's 24 June 2026 On-Demand announcement](https://www.riotgames.com/en/news/vanguard-on-demand) describes an optional mode loading the driver with a Riot game and unloading after gameplay. Therefore “every current Vanguard must always start during boot” is obsolete. The conventional mode retains early-presence/integrity-continuity behavior. The actual installation `START_TYPE` and mode transitions of this package have not been observed on Windows.

| Requirement | Evidence and scope | Ubuntu consequence |
|---|---|---|
| On-Demand platform | [Riot Pre-Check](https://support.riotgames.com/en-us/riot/performance/vanguard-pre-check): Windows 11 25H2+, Secure Boot, TPM 2.0, IOMMU, VBS and HVCI | Normal Wine on Ubuntu does not satisfy the documented Windows platform identity. Hardware capabilities alone do not supply Windows VBS/HVCI. |
| Conventional continuity | Riot's On-Demand article explains the existing early-driver-presence rationale | A service after Ubuntu login or a prefix restart does not prove equivalent host-wide history. Exact binary/backend enforcement remains unknown. |
| League's Secure Boot scope | The same Riot article distinguishes League from VALORANT and says Secure Boot is not required for every Windows 11 League player | Do not transfer universal VALORANT requirements to League. On-Demand has its own explicit requirement. |
| Conditional restrictions | [Security requirements](https://support.riotgames.com/en-us/riot/performance/vanguard-security-requirements) and [VAN: RESTRICTION](https://support.riotgames.com/en-us/riot/penalties/error-van-restriction) describe configuration-dependent conditions | Record actual mode, account/configuration, Windows reference build and returned restriction. Do not assume every listed property applies to every session. |
| TPM/Secure Boot/VBS failures | [VAN 9001](https://support.riotgames.com/en-us/riot/client/error-van-9001), [VAN 9003](https://support.riotgames.com/en-us/riot/client/error-van-9003), [VAN 9005](https://support.riotgames.com/en-us/riot/client/error-van-9005) | These establish enforcement categories, not exact APIs or commands used by this build. |
| VM rejection | [VAN 138](https://support.riotgames.com/en-us/riot/performance/error-van-138) documents unsupported virtualized environments | A genuine Windows VM is a generic API lab option, not a validated Vanguard gameplay solution. |

Riot's [2024 Vanguard x LoL article](https://www.leagueoflegends.com/en-us/news/dev/dev-vanguard-x-lol/) describes the then-current Wine/Lutris driver limitation, trust concerns about host-controlled VMs, and anti-cheat-session validation. It is historical architecture context, not a disclosure of every check in build 1.19.1.18. Valve's [Steamworks Proton guidance](https://partner.steamgames.com/doc/steamhardware/proton) describes Proton and vendor-enabled EAC/BattlEye paths, and distinguishes unsupported kernel anti-cheat. EAC/BattlEye integration is evidence that vendor integration is a real solution family, not evidence that Vanguard works through the same mechanism.

### 3.2 What genuine attestation would require

[Microsoft's `GetRuntimeAttestationReport`](https://learn.microsoft.com/en-us/windows/win32/api/sysinfoapi/nf-sysinfoapi-getruntimeattestationreport) returns a nonce-bearing signed Windows Secure Kernel report about driver/code-integrity state, with TPM 2.0, Secure Boot, VBS, HVCI and IOMMU requirements. Test-signing/debug flags must be off. The [implementer's explanation](https://www.andrea-allievi.com/blog/new-year-post-anti-cheat-evolution-in-windows-11/) describes measured identity, signing key, TPM evidence and retained unloaded-driver history. This supports the architecture analysis; it does not establish exactly which verification steps Riot implements.

[Microsoft HVCI documentation](https://learn.microsoft.com/en-us/windows/security/hardware-security/enable-virtualization-based-protection-of-code-integrity?tabs=intune) describes code-integrity enforcement inside the Windows VBS environment. Ubuntu's [Secure Boot](https://documentation.ubuntu.com/security/security-features/platform-protections/secure-boot/), [TPM](https://documentation.ubuntu.com/security/security-features/platform-protections/trusted-platform-module/) and [kernel protections](https://documentation.ubuntu.com/security/security-features/kernel-protections/) provide useful genuine Linux capabilities, with a different measured boot and enforcement baseline.

**Design inference:** a real Ubuntu TPM can attest Ubuntu measurements. Renaming that report or implementing the Windows function signature does not produce proof of Microsoft's Secure Kernel protecting this Linux environment. A Linux report requires an accepting verifier for its own platform chain. A locally signed Ubuntu bridge module does not automatically become trusted by Riot. The conventional mode's exact evidence protocol is unknown and must not be assumed identical to On-Demand.

Secure Boot is currently disabled on this laptop. That is a measured prerequisite issue for an environment that actually requires it; it is not a standalone fix for Wine. Investigate genuine firmware/key provisioning only after selecting the relevant environment. The acceptance gates require the measured state, implementation and resulting evidence to agree.

## 4. Architecture options and falsification experiments

| Architecture | Proposed technical contribution | Limitation / falsification test | Feasibility status |
|---|---|---|---|
| **A1: Extend Wine's user-space driver host** | Real sync/lifetime/data exports, virtual execution context, SCM/IOCTL/object/query behavior; reuse existing loader and transport | Test ordinary attached-process pointer dereferences and required privileged state. A host thread's logical process tag does not change its address space. Windows Secure Kernel evidence and host-wide Linux enforcement are absent. | Useful bounded conformance work; actual Vanguard acceptance unresolved. Initial implementation target. |
| **A1b: Controlled per-process driver execution** | Execute compatible callbacks in a target Wine process or a runtime owning multiple guest address spaces, with shared driver state | Requires common mappings, shared/private classification, nested attachment/APC state and fault/lifetime behavior. Two processes with the same virtual address and different bytes must remain distinct. Native thread migration is not a simple API. | A1 memory-architecture research hypothesis; substantial loader/server/runtime changes, not yet prototyped. |
| **A2: Wine plus a narrowly specified Ubuntu kernel broker** | A reviewed host component could provide real Linux memory/process/device operations and lifetimes unavailable in user space | Define NT↔Linux ABI and ownership; test actual pointer/context semantics. Linux ring 0 is not Windows ring 0, and a binary Windows driver cannot simply be linked into the Linux kernel. Broker trust and accepted evidence remain external gates. | Research hypothesis only; no design, prototype or accepted trust baseline. Avoid introducing it before demonstrated need. |
| **A3: Complete NT-compatible execution environment** | Model NT objects/address spaces/scheduling and privileged machine state rather than isolated API calls | Requires coherent MMU/interrupt/private-layout behavior wherever exercised. Generic emulation is not an accepted Windows measured environment. A few privileged-instruction handlers do not constitute this architecture. | Large OS/runtime research project; not an extension-sized promise. |
| **A4: Actual Windows guest on Ubuntu/KVM** | Actual NT contracts for generic reference experiments | Riot documents VM rejection; guest HVCI does not protect against the outer host administrator. KVM/IOMMU availability alone does not pass platform acceptance. | Diagnostic/reference option where suitable; no current gameplay route established. |
| **A5: Riot-authored or accepted native Linux integration** | Native service/module, real Linux host coverage, Linux-specific measurements and backend validation | Requires vendor components and verifier acceptance outside this fork's control | Architecture that can address the platform boundary; unavailable as a community-only deliverable. |
| **A6: Native Windows / dual boot** | Normal documented environment and useful reference behavior | Does not run Vanguard on Ubuntu | Baseline or fallback, outside the requested outcome. |

A2/A3 do not get approved merely because A1 fails a test. First document the exact operation and why a smaller compatible design cannot implement it. Explicit cross-process copy can reuse Wine's [process_vm_readv/ptrace backend](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/server/ptrace.c#L351), whose [Linux contract](https://man7.org/linux/man-pages/man2/process_vm_readv.2.html) copies between address spaces; it does not switch ordinary dereference context. A2 may use genuine [Linux page pinning](https://docs.kernel.org/core-api/pin_user_pages.html), with separate kernel-version/signing maintenance. A3 needs coherent emulated registers, MMU, faults, atomics and multi-vCPU state, plus synchronization with native game memory if only the driver is emulated. [KVM](https://docs.kernel.org/virt/kvm/api.html) supplies genuine guest execution for A4, but game and driver must share the same guest; a disconnected Windows driver cannot monitor a native Proton process using Windows pointers. A genuine full Windows reference avoids guessing API contracts; a disposable generic-driver lab must be separate from the normally secured Vanguard reference, since test-signing/debug configuration itself changes relevant security properties.

## 5. Existing Wine execution path

The pinned Wine contains this real path:

```text
services.exe -> driver-service routing -> winedevice.exe
             -> ntoskrnl!ZwLoadDriver -> PE loader -> DriverEntry
             -> device objects / wineserver requests -> IRP dispatch / IOCTL completion
```

Source: [services driver routing](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/programs/services/services.c#L820), [winedevice service](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/programs/winedevice/device.c#L76), [driver loading](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.c#L3940), [initialization/entrypoint](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.c#L4041), [device dispatch](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.c#L727).

This executes in a Wine user-space process. Wine's [autostart handling](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/programs/services/services.c#L409) recognizing boot/system-start flags does not mean Linux boot-time protected execution. The distinct user-mode [ntdll `NtLoadDriver`](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntdll/unix/system.c#L4967) is unimplemented. Preserve the distinction between service-route loading and direct syscall loading.

The [PE loader](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntdll/loader.c#L1247) can supply unimplemented-function thunks for absent imports. Therefore the 14 absent names are not all proven pre-DriverEntry failures. They can fail when reached. A function thunk is also not a correct replacement for imported data.

## 6. Confirmed static interface gaps

Driver normal imports: **129**, no delay imports or encoded ordinals; `ntoskrnl.exe` 119, `cng.sys` 9, `HAL.dll` 1. Service normal imports: **357**, no delay imports; **309 names + 48 encoded ordinals** (32 WS2_32 and 16 WLDAP32). Appendix A lists every encoded import. Import-table coverage must remain distinct from tested semantics.

### 6.1 All 14 missing driver exports

Observed absence was checked against the pinned `ntoskrnl.exe.spec` and module sources, not inferred from absent lexical definitions or header inlines. A header inline cannot satisfy an encoded PE import by itself. Proposed implementation files are relative to the `wine/` submodule.

| Gap ID | Actual imported name(s), counted individually | Compatibility hypothesis | Validation / failure criterion | Epic |
|---|---|---|---|---|
| **K01** | `KeAcquireGuardedMutex`, `KeReleaseGuardedMutex` (2) | Add paired ownership/contention behavior and correct guarded-region/APC interaction using existing initialization | Native-reference contention, recursive/invalid use where defined, APC suppression/restoration, release and teardown; fail if success does not exclude competing owners | E03, E04 |
| **K02** | `ExInitializePushLock`, `ExAcquirePushLockExclusiveEx`, `ExReleasePushLockExclusiveEx` (3) | Implement opaque push-lock initialization, exclusive acquisition, flags, wake-up and lifetime using compatible atomics/waiting; preserve pointer-sized storage and inline-WDK compatibility | Many-thread acquire/release, initialization/reuse, legal flags, waiters and teardown; validate any required structure ABI | E03 |
| **K03** | `KeGetCurrentIrql`, `KeIpiGenericCall` (2) | One coherent virtual execution model, with per-context IRQL and a rendezvous protocol for the processors that model exposes | Raise/get/restore agree; all modeled processors execute one callback at required context with barrier ordering; fail if required real interrupt/MMU semantics exceed A1 | E04, G2 |
| **K04** | `KeQuerySystemTimePrecise` (1) | Convert a genuine high-resolution host clock into the Windows time/precision contract | Epoch/units, resolution, wall-clock adjustment and comparison with coarse/monotonic queries; do not confuse precision with a monotonic wall clock | E06 |
| **K05** | `ExAllocateCacheAwareRundownProtection`, `ExFreeCacheAwareRundownProtection`, `ExAcquireRundownProtectionCacheAwareEx`, `ExReleaseRundownProtectionCacheAwareEx`, `ExWaitForRundownProtectionReleaseCacheAware` (5) | Correct allocation, distributed acquisition counts, rejection after rundown begins, wait-for-last-release and final free | Multi-CPU acquire/release versus concurrent rundown; count/overflow/error cases and safe cleanup; fail if waits return while users remain | E03, E04 |
| **K06** | `IoInitializeWorkItem` (1) | Caller-owned work-item initialization consistent with existing allocate/queue behavior and object lifetime | Reference size/layout, associated device lifetime, queued callback, cancellation/teardown; no unowned callback after free | E03, E07 |

Primary Windows contracts for proposed synchronization/time designs: [guarded mutexes](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/fast-mutexes-and-guarded-mutexes), [push-lock initialization](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-exinitializepushlock) and [exclusive-acquire macro](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-exacquirepushlockexclusive), [rundown protection](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/run-down-protection), [processor rendezvous](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-keipigenericcall), [precise system time](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-kequerysystemtimeprecise), [work-item initialization](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-ioinitializeworkitem). The actual imported push-lock Ex variants' `Flags` contract needs WDK definitions and native tests; the non-Ex macro documentation alone does not settle it. Cache-aware acquire/release must test count values greater than one. A correctness-first opaque allocation using ordinary rundown semantics is a design hypothesis; per-CPU optimization is not automatically required for functional correctness. Guarded locks must preserve caller-allocated size/alignment and nonrecursive ownership; do not embed a larger host lock object in Windows storage. Design details must follow the relevant Windows reference behavior, including version-dependent semantics, rather than matching return values alone.

### 6.2 All 12 explicit imported stubs

Every source link is immutable at the audited Wine commit. The last column proposes work; nothing in this table has been implemented or tested here.

| Gap ID | Import | Observed export declaration | Required solution and decisive test | Epic |
|---|---|---|---|---|
| **K07** | `KeDeregisterBugCheckReasonCallback` | [spec:554](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.exe.spec#L554) stub | Pair registration/removal with lifetime and callback-state handling; remove during in-flight handling safely | E06 |
| **K08** | `KeRegisterBugCheckReasonCallback` | [spec:629](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.exe.spec#L629) stub | Implement documented registration and reason-specific data contracts; determine whether host crash context is actually required; never equate a stored callback with Windows bugcheck support | E06, G2 |
| **K09** | `ExInitializeRundownProtection` | [spec:7](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.exe.spec#L7) stub | Initialize state/ABI consistently; fresh and reused object tests | E03 |
| **K10** | `ExAcquireRundownProtection` | [spec:5](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.exe.spec#L5) stub | Atomic accepted/rejected acquisition during rundown races | E03 |
| **K11** | `ExReleaseRundownProtection` | [spec:17](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.exe.spec#L17) stub | Release counts and wake final teardown exactly once | E03 |
| **K12** | `ExWaitForRundownProtectionRelease` | [spec:20](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.exe.spec#L20) stub | Prevent new acquisitions, wait for existing users; zero-user and contention tests | E03 |
| **K13** | `KeNumberProcessors` | [spec:603](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.exe.spec#L603) stub, expected **data** | Supply correct type/size/value and coherent legacy processor/group/topology semantics, not assumed host online-count equivalence; inspect built export and dereference through a test driver | E03, E04 |
| **K14** | `KeInsertQueueApc` | [spec:596](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.exe.spec#L596) stub | Real queueing/delivery, target-thread identity, disable rules, cancellation/exit and rundown; return-only success fails | E04 |
| **K15** | `IoQueryFileInformation` | [spec:442](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.exe.spec#L442) stub | Translate observed classes through real file/object identity with native-reference buffer/status contract; Microsoft reserves this routine for system use, so exact behavior is not settled by its signature; short buffers and deleted files | E06 |
| **K16** | `MmHighestUserAddress` | [spec:730](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.exe.spec#L730) stub, expected **data** | Export actual compatibility address-space boundary, consistent with probe/map behavior; dereference and boundary tests | E03, E05 |
| **K17** | `KeInitializeMutant` | [spec:584](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.exe.spec#L584) stub | Resolve the exact imported mutant variant's WDK/native contract; initialize real waitable ownership, recursion/release and APC state, without assuming `KeInitializeMutex` equivalence; wait/release/abandonment tests | E03, E04 |
| **K18** | `MmFreePagesFromMdl` | [spec:724](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.exe.spec#L724) stub | Free owned page allocations in a coherent MDL lifecycle; allocation failure, map/unmap and repeated cleanup fixtures | E05 |

For callback semantics see [Microsoft bugcheck registration](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-keregisterbugcheckreasoncallback); for APC behavior see [Microsoft APCs](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/types-of-apcs) and [APC disabling](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/disabling-apcs). Additional contracts: [legacy processor count/groups](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-kequeryactiveprocessorcount), [mutex context](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-keinitializemutex), and [reserved IoQueryFileInformation](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntifs/nf-ntifs-ioqueryfileinformation). Data exports require PE ABI validation, not only source declarations.

### 6.3 Present exports with observed semantic gaps

| Gap ID | Imported interface and pinned behavior | Proposed implementation and falsification test | Evidence / epic |
|---|---|---|---|
| **K19** | `MmAllocatePagesForMdl` returns `NULL` | Allocate real owned pages and compatible MDL/PFN state with constraints and failure behavior; test sizes/alignment/failure/cleanup | [ntoskrnl.c:2870](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.c#L2870); E05 |
| **K20** | `MmBuildMdlForNonPagedPool` is a no-op | Derive a valid MDL for tracked allocation ranges without pretending arbitrary untracked memory is valid; verify flags/span and mapping lifecycle | [ntoskrnl.c:2881](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.c#L2881); E05 |
| **K21** | `MmMapLockedPagesSpecifyCache` returns `NULL`; `MmUnmapLockedPages` does nothing | Map genuine owned/locked buffers into the chosen address space, maintain cache/access/protection and ownership; compare round-trip data, permissions, errors and cleanup | [ntoskrnl.c:2970](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.c#L2970), [2981](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.c#L2981); E05 |
| **K22** | `KeStackAttachProcess` / `KeUnstackDetachProcess` are no-ops | Architecture for subsequent ordinary accesses in the target process and restoration/nesting; a benign driver dereferences a known target-only mapping after attachment. Failure disproves a metadata-only design | [ntoskrnl.c:4620](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.c#L4620), [4625](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.c#L4625); E05, G2 |
| **K23** | `ProbeForRead` / `ProbeForWrite` perform no checks | Correct range/overflow/alignment/user-boundary and exception behavior; `ProbeForRead` does not require touching every page, while legacy write probing has per-page writable-access semantics. Test zero-length, misalignment, inaccessible/read-only, boundary/overflow and remap cases; later accesses can still fault | [ntoskrnl.c:3727](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.c#L3727), [3735](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.c#L3735); E05 |
| **K24** | `ObReferenceObjectByPointer` returns `STATUS_NOT_IMPLEMENTED`; `ObReferenceObjectByHandle` has a KernelMode path but UserMode returns not-implemented | Real typed object/reference lifetimes, mode/access validation, handle information and balanced dereference; wrong type/rights, closed handles, target exit and reference races | [ntoskrnl.c:3120](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.c#L3120), [350](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.c#L350); E06 |
| **K25** | x64 `KfRaiseIrql` / `KeLowerIrql` do not update execution level; raise does not supply old value | Integrate with K03/APC/spin-lock model; nested raise/get/restore and callback-context tests; fail if required hardware interrupt masking is outside A1 | [ntoskrnl.c:4650](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.c#L4650), [4655](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.c#L4655); E04 |
| **K26** | `KeAcquireSpinLockRaiseToDpc` has real user-space atomic locking but returns constant IRQL; release ignores supplied IRQL | Preserve mutual exclusion while coordinating virtual IRQL and legal blocking; contention and old-context restoration tests | [sync.c:646](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/sync.c#L646), [658](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/sync.c#L658); E04 |
| **K27** | Critical-region enter/leave and `KeAreAllApcsDisabled` use a per-thread counter, not a full APC/IRQL model | Model distinct disabling rules and nest/restore behavior; queued APC delivery must match actual context and thread lifetime | [ntoskrnl.c:3674](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.c#L3674), [3683](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.c#L3683), [3702](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.c#L3702); E04 |
| **K28** | `ZwQuerySystemInformation` aliases `NtQuerySystemInformation`; classes vary, module list is fixed/synthetic and unsupported classes return invalid-info-class | Record actual classes; build consistent inventories from real modeled objects/images; distinguish Windows-only guarantees from Linux facts. Compare sizes, versions, status and concurrent lifecycle | [spec:1499](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.exe.spec#L1499), [system.c:3554](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntdll/unix/system.c#L3554), [3768](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntdll/unix/system.c#L3768), [4291](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntdll/unix/system.c#L4291); E06, E08 |
| **K29** | `PsCreateSystemThread` creates a Wine user thread via `RtlCreateUserThread` | Define compatible thread/object identity, execution context, wait/termination and cleanup in chosen runtime; compare lifecycle and callers' required observations | [ntoskrnl.c:3194](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.c#L3194); E04, E06, G2 |

Memory contracts: [MDLs](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/using-mdls), [locked-page mapping](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-mmmaplockedpagesspecifycache), [process attachment](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntifs/nf-ntifs-kestackattachprocess), [ProbeForRead](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-probeforread), [ProbeForWrite](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-probeforwrite), [object references](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-obreferenceobjectbyhandle). A host allocation/locking primitive may implement some owned-buffer contracts; it is not proof of Windows PFNs, arbitrary physical mappings, or arbitrary attached-process pointers.

Existing asynchronous work must be preserved: `KeInitializeDpc` is imported, but `KeInsertQueueDpc` is **not** statically imported. Wine's [timer callback](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/sync.c#L438) invokes a DPC routine through a threadpool; [IoQueueWorkItem](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.c#L1301) actually queues work. Context, ordering, cancellation and teardown need conformance tests. There is no finding that all asynchronous work is absent. The existing work-item path discards scheduling-failure results and stores mutable callback/context, so queue failure and legal reuse/lifetime need explicit tests; this is a conditional source limitation, not a demonstrated Vanguard failure. Relevant contracts include [IoQueueWorkItem](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-ioqueueworkitem), [hardware priorities](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/managing-hardware-priorities), [DPC objects](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/introduction-to-dpc-objects), and [system threads](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-pscreatesystemthread).

### 6.4 Present exports that remain unreviewed

The driver classification is **14 absent + 12 explicit stubs + 103 export-present/semantics-unverified**. The 103 category includes the manually reviewed examples above and other imports whose full behavior was not audited. It does not mean 103 functions work. The nine CNG functions forward to `bcrypt`; implementations exist, but parameters are unknown. `KeQueryPerformanceCounter` exists through [HAL](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/hal/hal.c#L190), calling `NtQueryPerformanceCounter`; exact timing requirements remain untested.

All 357 service imports have matching specifications, including the encoded fixed ordinals. `kernel32` often wraps `kernelbase`, service functions often wrap `sechost`, and a wrapper with no local C body is not automatically missing. The service's actual error handling, query parameters, thread behavior, crypto providers, SCM lifecycle and transport remain unreviewed runtime dependencies. Appendix A is the complete static inventory, not a completed conformance matrix. E00/E10 must maintain per-interface statuses: observed import → source reviewed → called contract observed → reference tested → Wine tested → target validated, without promoting entries automatically.

## 7. Lifecycle, platform and conditional gaps

| Gap ID | Evidence / unknown | Proposed solution or investigation | Exit or falsification evidence | Epic |
|---|---|---|---|---|
| **S01** | Installer only extracted; installed files/registry/services/start types/restart transitions unknown | Observe unmodified installation, selected mode, update/uninstall and restart on ordinary Windows; conformance-test equivalent state using benign fixtures | Known service dependencies/start types/paths/registry and reproducible state transitions; extraction is insufficient | E00, E07 |
| **S02** | `vgc` imports SCM APIs but their target behavior is untested | Match access rights, configuration, dependencies, pending/running/stopping states, dispatch/control-handler/recovery/timeouts | Compare real status and failure behavior; [`StartServiceW`](https://learn.microsoft.com/en-us/windows/win32/api/winsvc/nf-winsvc-startservicew) distinguishes driver initialization from user-service notification | E07 |
| **S03** | `NtDeviceIoControlFile` imported; target device names/IOCTLs/methods/parameters unknown | Reuse [existing generic IOCTL route](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntdll/unix/file.c#L7112); validate namespace, handle security, buffered/direct/caller-pointer I/O, status/byte counts and event/APC/cancel | Native/Wine generic fixtures agree including size/error/unload races; actual contract must be identified before target sufficiency claims | E05, E07, E10 |
| **S04** | `GetSystemFirmwareTable` imported; provider/table IDs unknown. Observed provider coverage only RSMB; other providers not-implemented | Identify required provider/table; faithfully translate accessible real-host data and precise errors | Requested provider supported with correct size/content contract; current RSMB construction is not full raw firmware passthrough | E06, E08, E10 |
| **S05** | System-information/security classes unknown; code-integrity query can return an enabled bit from a stub | Implement truthful class-specific modeled state; separate inventory from real policy enforcement | Genuine properties agree with report; a flag cannot replace signature/HVCI enforcement | E06, E08 |
| **S06** | Both binaries dynamically resolve APIs; protected-looking/high-entropy sections limit metadata inference | Record extra module/name/ordinal and observed contract from ordinary diagnostics and compatibility observations; retain unknowns until evidenced | New dependency has evidence and correct family/architecture classification; entropy alone never names a check | E10 |
| **S07** | CNG/WinVerifyTrust/CRYPT32 surfaces exist; action IDs, algorithms, blobs, padding/flags/provider operations unknown; artifact trust unverified | Genuine signature verification and algorithm/flag/blob/provider conformance fixtures, positive and negative | Valid signatures pass; changed/untrusted/revoked cases fail as applicable; no unconditional trust result | E08 |
| **S08** | Actual mode-dependent TPM/boot/attestation/backend checks unknown beyond public requirements | Identify selected mode and restriction; assess genuine Linux evidence and whether verifier accepts it | Accepted authentic chain for chosen platform, or explicitly unresolved/external dependency | E01, E08, G1 |
| **S09** | `MmGetSystemRoutineAddress`, `GetProcAddress`, `LoadLibrary` may reveal callbacks, private layouts or privileged operations later | Inspect only demonstrated dependencies; test coherent NT object/layout and CPU/address-space contracts | A1 either conforms to required operations or fails G2 and requires architecture review | E05, E09, E10 |
| **S10** | Socket/LDAP imports exist; DNS/TLS/certificates/time/client network and anti-cheat session untested | Validate ordinary network behavior; separate local readiness from genuine remote-issued anti-cheat session | Authentic session accepted under exact mode/platform; opaque backend behavior remains an external gate | E08, E11, G5 |
| **S11** | Current Riot Client and League launch/rendering/audio/input/session untested | Pin current client/game, validate installation/login/update and DXVK/Vulkan/GPU selection on this laptop after lower gates | Complete connected gameplay, no anti-cheat disconnect, recorded runtime stack/stability | E11, G5 |
| **S12** | Reboot/update/mode transition/stop/uninstall regressions untested | Preserve baseline inventories; diff new binaries; rerun affected conformance and genuine session checks | Repeat G4/G5 after package/client/kernel/driver changes with clean teardown | E12, G6 |

New observed firmware anchors: [`kernelbase` query](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/kernelbase/memory.c#L1930), [RSMB-only provider dispatch](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntdll/unix/system.c#L2718), [Linux SMBIOS construction](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntdll/unix/system.c#L2486). [Microsoft firmware contracts](https://learn.microsoft.com/en-us/windows/win32/api/sysinfoapi/nf-sysinfoapi-getsystemfirmwaretable) distinguish ACPI/FIRM/RSMB. ACPI/FIRM relevance is conditional; their being unsupported is not proof this service requests them. [Code-integrity stub](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntdll/unix/system.c#L4198) is relevant only if reached.

Device I/O contracts: [Microsoft buffering methods](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/buffer-descriptions-for-i-o-control-codes). Cryptographic trust contract: [WinVerifyTrust](https://learn.microsoft.com/en-us/windows/win32/api/wintrust/nf-wintrust-winverifytrust). Lifecycle sources: [Riot restart guidance](https://support.riotgames.com/en-us/riot/gameplay/how-to-fix-your-game-requires-a-system-restart-to-play), [reinstall/service guide](https://support.riotgames.com/en-us/riot/performance/uninstall-and-disable-vanguard).

The driver imports nine CNG functions: `BCryptVerifySignature`, `BCryptFinishHash`, `BCryptDestroyHash`, `BCryptImportKeyPair`, `BCryptCloseAlgorithmProvider`, `BCryptGetProperty`, `BCryptHashData`, `BCryptCreateHash`, `BCryptOpenAlgorithmProvider`. They forward to [existing bcrypt implementations](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/bcrypt/bcrypt_main.c#L368); exact algorithms/parameters are unresolved. `BCryptImportKeyPair` has an unsupported decrypt-key path in [the inspected implementation](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/bcrypt/bcrypt_main.c#L1000). This is a conditional parameter gap, not proof Vanguard uses that path or what its signature verifies.

### 7.1 Conditional extensions not justified as confirmed target work

These names are **not statically imported** by either audited binary: process/thread/image notification registration, `ObRegisterCallbacks`, `MmCopyVirtualMemory`, `MmGetPhysicalAddress`, `KeInsertQueueDpc`, TBS, `GetRuntimeAttestationReport`. Their dynamic use remains unknown. Do not implement them as established Vanguard requirements simply because they are plausible anti-cheat APIs.

If independently observed, known Wine limitations already suggest the following designs:

| Conditional area | Existing source limitation | Design / conformance requirement |
|---|---|---|
| Process/thread/image events | [Process/thread callbacks](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.c#L3299) include success stubs; [image callbacks](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.c#L3565) cover a limited driver-loading route | Bridge real prefix process/thread/image events through wineserver, with reentrancy, lifetime and unregister rundown. Prefix coverage is not host-wide Linux coverage. |
| Handle callbacks | [`ObRegisterCallbacks`](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.c#L3152) supplies a placeholder | Integrate create/duplicate pre/post operations and actual right changes with server handles; never just report registration success. |
| Memory copy/physical state | [`MmCopyVirtualMemory`](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.c#L4332) unimplemented; [physical-address/mapping behavior](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.c#L2929) incomplete | Real copy/fault/partial-result/lifetime semantics and coherent address model; arbitrary host physical access is not an NT model. |
| Direct DPC queue | [`KeInsertQueueDpc`](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl.c#L2639) reports success without queueing | Extend existing scheduler only when required; validate delivery/removal/CPU targeting and lifetime. |
| TPM/provider/report APIs | [TBS](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/tbs/tbs.c#L27) lacks a functional TPM backend; [NCrypt provider](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ncrypt/main.c#L519) is generic; no runtime-attestation identifier in recorded source search | Genuine provider/backend semantics, errors and key lifetime if used; authentic accepted platform evidence remains G1. |
| Private NT/CPU state | [Wine-private process/thread structures](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/ntoskrnl_private.h#L53) are small compatibility objects; [privileged instruction handler](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/instr.c#L483) is limited | Determine actual documented accessor versus direct-layout dependency; coherent ABI/MMU/context model if required. Additional instruction cases alone cannot establish it. |

## 8. Structured implementation backlog

These epics define scope, likely code ownership, dependencies and exit evidence. File paths are **candidate future ownership**, not a claim that changing only those files is sufficient. Keep one write owner per overlapping module; coordinate ntoskrnl/sync/server changes as a shared design. Review current upstream before implementation to avoid duplicating fixes beyond the pinned revision.

### E00 — Versioned evidence and Windows reference

**Depends on:** nothing. **Addresses:** G0, S01/S06 and complete import inventory. **Owner/files:** research/test tooling and fixtures outside vendor binaries; future `wine/dlls/ntoskrnl.exe/tests/` harness metadata.

Create a manifest of artifact hashes/version/encoded imports, Proton/Wine SHAs, SDK digest when resolved, Ubuntu stack, and chosen mode. Use separate ordinary secured Windows reference and generic-driver development lab. Record unmodified installer state, SCM configuration, mode transitions, normal restart and diagnostic behavior. Establish every tested contract's native result, including statuses, exceptions, ordering and lifetime. Preserve sanitized provenance only; acquisition response cookies are unnecessary.

**Exit:** reproducible inputs, actual reference mode/configuration, encoded-import baseline, a per-interface evidence status register and explicit unknown parameters. **Falsification:** reference behavior varies across modes/builds without being scoped; incorrect encoded ordinal interpretation; baseline hashes differ. **Blocked by:** access to a suitable Windows reference is not established here.

### E01 — Platform and architecture feasibility decision

**Depends on:** E00 baseline; runs before and in parallel with E02. **Addresses:** G1/G2, S08/S09. **Owner/files:** architecture decision/evidence; no automatic code changes.

Choose A1 initially for conformance work. Determine the selected mode's genuine requirements. Test the minimum process-attachment, private-state and execution-context hypotheses using a benign driver. Document accepted versus unavailable evidence and the boundary between prefix, host and Windows-only guarantees. If a reached contract requires properties A1 cannot produce, stop that route and evaluate a specified A2/A3 or vendor-integrated A5 design. Windows/KVM remains a generic reference, not an accepted Vanguard route.

**Exit:** an architecture decision with passed tests, failed tests and explicit external platform-acceptance dependency. **Falsification:** signed Windows evidence is required but only Linux measurements are available; ordinary attachment access cannot be modeled; privileged/private dependencies have no coherent implementation. **Blocked by:** actual runtime requirements and verifier acceptance remain unknown.

### E02 — Minimum build and generic driver harness

**Depends on:** E00; architecture scope from E01. **Addresses:** G2/G3. **Owner/files:** `wine/dlls/ntoskrnl.exe/tests/driver.c`, test-driver files/build descriptions and explicit isolated Wine build environment.

Reuse [existing MDL tests](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/tests/driver.c#L279) and [memory/attachment tests](https://github.com/ValveSoftware/wine/blob/e60892cc2398b0a83c332a2078c7b85e47bdb42b/dlls/ntoskrnl.exe/tests/driver.c#L2222). The inspected suite already has `todo_wine` memory cases and an attachment block skipped on Wine; an existing skip is not a pass. Compile only required tooling/tests initially. Validate x64 calling conventions, actual built exports/data sizes, entrypoint/unload and IOCTL transport. Record toolchain/compiler/linker/runtime revisions and native/Wine results.

**Exit:** generic test driver runs in both laboratories; reference and Wine failures recorded without suppressing them. **Falsification:** tests run system Wine instead of the built checkout; data exports remain function thunks; crashes/skip/todo statuses reported as passes. **Blocked by:** build prerequisites and reference lab, neither exercised yet.

### E03 — Synchronization, rundown, work-item initialization and data exports

**Depends on:** E02; E04 design for APC/IRQL-sensitive semantics. **Addresses:** K01/K02/K05/K06/K09–K13/K16/K17. **Owner/files:** `wine/dlls/ntoskrnl.exe/ntoskrnl.exe.spec`, `ntoskrnl.c`, `sync.c`, `ntoskrnl_private.h`, relevant ABI declarations/tests.

Implement real state/lifetime and exports. Start ordinary rundown and data-export ABI as bounded increments, then guarded mutex/push-lock/mutant/cache-aware rundown/work-item cases. Every increment includes tests for permitted initialization, ownership, waiters, rundown rejection, last-release wake-up and teardown. Coordinate processor-count data with E04 and user-address boundary data with E05.

**Exit:** native-comparison tests including many-thread races and unload lifetime pass; export kind/layout correct. **Falsification:** return-success shortcut, constant inaccurate topology/boundary, missed waiter or callback after free. **Blocked by:** exact shared opaque ABI or required execution-level semantics where unresolved.

### E04 — Coherent execution context and async delivery

**Depends on:** E01/E02, coordinated E03 primitives. **Addresses:** K03/K14/K25–K27/K29 and existing timer/work-item context. **Owner/files:** `wine/dlls/ntoskrnl.exe/sync.c`, `ntoskrnl.c`, `ntoskrnl_private.h`; relevant thread/server protocol only when required.

Define virtual IRQL, processor model, APC types/disable state, thread lifetime and callback execution/cancellation rules together. Add real APC queueing and rendezvous, preserve existing asynchronous code, and integrate spin-lock/critical-region behavior. A logical IRQL variable is useful only for contracts that can be modeled; it is not Linux interrupt masking or a genuine NT scheduler.

**Exit:** required ordering, callback identity/context, suppression/restoration, teardown and rendezvous tests pass native comparisons. **Falsification:** callback never fires, wrong target/context, unload race, model relies on a hardware property absent from A1. **Blocked by:** G2 for actual privileged execution requirements.

### E05 — Memory, MDLs, probe faults and process attachment

**Depends on:** E01/E02; E03 lifetime and E04 context. **Addresses:** K18–K23, S03/S09. **Owner/files:** `wine/dlls/ntoskrnl.exe/ntoskrnl.c`, private allocation/MDL state; relevant `wine/dlls/ntdll/unix/` memory and `wine/server/` paths after design approval.

First implement owned-buffer MDL allocation/build/map/unmap/free with coherent boundaries and failure behavior. Add probe/exception handling with boundary and concurrent-unmap tests, preserving the distinct read range/alignment versus legacy write-access contract. Track MDL storage separately from allocated pages and test separate page/MDL release, offsets, flags, partial allocation, alias visibility and read-only/NX behavior. Separately prototype attachment using target-only mappings and direct dereferences, plus restore/nesting/lifetime. A remote-memory copy helper cannot substitute for ordinary pointer accesses after attachment. Do not invent physical/PFN state where required operations expose it.

**Exit:** reference-comparison memory lifecycle, protection, faults, direct attached access and cleanup pass for reached contracts. **Falsification:** bookkeeping-only attachment fails the target-only pointer test; inconsistent mapping/ownership; required physical/private state cannot be implemented. **Blocked by:** G2 architecture decision; A2/A3 work requires a separate design if needed.

### E06 — Objects, files, time, queries and callback bookkeeping

**Depends on:** E02/E03, E05 for memory-dependent buffer contracts. **Addresses:** K04/K07/K08/K15/K24/K28, S04/S05. **Owner/files:** `wine/dlls/ntoskrnl.exe/ntoskrnl.c`, `wine/dlls/ntdll/unix/system.c`, `wine/dlls/kernelbase/memory.c`; server objects/handles only as required.

Implement typed references and rights/lifetimes, observed file-information classes and precise time. Match query sizes/status/privileges and derive inventories from actual modeled images/objects. Add real requested firmware provider support from accessible host data, never substitute invented Windows tables. Bugcheck registration requires lifecycle/state and reason-specific handling; if a real fatal kernel context is reached, re-enter G2 instead of claiming a host-process crash is equivalent.

**Exit:** correct query content and negative/error behavior, balanced refs, concurrency and real time/firmware semantics. **Falsification:** synthetic list or enabled-integrity bit taken as real enforced policy; unsupported required provider/class; lifetime leak/use-after-free. **Blocked by:** actual requested class/provider/parameters and G1 for security evidence.

### E07 — Installer, SCM, loader, device transport and teardown

**Depends on:** E00/E02; E03–E06 for actually reached driver behavior. **Addresses:** S01–S03, G4. **Owner/files:** `wine/programs/services/services.c`, `wine/programs/winedevice/device.c`, `wine/dlls/ntoskrnl.exe/ntoskrnl.c`, `wine/dlls/ntdll/unix/file.c`, `wine/server/device.c`, relevant `sechost`/SCM tests.

Retain real existing paths. Add only demonstrated route/semantics gaps. Validate namespace/access, buffered/direct/caller-pointer transport, byte counts, asynchronous event/APC completion, cancellation and unload. Match install/update/remove/service dependencies, failure recovery and mode lifecycle. Report driver-entry completion, service-running and stable communication separately.

**Exit:** native/Wine benign lifecycle/transport comparisons pass; unmodified target reaches genuine local milestones when architecture permits. **Falsification:** correct local status is reported without actual initialization; direct-call loader remains unsupported when used; teardown or pointer-ownership mismatch. **Blocked by:** target parameters/runtime and preceding semantic gaps; G1 still blocks any session guarantee.

### E08 — Crypto, firmware/security providers and authentic platform evidence

**Depends on:** E00/E01, E02 fixture environment; E06 queried state. **Addresses:** S04/S05/S07/S08/S10. **Owner/files:** existing `wine/dlls/bcrypt/`, `wintrust/`, `crypt32/`; `tbs/`, `ncrypt/`, API exports or host integration only if observed and implementable.

Validate actual vendor signature integrity/trust and action-specific WinVerifyTrust behavior. Add algorithm/blob/padding/flags/provider conformance only for established requirements. Test correct invalid-signature and untrusted-chain failures. Implement a genuine TPM/provider backend only if used. Define real reported security state and accepted platform identity; returned trust and platform evidence must correspond to the implemented environment.

**Exit:** crypto/provider/query contracts pass; G1 accepted genuine platform chain is established or explicitly remains external/unresolved. **Falsification:** certificate metadata treated as verified signing, unsupported required algorithm/provider, Linux boot evidence assumed to prove Windows protection. **Blocked by:** parameters and Riot-verifier support for a Linux chain.

### E09 — Conditional event, handle or private-state extension

**Depends on:** independently established S06/S09 requirement; E01/E02, E03/E04/E06. **Owner/files:** `wine/dlls/ntoskrnl.exe/ntoskrnl.c`, private structures; `wine/server/process.c`, `thread.c`, `handle.c`, `device.c`, `protocol.def`; instruction handler only after coherent design.

If runtime requires callbacks, bridge real events and affected operations with safe lifetimes and reentrancy. Server must not synchronously deadlock itself waiting for callbacks that re-enter Wine. Cover both open and duplicate handle paths, actual access changes, image/process/thread lifecycle and unregister during delivery. Prefix notifications remain different from host-wide coverage. Direct private structures or machine state trigger G2.

**Exit:** tests prove actual event delivery/access effects and race/reentrancy safety for evidenced contracts. **Falsification:** success-only registration, one path covered while duplicate remains wrong, server deadlock, or inconsistent private/privileged model. **Blocked by:** demonstrated dependency; do not expand scope solely from anti-cheat speculation.

### E10 — Runtime completeness and target diagnostics

**Depends on:** E00/E01/E02; repeats as lower epics mature. **Addresses:** S03–S09 and unreviewed imports. **Owner/files:** versioned compatibility evidence/test instrumentation, explicit per-interface register; no vendor modifications.

Use normal diagnostics and compatibility observations to record reached exports, dynamic resolutions, query classes, crypto/provider parameters and device contracts. Promote evidence labels only with direct support. Review all remaining imported interfaces, prioritize observed failures and add family conformance tests. Protected metadata does not establish a particular hidden check. Preserve product errors as evidence rather than altering their result.

**Exit:** actual dependencies and parameter contracts are mapped to implementation/test status; remaining unknowns named. **Falsification:** source presence automatically promoted to working behavior, static absence promoted to non-use, or one observed path promoted to exhaustive runtime coverage. **Blocked by:** proprietary behavior and opaque backend decisions may remain unresolved.

### E11 — Complete Proton integration, Riot Client and League session

**Depends on:** G1–G4, E07/E08/E10; fetch complete pinned Proton build dependencies when needed. **Addresses:** S10/S11, G5. **Owner/files:** Proton integration/configuration and demonstrated client/graphics compatibility modules only.

Build the fork with pinned SDK digest/submodules. Validate current client installation/login/update, process architecture/WoW64 requirements, DNS/certificates/secure time and actual network readiness. Test hybrid GPU selection, Vulkan device/extensions, DXVK rendering, windowing, audio and input on this exact Ubuntu/NVIDIA/Mesa stack. Then obtain a genuine accepted anti-cheat session and finish a connected League match, recording versions/errors/stability separately.

**Exit:** complete actual session on Ubuntu, unmodified components, no anti-cheat disconnect; runtime and graphics evidence recorded. **Falsification:** login/rendered window or SERVICE_RUNNING reported as game acceptance, Linux-hosted Windows guest described as native Ubuntu compatibility. **Blocked by:** authentic verifier acceptance and lower semantic/architecture contracts.

### E12 — Updates, reboot, long-running and teardown regression

**Depends on:** E11 initial outcome, E00 manifests. **Addresses:** S12/G6. **Owner/files:** regression fixtures/manifests and documented integration behavior.

Recheck service mode/restart, shutdown/reboot, update/uninstall/reinstall, multi-session start/stop and long-running races/leaks. On each new package compare names/ordinals/hashes and query/platform requirements; run affected conformance tests and genuine gameplay again. Ubuntu kernel/graphics changes create a new baseline rather than silently inheriting old results.

**Exit:** G4/G5 survive repeat runs and scoped changes; failures are reproducible. **Falsification:** one old version's success claimed for a changed package/kernel/driver; leaked callback/object/driver state across sessions. **Blocked by:** any G5 failure or changed external acceptance.

### 8.1 Dependency order and first sprint

```text
E00 --> E01: early platform + address-space/privileged feasibility gates
  \----> E02: minimum generic driver harness
          |----> E03 <---- coordinated design ----> E04
          |                      \----> E05
          |--------------------------------> E06
E00 + E02 + reached semantic families --------> E07
E01 + E02 + E06 ------------------------------> E08
E10: evidence register runs throughout; E09 only if observed
G1 + G2 + E07 + E08 + E10 --------------------> E11 --> E12
```

**First sprint deliverables:** (1) frozen target/reference/mode evidence; (2) minimal Wine test build and actual baseline results; (3) decisive benign process-attachment and execution-context tests; (4) ordinary rundown and data-export conformance patches as the first bounded implementation increments; (5) a written G1/G2 decision before a larger campaign. Do not fetch/build every Proton component merely to learn that a driver contract or required trust identity is incompatible with A1.

There is no evidence-based calendar estimate or percentage completion for actual Vanguard playability. API counts are interface inventory, not outcome progress. Keep generic compatibility improvements independently useful while reporting G4/G5 as unachieved until directly tested.

## 9. Research snapshot validation and handoff state

Completed: official public-package acquisition and static extraction; hashes/versions/encoded imports; independent import-parser agreement; selected pinned-Wine source investigations; primary-source web research; read-only current Ubuntu/build/hardware observations; this engineering document.

Not performed: full Authenticode trust verification, build, conformance-driver execution, installer or Vanguard execution, runtime tracing, firmware changes, platform attestation provisioning, genuine anti-cheat session or gameplay. No compatibility patch, commit, push, PR or deployment is delivered by this document.

Web sources were researched/accessed **9 October 2026** and can change; source-code links use immutable revisions. Host/package/update observations are snapshots. Preserve this baseline when inputs change and record the new experiment and current status in the [implementation register](vanguard-implementation-progress.md), following the [evidence convention](evidence/README.md). It is self-contained for review; raw binaries and scratch reports are not prerequisites for understanding its claims.

## Appendix A. Complete static import inventory

These are the validated encoded imports of the pinned artifacts. An `#ordinal` remains an ordinal; a standard-name hint is a parser annotation, not what the binary encoded. This appendix supplies the unreviewed remainder explicitly. Implemented/export-present interfaces still require observed parameter contracts and conformance review under E10.

### A.1 `vgk.sys` — 129 imports

**`cng.sys` — 9**

```text
BCryptVerifySignature
BCryptFinishHash
BCryptDestroyHash
BCryptImportKeyPair
BCryptCloseAlgorithmProvider
BCryptGetProperty
BCryptHashData
BCryptCreateHash
BCryptOpenAlgorithmProvider
```

**`ntoskrnl.exe` — 119**

```text
strcmp
RtlPcToFileHeader
ExFreePoolWithTag
ZwClose
KeDeregisterBugCheckReasonCallback
KeRegisterBugCheckReasonCallback
KeInitializeGuardedMutex
KeAcquireGuardedMutex
KeReleaseGuardedMutex
ExInitializeRundownProtection
ExAcquireRundownProtection
ExReleaseRundownProtection
ExWaitForRundownProtectionRelease
ZwCreateKey
ZwOpenKey
ZwSetValueKey
wcslen
PsThreadType
ExAllocatePoolWithTag
KeInitializeSpinLock
KeAcquireSpinLockRaiseToDpc
KeReleaseSpinLock
KeNumberProcessors
RtlCompareMemory
ExInitializePushLock
ExAcquirePushLockExclusiveEx
ExReleasePushLockExclusiveEx
strlen
IoFileObjectType
RtlFreeUnicodeString
ZwTerminateProcess
RtlDuplicateUnicodeString
ObfDereferenceObject
__chkstk
ExGetPreviousMode
ProbeForRead
ProbeForWrite
IoGetCurrentProcess
strncpy_s
swprintf_s
_vsnwprintf
wcscpy_s
RtlInitUnicodeString
RtlTimeToTimeFields
KeGetCurrentIrql
KeAreAllApcsDisabled
KeIpiGenericCall
ZwWriteFile
IoCreateFileEx
ZwFlushBuffersFile
KeInitializeApc
KeInsertQueueApc
wcscat_s
IoQueryFileInformation
ZwOpenDirectoryObject
ZwQueryDirectoryObject
strchr
ObReferenceObjectByHandle
_snprintf_s
RtlPrefixUnicodeString
RtlMultiByteToUnicodeN
MmHighestUserAddress
strnlen
strcpy_s
MmGetSystemRoutineAddress
DbgPrintEx
KeInitializeEvent
KeClearEvent
KeSetEvent
KeDelayExecutionThread
KeEnterCriticalRegion
KeLeaveCriticalRegion
KeInitializeTimerEx
KeCancelTimer
KeSetTimerEx
KeWaitForMultipleObjects
KeWaitForSingleObject
KeBugCheckEx
KeQuerySystemTimePrecise
KeQueryActiveProcessorCountEx
KeGetCurrentProcessorNumberEx
ExAllocateCacheAwareRundownProtection
ExFreeCacheAwareRundownProtection
ExAcquireRundownProtectionCacheAwareEx
ExReleaseRundownProtectionCacheAwareEx
ExWaitForRundownProtectionReleaseCacheAware
MmBuildMdlForNonPagedPool
MmMapLockedPagesSpecifyCache
MmUnmapLockedPages
PsCreateSystemThread
PsTerminateSystemThread
IoAllocateMdl
IoFreeMdl
ObfReferenceObject
ObReferenceObjectByPointer
PsGetCurrentProcessId
PsGetCurrentThreadId
KeStackAttachProcess
KeUnstackDetachProcess
ExEventObjectType
KeLowerIrql
KfRaiseIrql
ZwReadFile
ZwQuerySystemInformation
IoQueueWorkItem
__C_specific_handler
ExSystemTimeToLocalTime
KeInitializeMutex
KeReleaseMutex
KeInitializeMutant
KeInitializeDpc
KeInitializeTimer
KeSetTimer
KeAcquireSpinLockAtDpcLevel
KeReleaseSpinLockFromDpcLevel
MmAllocatePagesForMdl
MmFreePagesFromMdl
IoAllocateWorkItem
IoInitializeWorkItem
```

**`HAL.dll` — 1**

```text
KeQueryPerformanceCounter
```

### A.2 `vgc.exe` — 357 imports

**`USER32.dll` — 5**

```text
GetUserObjectInformationW
MessageBoxW
wsprintfW
GetProcessWindowStation
ExitWindowsEx
```

**`WLDAP32.dll` — 16**

```text
#79
#200
#143
#60
#33
#30
#35
#301
#50
#46
#32
#41
#211
#22
#27
#26
```

**`ntdll.dll` — 34**

```text
NtWriteFile
NtQueryInformationFile
NtAllocateVirtualMemory
RtlUnwind
RtlVirtualUnwind
NtUnmapViewOfSection
RtlCaptureContext
RtlAddFunctionTable
NtMapViewOfSection
RtlUnwindEx
NtCreateSection
NtWaitForSingleObject
ZwQuerySystemInformation
NtTerminateProcess
RtlAddVectoredContinueHandler
RtlLookupFunctionEntry
NtCreateEvent
NtFlushBuffersFile
NtFsControlFile
RtlPcToFileHeader
NtFreeVirtualMemory
NtTerminateThread
LdrLoadDll
NtReadFile
NtReadVirtualMemory
RtlDeleteFunctionTable
NtProtectVirtualMemory
NtWriteVirtualMemory
NtQueryVirtualMemory
NtClose
NtDeviceIoControlFile
VerSetConditionMask
NtCreateThreadEx
NtCreateFile
```

**`IPHLPAPI.DLL` — 2**

```text
GetBestRoute
GetIpNetTable
```

**`SHELL32.dll` — 3**

```text
ShellExecuteExW
CommandLineToArgvW
SHGetKnownFolderPath
```

**`WS2_32.dll` — 41**

```text
#21
#19
#14
#18
#17
#1
#112
getaddrinfo
#16
#15
WSACloseEvent
#9
#13
#20
#23
#56
#57
#10
#4
WSAEnumNetworkEvents
#8
WSAEventSelect
WSAResetEvent
#151
WSAWaitForMultipleEvents
#6
#12
#51
#7
#22
WSAIoctl
#115
#3
#111
#52
#11
WSACreateEvent
#116
#2
freeaddrinfo
#55
```

**`ADVAPI32.dll` — 45**

```text
RegQueryValueExW
CreateServiceW
BuildSecurityDescriptorW
FreeSid
ChangeServiceConfigW
RegDeleteKeyValueW
QueryServiceStatus
StartServiceCtrlDispatcherW
SetSecurityDescriptorDacl
SystemFunction036
CryptGenRandom
InitiateShutdownW
SetTokenInformation
SetServiceStatus
DuplicateTokenEx
RegDeleteKeyW
CryptAcquireContextW
LookupPrivilegeValueW
AdjustTokenPrivileges
CryptReleaseContext
RegisterEventSourceW
RegCreateKeyExW
ControlService
SetServiceObjectSecurity
OpenProcessToken
QueryServiceConfigW
RegSetValueExW
CryptAcquireContextA
InitializeSecurityDescriptor
RegOpenKeyExW
CreateProcessAsUserW
AllocateAndInitializeSid
GetTokenInformation
OpenServiceW
RegGetValueW
DeregisterEventSource
OpenSCManagerW
StartServiceW
CloseServiceHandle
RegisterServiceCtrlHandlerExW
EqualSid
RegCloseKey
ReportEventW
QueryServiceObjectSecurity
DeleteService
```

**`VERSION.dll` — 3**

```text
VerQueryValueW
GetFileVersionInfoW
GetFileVersionInfoSizeW
```

**`USERENV.dll` — 2**

```text
CreateEnvironmentBlock
DestroyEnvironmentBlock
```

**`WINTRUST.dll` — 3**

```text
WTHelperProvDataFromStateData
WTHelperGetProvSignerFromChain
WinVerifyTrust
```

**`WTSAPI32.dll` — 4**

```text
WTSSendMessageW
WTSQueryUserToken
WTSEnumerateSessionsW
WTSFreeMemory
```

**`CRYPT32.dll` — 5**

```text
CryptMsgClose
CertCloseStore
CryptQueryObject
CryptMsgGetParam
CertVerifyTimeValidity
```

**`bcrypt.dll` — 1**

```text
BCryptGenRandom
```

**`ole32.dll` — 4**

```text
CoCreateInstance
CoTaskMemFree
CoUninitialize
CoInitializeEx
```

**`KERNEL32.dll` — 189**

```text
GetOEMCP
GetFileSizeEx
SleepEx
TlsSetValue
CreateToolhelp32Snapshot
MoveFileExA
TerminateProcess
GetEnvironmentStringsW
ReadConsoleW
HeapSize
QueryPerformanceCounter
GetModuleHandleW
GetFileAttributesW
FileTimeToSystemTime
AllocConsole
FlsSetValue
LoadLibraryExW
WaitForSingleObjectEx
CloseHandle
UnhandledExceptionFilter
GetStdHandle
GetModuleHandleA
VirtualAlloc
ConnectNamedPipe
UpdateProcThreadAttribute
AcquireSRWLockShared
FreeLibraryAndExitThread
GetCommandLineW
InitializeCriticalSection
Process32NextW
HeapReAlloc
GetExitCodeThread
TlsGetValue
MultiByteToWideChar
FindFirstFileExW
GetEnvironmentVariableW
GlobalMemoryStatusEx
GetExitCodeProcess
IsDebuggerPresent
SetInformationJobObject
VirtualFree
ProcessIdToSessionId
GetEnvironmentVariableA
ExitProcess
SetConsoleMode
CompareStringW
CreateDirectoryW
SystemTimeToFileTime
GetSystemTimeAsFileTime
GetWindowsDirectoryW
SetConsoleTextAttribute
TlsFree
K32GetProcessImageFileNameW
ExitThread
WaitForSingleObject
InitOnceBeginInitialize
GetCurrentDirectoryW
GetLocaleInfoEx
SetPriorityClass
OpenProcess
GetCurrentThreadId
FreeEnvironmentStringsW
ReleaseSRWLockExclusive
FlsGetValue
CreateThread
GetConsoleOutputCP
GetFileInformationByHandleEx
SetStdHandle
CreateFileW
VirtualProtect
SetThreadPriority
DeleteFileW
FindClose
GetStartupInfoW
TryEnterCriticalSection
AssignProcessToJobObject
InterlockedPushEntrySList
FlushFileBuffers
AcquireSRWLockExclusive
GetModuleFileNameA
LeaveCriticalSection
FlsAlloc
HeapQueryInformation
GetConsoleMode
ConvertThreadToFiber
SetEnvironmentVariableW
InitializeSListHead
GetTickCount
TryAcquireSRWLockExclusive
SleepConditionVariableSRW
ResumeThread
GetACP
GetProcAddress
DeleteCriticalSection
GetTickCount64
GetSystemWindowsDirectoryW
GetCommandLineA
FlsFree
DecodePointer
CreateFiber
FormatMessageW
CreateNamedPipeW
DebugBreak
GetCurrentProcessId
ReadFile
SetLastError
GetFinalPathNameByHandleW
MoveFileExW
GetModuleFileNameW
GetUserDefaultLCID
TlsAlloc
SetFilePointer
SetUnhandledExceptionFilter
EnterCriticalSection
ReleaseSRWLockShared
GetDriveTypeW
CopyFileW
LCMapStringW
RaiseException
LCMapStringEx
InitializeProcThreadAttributeList
GetModuleHandleExW
GetSystemFirmwareTable
CreateProcessW
EnumSystemLocalesW
FindFirstFileW
GetLastError
GetCPInfo
FormatMessageA
LoadLibraryW
PeekNamedPipe
GetConsoleScreenBufferInfo
VerifyVersionInfoW
GetTimeFormatW
DisconnectNamedPipe
EncodePointer
HeapFree
OutputDebugStringW
GetStringTypeW
GetLocaleInfoW
CreateEventW
GetFullPathNameW
GetSystemTime
SystemTimeToTzSpecificLocalTime
CreateMutexW
ConvertFiberToThread
Sleep
WakeAllConditionVariable
WTSGetActiveConsoleSessionId
LocalFree
SetEndOfFile
GetFileInformationByHandle
SetFilePointerEx
InitializeCriticalSectionAndSpinCount
GetTimeZoneInformation
GetSystemDirectoryA
CreateEventA
GetDateFormatW
WriteConsoleW
GetFileType
GetCurrentProcess
WideCharToMultiByte
AreFileApisANSI
OpenEventW
DeleteProcThreadAttributeList
DeleteFiber
GetProcessHeap
HeapAlloc
IsValidLocale
FindNextFileW
LoadLibraryA
Process32FirstW
GetSystemTimes
GetFileTime
QueryPerformanceFrequency
SetFileInformationByHandle
ReadConsoleA
IsProcessorFeaturePresent
FreeLibrary
CreateJobObjectW
SetEvent
IsValidCodePage
WriteFile
WaitForMultipleObjects
InitOnceComplete
SetConsoleCtrlHandler
InitializeCriticalSectionEx
SwitchToFiber
GetFileAttributesExW
```
