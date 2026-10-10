# A1b private-backing matrix and live-view experiment

Date: 2026-10-10. Scope: bounded Linux x86_64 Wine experiments for the A1b
private-backing prerequisite and the follow-on managed TARGET to EXECUTOR live
view. This is generic local evidence; it does not establish Vanguard
acceptance or gameplay.

## Phase 1: private-backing matrix

**Observed:** the completed matrix exercises ordinary compiled pointer reads,
writes, and instruction execution across private allocation lifetime and
protection changes. It covers full-span zeroing on first commit, recommit, and
exact-address reuse; RW access; NX and RX behavior; denied writes; execute
permission removal; read-only and no-access faults; decommit from no-access
and RW states; neighboring-page preservation; release and address reuse; and
parent access after a same-address child exits. Remote helpers set up or
inspect fixture state; they do not count as alias proof.

All nine final runs exited 0 with 104 existing todos, zero failures, and zero
skips. The same PE fixture ran against the candidate in default-off and
opt-in modes and against the unmodified Wine baseline:

| Run | Result | Log SHA-256 |
|---|---:|---|
| Current runtime, default off | 2,423 / 104 / 0 / 0 | `599179abb69b62f33c59230194101a784b12d285e73911b00165e8be26d8a63f` |
| Current runtime, backing enabled | 2,503 / 104 / 0 / 0 | `43be3323cc449e5e16aea07da086242c2d3e87142c7bdec9554328b1ec7fa228` |
| Unmodified Wine baseline, default off | 2,423 / 104 / 0 / 0 | `c2e2174604f9cf36baf42d5b9d126f4d5be2583ecdeb09e7dd412d65eb3aaff6` |
| Inject backing mmap failure | 2,513 / 104 / 0 / 0 | `955f0fb3fdab0b1cf49f43cfcfc31581543c7509cac3f2f38decfd68e7f4272b` |
| Inject executable mprotect failure | 2,517 / 104 / 0 / 0 | `18f5570aafb1532ee78fd8998712334fd05a608a8d5787e9af424b511b0d2703` |
| Inject partial protection failure | 2,527 / 104 / 0 / 0 | `62722e86dc8977fd06447c3f6a0885315b3950e4e532769af9db123bc36cb851` |
| Inject decommit hole-punch failure | 2,521 / 104 / 0 / 0 | `fa868c0b103b60210c08a2738f596cb4128f7c73ddea195557649dc587586a5e` |
| Inject fatal protection rollback | 2,509 / 104 / 0 / 0 | `edf09ac653c0328257047626ddf1a7d3e99d6ee2a927f75623e5baea983e0295` |
| Inject fatal decommit rollback | 2,509 / 104 / 0 / 0 | `063e8a41baa4044b0571447ac43252c2c66759b31aac27c4af2125f598dd1a89` |

In that table, counts are `executed / todo / failures / skipped`. The mapping
failure returned `STATUS_NO_MEMORY` (`0xc0000017`) and retry passed. Executable
and partial-protection failures returned `STATUS_ACCESS_DENIED` (`0xc0000022`)
and recovered on retry. The hole-punch failure returned
`STATUS_NOT_SUPPORTED` (`0xc00000bb`), then retry/recommit passed. The fatal
protection and decommit rollback cases observed both primary and rollback
injection markers and terminated their child with `0xc0000001`, as designed.
No injected run reported an unexpected failure.

The default-off candidate and unmodified baseline used the same PE, had the
same parent summary, and had equal ordered unexpected-failure payloads. The
candidate runtime was copied into a fresh isolated scratch from the checked
managed-EXECUTOR source/object tree; the changed PE fixture was rebuilt. This
was an assembled Wine-only runtime, not a fresh full Wine or Proton build.

Inputs and provenance:

