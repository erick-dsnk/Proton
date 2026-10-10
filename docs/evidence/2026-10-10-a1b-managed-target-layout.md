# A1b managed TARGET address-space layout

Date: 2026-10-10. Scope: an opt-in, Linux AMD64 managed-TARGET address-space
admission mode in Wine's preloader/Unix ntdll. This gives a process a
collision-checked guest range and a truthful reduced user-address limit. It is
not an executor, shared kernel arena, process attach implementation, or
Vanguard compatibility result.

## Contract and result

The only admitted contract is
`WINE_MANAGED_LAYOUT=v1:target:400000000000`, with guest addresses
`[0x10000, 0x400000000000)` and highest user address `0x3fffffffffff`.
Admission is Linux AMD64 only. Executor role is explicitly unsupported. The
preloader reserves the guest span with strict non-replacing semantics, checks
PIE/ELF placement, and exports an admission descriptor. Unix ntdll requires
that descriptor to match the setting, copies the bounds into process state,
and keeps enforcement active for that process even after the environment
setting is removed. Managed VM metadata remains native-side. Wine's PE image
and guest allocation paths enforce the guest ceiling.

The target's Windows TEB/PEB and explicitly allocated Wine syscall/native
thread stacks may remain guest-side; this mode does not make them exportable
executor state. A benign native fixture observed the preloader, ELF, heap and
automatic native pthread stack outside the guest span. The design does not
claim all stacks are outside the span.

The final preloader admission matrix passed **14/14** malformed, unsupported,
descriptor, architecture/layout and ELF rejection cases. The non-destructive
collision fixture got `EEXIST` and verified both occupied mappings and a
64-byte sentinel were unchanged. The corrected focused Wine fixture reported
**3 assertions** in the preloader child and **29 assertions** in the Wine
parent, with no failures (runner exit 0). It covered final-page/crossing-bound
allocation, persistent guest coverage, descriptor admission, and rejection
paths. The default-off virtual suite reported **2,338 / 104 / 0 / 0**, exit 0;
this is recorded as observed and not forced to match the earlier separate
private-backing suite's 2,340 assertions.

The final fault-injection run reported **3 assertions / 0 failures** in the
preloader child and **39 / 0 / 0 / 0** in the parent (tests / todos / failures /
skips), exit 0. The injector observed eight
reserved-mapping `ENOMEM` markers and one child-environment `ENOMEM` marker.
The parent asserted `STATUS_NO_MEMORY`, a null output address and unchanged
size, then disabled injection and successfully allocated, wrote and released
the same bounded size. Injected child `setenv` failure prevented the child
launch; the current Wine grandchild transport exposed `ERROR_WAIT_1` (731) to
the caller. That observed transport is experimental Wine behavior, not a
Windows conformance claim.

A benign fake legacy shared-object presentation reached the managed guard
warning and did not run its constructor sentinel. No actual legacy `.so` was
loaded. An earlier fixture accidentally presented a regular PE module and
therefore did not test the guard; only the corrected Winebuild placeholder
presentation counts.

## Combined E05 run

The same assembled x64 runtime ran the generic E05 suite with the managed
TARGET descriptor observed in actual driver hosts. The default-off run
reported **34,593 tests / 169 todos / 21 failures / 1 skipped**. With backing,
arena and managed-layout options enabled, it reported **34,942 / 169 / 21 /
1**. A final monitored opt-in rerun had the same totals. Each run exited 21.
Six actual `winedevice.exe` processes were inspected using read-only `/proc`
memory access inside the isolated container, with `CAP_SYS_PTRACE` restricted
to that observer; Wine and test execution retained uid/gid 1000. All six had
the expected descriptor (`TARGET`, start `0x10000`, end
`0x400000000000`), `managed_target=1`, `user_space_limit` equal to the guest
end, continuous guest-span coverage, and all three experiment flags.

The default-off, opt-in and two monitored opt-in full-suite runs each had the
same 37 failure diagnostic lines and 25 unique diagnostics as the retained GCC
baseline after stripping only source-file/line prefixes. There were no
baseline-only or candidate-only diagnostics. The one skip is the existing GCC
`__try`/`__finally` limitation. E05's eight attachment expectations remain
`todo_wine`; direct attached-memory probes still fault and
`KeStackAttachProcess`/`KeUnstackDetachProcess` remain stubs.

