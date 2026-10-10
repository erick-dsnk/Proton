# A1b private-mapping backing prerequisite

Date: 2026-10-10. Scope: Linux x64 experimental backing for eligible
`MEM_PRIVATE` reservations. This is a mapping-storage prerequisite; it does
not switch Wine's current process address space or implement E05 attachment.

## Observed result

With `WINE_SHARED_PRIVATE_BACKING=1`, the current x64 Wine virtual-memory suite
reported **2,418 tests / 104 todos / 0 failures / 0 skipped**, runner exit 0.
With the option unset, the same focused suite reported **2,340 / 104 / 0 / 0**,
exit 0. The opt-in adds 78 checks. The fixture exercises eligible private
reservation backing, commit and recommit, protection, partial decommit and
release, with failure cleanup. A post-fix injected `mmap` failure reported
`STATUS_NO_MEMORY` (`0xc0000017`) and a retry succeeded; the failure-injection
suite reported **2,428 / 104 / 0 / 0**, exit 0. A separate unrecoverable
decommit-rollback injection terminated its child process as designed; the
parent test run reported **2,424 / 104 / 0 / 0**, exit 0.

A full generic `ntoskrnl.exe` run using the opt-in ntdll/server modules reported
**34,593 tests / 169 todos / 21 failures / 1 skipped**, runner exit 21. Its 37
ordered assertion-failure payloads match the retained baseline's 37 exactly,
including order and multiplicity; there are no missing or extra failure
payloads. The full suite's 21 failures therefore show no diagnostic change
against that baseline. In the E05 attachment block, the actual
`KeStackAttachProcess` and `KeUnstackDetachProcess` routines still log as
stubs. All eight ordinary attached-pointer expectations remain `todo_wine`;
the direct reads fault with `STATUS_ACCESS_VIOLATION`. The current public
attach behavior is unchanged.

The storage path is opt-in and restricted to Linux x64. The wineserver owns a
private backing object and generation metadata for an eligible mapping. The
mapping still reports `MEM_PRIVATE`; the local view retains normal protection
and commit state. Mutations fence the current generation, perform the local
operation, then complete the server transaction; failed rollback paths fail
closed. Foreign mapping acquisition remains unsupported. A separate `/proc`
observation did show distinct memfd-backed views at the same VA in a parent and
child, isolated writes and backing-FD closure at child exit. This verifies
per-process backing lifetime and isolation, not a shared alias or coherent
second-process ordinary pointer access.

The injection history distinguishes intended fail-closed cases from harness
errors. Partial protection rollback and hole-punch failure returned their
expected errors and could retry. Executable-protection failure returned
`STATUS_ACCESS_DENIED`, then succeeded on retry. Fatal protection and the
corrected fatal-decommit rollback case terminated their child processes with
the recorded failure status. The pre-fix `mmap(ENOMEM)` injection exposed an
incorrect `STATUS_UNSUCCESSFUL`; it is excluded as a pass and was rerun after
the source fix, where it returned `STATUS_NO_MEMORY` and retried successfully.
An earlier fatal-decommit harness used the wrong restore protection and did not
inject rollback; only the corrected `PROTON_VM_FAIL_RESTORE_PROT=R` run counts.
The frozen manifest contains each attempt and its classification.

## Inputs and artifacts

| Input | Value |
|---|---|
| Proton revision | `c3547256adf6801cb45299690ea96ce208be097c` |
| Wine revision | `2990a75de24c57ab0a8ff2dc3caab7d075d4df40` |
| SDK | `registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64@sha256:97526b794ce1a9bed5f891084462260b3a02399569f7438a3a57b5a253001db9` |
| Architecture/configuration | x86_64, `--enable-win64` |
| Build scope | Targeted ntdll/server/ntoskrnl test artifacts; not a full Wine or Proton build |
| Scratch directory | `/home/eric/repos/proton-build-vanguard/a1b-attach-backing-recovery-20261010T140415Z` |
| Frozen manifest / SHA-256 | `/home/eric/repos/proton-build-vanguard/a1b-attach-backing-recovery-20261010T140415Z/private-backing-evidence.json` / `bfec5f6301af690a5a34857d6b2b8355a5fde5ec634459751e10f0ed29c3e564` |

Relevant source SHA-256 values at the validated fix are:

| File | SHA-256 |
|---|---|
| `dlls/ntdll/unix/virtual.c` | `d50675d66226460701f9ef00a49908bf02ed54b89ae28884e57cafcf9b5d6d12` |
| `dlls/ntdll/unix/server.c` | `435772dadd2da08a31935a6d8ea4c0e3048821604b56da770d215ef3a3af97a2` |
| `dlls/ntdll/unix/unix_private.h` | `cffeb047dd8a3463db0d06d094018a258d57f057e789e34bd83d267689b7e803` |
| `server/mapping.c` | `2a8f76f632c7e3864023e4edfd1ced50d0d986b135f06ce42a20760054571b88` |
| `server/protocol.def` | `c76074fc2db64d02422d3fd9f01ba6c8f82f04d805c5f2f08d68d5550defd630` |
| `server/process.h` | `8719f32bee746815d77efcfa64d8aa4f71bae78bf98b06b1410886a3d87a3451` |
| `server/request_handlers.h` | `ea5fa5a537e31bfd472be97f43371c819ee3cf1c485817b831676578abd79486` |
| `server/request_trace.h` | `5065cbc96327bd4884c5ee37173426639494b64edcad588fab2d7ec5de2042cd` |
| `include/wine/server_protocol.h` | `bb810941df40431e7a4cbfe89c02c6a109db5e057cadf0b11fdd77c757ba20ae` |