| Input | Value |
|---|---|
| Proton source revision for the VM matrix run | `c3547256adf6801cb45299690ea96ce208be097c` |
| Parent base for protocol and owner-lookup runs | `1b0a3946a44630f0601c7c60a8cd308758477458` |
| Wine component source base | `084fc093b4eaec9f66a942f5d902496318762abb` |
| Unmodified Wine baseline | `e60892cc2398b0a83c332a2078c7b85e47bdb42b` |
| Component state for integrated runtime | The experiment ran as a 13-file uncommitted delta on Wine `084fc093`. The same runtime source bytes are now published in Wine [`d262e37075efc5ce8c7be8e85a547fbb6c03ad3d`](https://github.com/erick-dsnk/wine/commit/d262e37075efc5ce8c7be8e85a547fbb6c03ad3d) on `vanguard-a1b-private-backing`, and the current Proton gitlink references that commit. Per-file tested hashes remain in the frozen `runtime-sources-rebuild2.json`, SHA-256 `84da7024702a377c09630c7d50f7d55f2fc81cb919168131c40e1efa87a2aa4e`. Publication adds no new runtime result. |
| SDK | `registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64@sha256:97526b794ce1a9bed5f891084462260b3a02399569f7438a3a57b5a253001db9` |
| Architecture/configuration | x86_64, `--enable-win64` |
| Scratch directory | `/home/eric/repos/proton-build-vanguard/a1b-private-matrix-20261010T1925Z` |
| Final matrix fixture source | `virtual-observer-final.c`, SHA-256 `4fa7dbca40ff33e0154910c01417774cd03cc5964ae61c30a882054a6dda33d6` |
| Final test PE | SHA-256 `e70bb17563d56bd31b677354e3890cb4aad82f2f5cb2a14e65923b37a6abc1cc` |
| Runtime `ntdll.so` | SHA-256 `9277e1c801420eb5e57fb6273e695129cd5ec494f65a12a0f02a7515cb72e0e0` |
| Runtime wineserver | SHA-256 `34786b32962cf532767edd91835e21893a8d50cb4e7b43b9ef794a554f26bf5e` |
| Machine-readable run manifest | `private-backing-vm-matrix-evidence.json`, SHA-256 `86593254bda16152571bf0bc518e816ca09f6f3257f9e0b943eaf1f0f095a713` |

Each normal run used the pinned SDK in Docker, one CPU, 4 GiB, uid `1000:1000`,
a distinct Wine prefix, `WINEARCH=win64`, disabled optional Mono/HTML
installers, and `WINEDEBUG=-all`. The exact wrapper command inside the SDK
was:

```sh
timeout --kill-after=15s 240s xvfb-run -a /src/tools/runtest -v -T /build -M ntdll.dll -p /build/dlls/ntdll/tests/x86_64-windows/ntdll_test.exe virtual
```

The opt-in runs additionally set `WINE_SHARED_PRIVATE_BACKING=1`. Injection
runs additionally set the relevant `PROTON_VM_FAIL_*` variables and loaded
`/matrix/failinject.so` with `LD_PRELOAD`; exact per-run Docker argv and
injection values are retained in the manifest.

The manifest records full Docker argv, per-run exit status and logs, source and
binary hashes, and the baseline comparison. The manifest and logs remain in
the local scratch directory; the absolute paths identify local provenance and
are not portable download links. The final default-off observer run changed
only fixture observation timing; the prior six injection runs use the
pre-observer-guard fixture, whose source and PE hashes are also in the
manifest.

**Limit:** this matrix validates private mapping behavior in one Wine x86_64
runtime and its recorded default-off baseline. It does not test i386, native
Windows, foreign-process mapping leases, revocation of a live foreign view,
the E05 attachment path, or a full Proton build.

The backing identity and owner lookup checks were then extended in separate
fixtures. The native protocol fixture reported 84 parent plus 6 child checks
with the option off and on, and 8 checks for injected backing creation failure;
all three runs exited 0 without failures. That fixture uses synthetic server
metadata, so it does not prove that Wine VM allocation publishes real mapping
identity.

The phase-1 `/proc` FD observer reported 2,453 / 104 / 0 / 0 with backing off
and 2,503 / 104 / 0 / 0 with backing on; both exited 0. It observed live
same-address `0xb10000` mappings: anonymous private mappings when off and
distinct memfd-backed mappings (device 1, inodes 48066 and 48067) when on. The
server held both backing objects while both mappings were resident, closed
the child's backing after child exit while the parent mapping remained, and
closed both after final release/exit. Its creation-failure observer confirmed
that injected ENOSPC affected both candidate backing objects and neither
remained in the server afterward; 8 checks, 0 failures, exit 0. Actual byte
values were checked by PE instructions because same-uid `/proc/<pid>/mem`
access was denied to the external observer.

**Provenance boundary:** these observer v5 results ran on the phase-1 component
snapshot at Wine `084fc093`, before the later integrated server owner-index and
process-exit changes. A current rebuild2 opt-in rerun then passed **2,503 / 104
todos / 0 failures / 0 skipped**, runner exit 0. It observed parent/child
same-address `rw-s` mappings at `0x00b10000`, distinct device-1 memfd inodes
60732 and 60733, server ownership of both during residency, child backing
closure after child exit, and closure of both after fixture completion. Actual
bytes were asserted by the PE fixture; the observer read maps and FD inventory,
not `/proc/mem`.

The current-runtime observer manifest
`observer-current-on-evidence.json` has SHA-256
`946a0666d921c9e5036b824a4219314e4814ea25c1784a15be60493340c0fea1`; its
readable summary hash is `11ce6bc77f1431547bb27d1e7e7daa8c9109a903cbacff0504415bb750604ace`.
Its observer log SHA-256 is
`7aa2bb9957346c60fe945af2f0ba0117e70e7bb73546217ff6c57d9c55282a6c`, and the
three-snapshot inventory SHA-256 is
`1a5cd8ded16fd0952ccf56f646e19fe72e682cb973e64a1543195363154bfd32`. This
confirms the current integrated source's ordinary private-backing FD lifetime
at the observed checkpoints.

Finally, the integrated real-owner lookup fixture passed with the option off
(87 parent plus 6 child checks) and on (118 parent plus 6 child checks), both
with zero failures and exit 0. It checked an actual eligible allocation's
base, extent, identity and page flags, stale requests, generation and
protection/decommit/recommit updates, recommit zeroing, release lookup
returning `NOT_FOUND`, and fresh identity after exact-address reuse.

The protocol, real-owner lookup, corrected fatal-decommit, and current-runtime
FD-observer fixtures passed for their recorded cases. Together they close the
documented phase-1 private-backing matrix for the bounded Wine AMD64 source
snapshot. None of these fixtures exercise an ordinary EXECUTOR pointer through
a foreign TARGET view or prove revocation while such a pointer is active.

The frozen combined protocol/FD manifest
`private-backing-protocol-and-fd-evidence.json` (SHA-256
`181e75c1756bf71abbd1d3a112487f3b170d9928d0ad658d30213dbebef54c34`) records
the exact commands, logs, source and artifact hashes, observation snapshots,
and excluded attempts. Its readable report is
`private-backing-protocol-and-fd-report.md` (SHA-256
`4c4196aa72350bf044398703b918b50ce937eae3364c438b7288ef34c0707579`). Both
are retained in the local scratch directory, not distributed with the
repository. The targeted rebuild used for the real-owner lookup passed with
exit 0; its build log SHA-256 is
`67b495b45fb29578b8df6449d7e802b3e85f4082d6d15dc45ba742bdf7440d0c`. The
real-owner fixture PE SHA-256 is
`b0b86eebbdb8083dac4c00f9ddee4b1399a51cfbaec27fcfa6aea9d9dd705902`; exact
per-run logs are listed in the frozen manifest.

### Final-runtime fatal-decommit harness diagnosis

The matrix was rerun against the selected integrated rebuild2 runtime before
finalizing this record. Default-off and the unmodified baseline both passed
2,423 / 104 todos / 0 failures / 0 skipped; opt-in passed 2,503 / 104 / 0 / 0.
The first fatal-decommit rerun omitted `PROTON_VM_FAIL_RESTORE_PROT=R`. Since
the fixture makes the page read-only, the runtime correctly restored
`PROT_READ`, while the default shim matched RW. The two resulting runs reported
2,509 tests / 104 todos / 1 failure / 0 skipped and runner exit 1, but did not
inject the rollback failure. An observer-only diagnostic reproduced this
command mismatch: the backing FD and target VMA matched device `0:1`, inode
59040; rollback requested `PROT_READ` against a configured RW injection, no
rollback marker fired, and the child exited normally.

Adding only the missing `PROTON_VM_FAIL_RESTORE_PROT=R` setting passed: the
actual `PROT_READ` rollback injection fired, the child exited
`STATUS_UNSUCCESSFUL` (`0xc0000001`), and the suite reported 2,509 tests / 104
todos / 0 failures / 0 skipped, runner exit 0. The matching backing FD and VMA
were device `0:1`, inode 59867. No runtime source change or rebuild was needed.
The two earlier attempts remain preserved as harness-parameter failures, not
runtime defects. The final scoped matrix therefore passes with the corrected
command.

The diagnosis summary is retained locally at
`private-decommit-diagnosis/decommit-diagnosis-summary.md` (SHA-256
`cb4bf74be9a591fddb0ae13266f1b273916b9540644236e173a9a5fa9d2faa93`); its
machine-readable manifest SHA-256 is
`bb3fe388b43f720e04f4551622820ca11fc34f72af16263b1f6d174b19d85d40`. It
records the missing-setting reproduction, corrected run, commands, markers,
source hashes and runtime artifact hashes. The earlier two-attempt regression
manifest remains retained separately for provenance.

## Phase 2: managed TARGET to EXECUTOR live view

**Status:** the scoped runtime source has two successful targeted rebuilds, a
source review, an EXECUTOR descriptor/FD regression, unchanged TARGET-v1
regression, and compile-time 32-bit and 64-bit ABI layout checks. The 32-bit
check compiles declarations only; it is not i386 runtime evidence. These are
prerequisites, not the live-view proof.

The helper-based ordinary-pointer fixture did not reach its alias assertions.
Two attempts ended before alias operations: one with helper `LoadLibrary`
error 126, and a subsequent attempt with the same helper load error plus a
storage-prefix setup failure. A later fixture execution was stopped by the
automated safety filter after it flagged a possible cybersecurity risk. No
successful live-view run was observed, and the work was not rerouted through
another tool or helper. The ordinary pointer read/write, acknowledgement,
consumer/target exit, collision, and active-access revocation cases therefore
remain unproven.

The pass condition remains an ordinary executor pointer load and store against
the same live TARGET mapping at its original virtual address, with coherent
writes in both directions and deterministic revocation. A copy, snapshot, or
remote read/write helper does not pass. Isolation, permissions, generation,
target exit, and default-off behavior must remain explicit in the final test
record. The scoped design covers a cooperative Linux AMD64 managed cohort and
a complete committed readable, non-executable private extent. It does not
claim protection against arbitrary native `MAP_FIXED`, `munmap`, or `mremap`
calls that bypass the managed VM lock within the admitted guest range. See the
[attachment backing design](2026-10-10-a1b-attach-backing-design.md) for its
stop conditions and the complete E05 execution chain.

The live-view proof is incomplete and A1b is not complete. Even if this proof
later passes, it establishes one memory primitive only.
The public `KeStackAttachProcess` / `KeUnstackDetachProcess` routines and all
eight E05 attachment `todo_wine` expectations remain unchanged until the
complete execution chain and E05 behavior pass. Native Windows reference,
i386, Vanguard call-path relevance, genuine platform acceptance, accepted
sessions, and gameplay remain separate unresolved gates.

## Publication provenance (2026-10-10)

The component implementation and seven fixture sources are published in Wine
[`d262e37075efc5ce8c7be8e85a547fbb6c03ad3d`](https://github.com/erick-dsnk/wine/commit/d262e37075efc5ce8c7be8e85a547fbb6c03ad3d)
on `vanguard-a1b-private-backing`. A fresh remote clone retrieved that exact
commit. All 22 changed source files matched the local committed bytes, and all
13 runtime source files matched the tested hashes in
`runtime-sources-rebuild2.json`. The parent gitlink was advanced only after this
retrievability check. The original manifests retain their pre-commit source
identity and artifact hashes; they were not rewritten as post-publication runs.

The verification used a new repository without local alternates:

```sh
git clone --depth 1 --filter=blob:none --single-branch \
  --branch vanguard-a1b-private-backing --no-checkout \
  https://github.com/erick-dsnk/wine.git /tmp/a1b-wine-publication-d262e370
git -C /tmp/a1b-wine-publication-d262e370 rev-parse HEAD
```

Both commands exited 0. A Python SHA-256 comparison read each changed file via
`git show HEAD:<path>` in the fresh clone and compared it with the committed
workspace source; the 13 runtime files were also compared with the frozen
manifest. All comparisons passed. This publishes the source and fixture
scaffolding; it does not complete the live-view proof, broaden the tested
cohort, implement public attach/detach, or establish Vanguard acceptance or
gameplay.