## Build identity and evidence

| Input | Value |
|---|---|
| Proton revision | `c3547256adf6801cb45299690ea96ce208be097c` |
| Wine revision | `2990a75de24c57ab0a8ff2dc3caab7d075d4df40` |
| SDK | `registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64@sha256:97526b794ce1a9bed5f891084462260b3a02399569f7438a3a57b5a253001db9` |
| Architecture/configuration | Linux AMD64, `--enable-win64`; `config.status` SHA-256 `109eddd17d099f8aed74ab7dcb3ff4ff50c977f6e8ae9ce79e910bf336ff64f5` |
| Frozen runtime manifest | `/home/eric/repos/proton-build-vanguard/a1b-managed-layout-20261010T/managed-runtime-evidence.json`, SHA-256 `1f3f8c35c21af9a7979414279e746b51e9ddc8669d74c3f9c66382d13b0e0656` |
| Exact E05 command metadata | `/home/eric/repos/proton-build-vanguard/a1b-managed-layout-20261010T/e05-observed-final-command.json`, SHA-256 `2bdd334ea8cdae65240b79ffd90290f11d2700a905d44da2ba292d596be01e3f` |

The manifest has the complete source/artifact inventory, exact commands,
configuration and logs, failure chronology, and admission/baseline JSON. Key
final source SHA-256 values are:

| File | SHA-256 |
|---|---|
| `include/wine/managed_layout.h` | `05ef9b870aba6ad60439c4f07f8408cd18415d0595686e04b3290ba56822b045` |
| `loader/preloader.c` | `ecae6ce60eab5e447a0c50e0eafefa6b47c034e4dcd810cd9b311e589a668187` |
| `loader/main.c` | `8f1334a9cefbc04a6d5f8d7d29c192edb044b71c31f6c5f2b650fa357ff6df3b` |
| `dlls/ntdll/unix/loader.c` | `318134e7432e0def957d09d1249b6a411db5c53f696dbb7bddaf2a14abf5e600` |
| `dlls/ntdll/unix/virtual.c` | `634f5f70d7df90688e4a725bd2e315fcb9ec23118b0a5382fadf5ce4d0074c2e` |
| `loader/tests/managed-layout.c` | `86378e4f347752d03fd0ce6aa68d6515a98583fb1e0f3d57dabf6f345b61cb95` |
| `loader/tests/managed-layout-inject.c` | `e1ec0e222df17abfec0c99a7e8a593a31a787ae5cac0135361d6639b7ed1d0a7` |
| `dlls/ntdll/tests/virtual.c` | `942efde5673968df66125e23d8b9187aea324f9c5d473f8ef0fcee6ff001ffdc` |

All eight bounded target builds eventually exited 0; build attempts 1 and 2
exited 2 before compilation due to missing generated inputs and are retained
in the manifest. The final bounded artifacts were compiled against a copied,
compatible build tree with generated-input identity checked. Existing PE
ntdll, wineserver and unrelated runtime artifacts were retained; arena,
services, kernel and driver artifacts came from the separately validated
runtime. No complete current-source Wine build or full Proton build is
claimed. The source review cleared the final native fixture, injection
fixture, PE virtual fixture, and the AMD64 multiarch selector change; runtime
validation remains AMD64-only.

Earlier invalid fixture attempts are preserved in the manifest and excluded
from the passing counts: the initial endpoint overlapped the loaded ntdll
image, one legacy presentation did not reach the guard, an admission matrix
expected incorrect diagnostic strings, and the first injection did not keep
the ENOMEM injector active through the full allocation search. Each was
corrected and the final corresponding run is identified above.

## Remaining boundary

This implements a bounded **TARGET layout only**. It does not reserve
executor-private RTL/TEB/PEB/heap/stack slots, start a separate executor, boot
canonical host ntdll, import or initialize the Vanguard driver in a canonical
shared kernel image, create cross-process arena aliases, or implement ordinary
Wine attach semantics. A managed TARGET does not prove an executor can run with
the host runtime excluded from its guest range. Native Windows, i386 and
multiarch runtime rejection remain unvalidated. The next separate gate is a
reviewed host-runtime boot in the future executor role; only after that can
the project test live aliases and ordinary E05 pointer behavior. Vanguard
acceptance and gameplay remain unproven.