The approved source correction changed `virtual.c` from SHA-256
`b286d94bebda45348384f1e3c3ce7bdc8412f1b24623ab081bdcd10949034459` to the
recorded final hash. It captures `errno` immediately after a failed `mmap`,
returns `STATUS_NO_MEMORY` for `ENOMEM`, and preserves the existing
`errno_to_status()` mapping for other errors. The abort and cleanup path did
not change.

The post-fix focused-run logs are local:

| Run | Artifact | SHA-256 | Exit |
|---|---|---|---:|
| Default-off virtual suite | `/home/eric/repos/proton-build-vanguard/a1b-attach-backing-recovery-20261010T140415Z/postfix-defaultoff-virtual.log` | `588a27297646fe26bc9cf7f31f4ac2cfbab4b579aaecf03644bd21e0fa598aec` | 0 |
| Opt-in virtual suite | `/home/eric/repos/proton-build-vanguard/a1b-attach-backing-recovery-20261010T140415Z/postfix-optin-virtual.log` | `b841b4054551adfb91e0861609d86b6094ec635ea250b75c2d793e913699dbb1` | 0 |
| ENOMEM injection and retry | `/home/eric/repos/proton-build-vanguard/a1b-attach-backing-recovery-20261010T140415Z/postfix-map-failure-validation.log` | `74973ade3a02b314f24769a5736c4ca53cca1d617a3020b0fe7b3b7046d874e6` | 0 |
| Fatal rollback cleanup | `/home/eric/repos/proton-build-vanguard/a1b-attach-backing-recovery-20261010T140415Z/inject-fatal-decommit-fixed.validation.log` | `f20fa848586589a648c0abcbf4a25f53252b2bf12687b32d6926549b5c7472ba` | 0 |
| E05 and full generic suite | `/home/eric/repos/proton-build-vanguard/a1b-attach-backing-recovery-20261010T140415Z/postfix-e05-optin.log` | `6414802d416b7fa89feaadb5281206c89931526d706158271b65dbfeca599336` | 21 |
| Targeted E05 test build | `/home/eric/repos/proton-build-vanguard/a1b-attach-backing-recovery-20261010T140415Z/postfix-e05-target-build.log` | `6d536a7c6e0839a0ae9f211c1ab6b024ac345ffcf37dca9bbf9fe51b50024dac` | 0 |
| GCC full-suite baseline | `/home/eric/repos/proton-build-vanguard/a1b-finally-gcc-20261010T124212Z/final-source-strict.log` | `3557d41f8992ef9b140a3daab2e57f3ff5a9251e7d996f78d0a525eb741b6504` | 21 |

Runtime artifacts: `ntdll.so` `a1a47247ef2ec2008c26da2d5aef6324799b1db245fa0daaf3b7a935771c9c4b`, wineserver `34786b32962cf532767edd91835e21893a8d50cb4e7b43b9ef794a554f26bf5e`, launcher `f4882de048f35d8bcba4de36ac857bf99ae24554013227037e672d76a9e1728f`, and `ntoskrnl.exe_test.exe` `1519e9ae2a41d3e264fd917f347aec9c6b6a11abe40af3ceae93724c67e08d05`.

The E05 suite's `ntoskrnl.exe` runtime module was retained at baseline SHA-256
`718e7adb5accf155445c60dfb9426274ed6a232a5b4943d5a7577b25b03e85b1`; the
updated benign fixture PE was used to reach the attachment test. The candidate
and baseline have identical ordered `Test failed` payloads, 37/37 with no
missing or extra entries. The explicit normalizer yields 18 distinct semantic
templates; this record reports the verified ordered comparison rather than
forcing a separate 25-message grouping.

The recoverable E05 test build command inside the pinned SDK was
`make -j1 V=1 -C dlls/ntoskrnl.exe/tests`. The E05 runtime command was:

```sh
export WINEPREFIX=/build/prefix-postfix-optin WINE_SHARED_PRIVATE_BACKING=1
timeout --kill-after=15s 300s xvfb-run -a /src/tools/runtest -v -T /build -M ntoskrnl.exe -p /build/dlls/ntoskrnl.exe/tests/x86_64-windows/ntoskrnl.exe_test.exe ntoskrnl
```

It used uid `1000:1000`, the pinned SDK, one CPU and 4 GiB memory. The complete
Docker argv and failure-injection chronology are in the frozen manifest above.
The earlier focused virtual-suite Docker argv was not retained and is not
reconstructed here.

## Limits and next gate

The full Wine build attempt in the earlier scratch failed in the unrelated
`cryptxml` archive step (`ranlib` could not copy `libcryptxml.a`). The recorded
runtime uses rebuilt targeted modules and retained Wine components; it is not
a complete fresh Wine build. The full E05 run has an exact baseline
comparison; the broader private-backing lifecycle matrix, foreign-view
revocation and cross-process aliases remain unvalidated.

This storage experiment is not the process executor or the kernel arena.
Those two prerequisites were tested separately; their combination has not
been validated. Next, complete the failure-injection and diagnostic-baseline
record, then establish a managed loader layout and a real executor host-RTL
boot. Only after those gates should live foreign-view leases and actual E05
pointer behavior be attempted. Vanguard acceptance and gameplay remain
separate, unresolved gates.
