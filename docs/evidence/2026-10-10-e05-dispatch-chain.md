# 2026-10-10 — E05 buffered dispatch attachment-chain experiment

Status: completed for the bounded opt-in single-thread synchronous scope.
Claim label: observed across three strict x64 Wine runs, with an exact
default-off diagnostic comparison. Concurrency and wider compatibility gates
remain open. No Vanguard binary or target session is used.

## Question and scope

Can the managed EXECUTOR run the instrumented E05 test driver through the
normal buffered-IOCTL dispatch path while changing only its
declared read-only private user-memory view across
caller → A → B → A → caller? Ordinary compiler-generated pointer loads at the
same virtual address must observe each process's distinct bytes, including an
address mapped only in a target. The driver's code and globals, IRP and buffers,
pool allocations, stack locals, process references, and `KAPC_STATE` must stay
valid across the complete nested sequence.

This tests a bounded executor hypothesis. It does not implement or demonstrate
general Wine `KeStackAttachProcess`/`KeUnstackDetachProcess` semantics. It also
does not establish Vanguard call-path relevance, local Vanguard operation,
platform acceptance, an accepted session, or gameplay. The original E05
load/attach/detach sequence is preserved, with strict instrumentation and
compiler-generated pointer reads added for this experiment.

The experiment is scoped to one logical driver thread and two explicitly declared
64 KiB read-only private memory extents per process: a common mapping and a
target-only mapping. The fixture establishes distinct
bytes at a shared VA and a target-only mapping, verify direct ordinary loads in
each view, and check creator process/thread identity and kernel-owned sentinels
before, during, and after nested attach/detach. `PsGetCurrentProcessId()` should
retain the dispatch creator PID; `PsGetProcessId(PsGetCurrentProcess())` should
track caller/A/B/A/caller. Check `KAPC_STATE` contents while each state is
active, and separately check its canary/storage lifetime after detach. Keep
remote-copy helpers out of the
assertion path: they cannot establish ordinary pointer access in the running
driver continuation.

The current strict fixture uses compiler-generated `volatile BYTE *` loads for
the common mapping at all five phases and for the target-only mapping at A/B/A;
the target-only absence at caller is checked with the guarded-read path. Retain
the generated-load disassembly with the final evidence. The separate uncaught
fault request must record the attached PID at the injection point and verify
that it is A, require the wrapper result to map to `ERROR_NOACCESS` with zero
returned bytes, then run the healthy full chain and recheck identities.

Fault cleanup is a separate subtest: one fixture catches its own fault and
explicitly detaches, while another lets an attached driver fault escape to the
dispatch wrapper. The latter must be followed by a healthy complete five-phase
IOCTL to show the wrapper restored/released state. These outcomes must be
reported separately; explicit driver detach alone does not prove wrapper
cleanup.

## Implementation under test

The experiment uses one physical real `winedevice` managed EXECUTOR
with declared read-only private mappings. Loader/runtime selection is opt-in:

```text
WINE_MANAGED_LAYOUT=v1:target:400000000000
WINE_SHARED_PRIVATE_BACKING=1
WINE_SHARED_KERNEL_MEMORY=1
WINE_EXPERIMENTAL_DRIVER_EXECUTOR=1
WINE_EXPERIMENTAL_ATTACH_RANGES=23000000:10000,24000000:10000
```

The run uses this managed TARGET layout, private backing, kernel memory, and
executor selection through SCM environment propagation. SCM starts the real
`winedevice.exe` managed EXECUTOR, and the test reaches buffered IOCTL
`0x22203c` through `IoCallDriver`. The prototype is opt-in and scoped to this
synchronous serial path; it does not establish general attach behavior.

## Inputs

| Input | Exact value |
|---|---|
| Proton source revision | `c0a06aa7c4d5258413acf4edf5c179027e6fd1f0`; parent worktree has documentation edits |
| Wine component base revision | `9c389578ccc8c7111047dbb826debc102a8ddf26`; working tree has executor/runtime/fixture changes across `ntdll/unix/loader.c`, `ntoskrnl.exe/ntoskrnl.c`, `ntoskrnl.exe/tests/{driver.c,driver.h,ntoskrnl.c}`, and `programs/services/services.c` |
| Other relevant gitlinks / harness revision | Wine base `9c389578ccc8c7111047dbb826debc102a8ddf26`; results manifest below |
| SDK tag and digest / toolchain | SteamRT4 SDK `registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64@sha256:97526b794ce1a9bed5f891084462260b3a02399569f7438a3a57b5a253001db9`; configured x64 Wine (`--enable-win64`) |
| Host OS, kernel, architecture | Ubuntu 24.04.4 LTS, kernel `7.0.0-38-generic`, x86_64 host; x64 Wine test build |
| Test driver / harness build and architecture | compiled x64 Wine test; test executable SHA256 `22e421c4d90364f51984a1c99acc5b94a95782ab6c8cb3d236d4d894b54eef58`; `driver.dll` SHA256 `f69b4cc828297406d2e23192ec9bbcd28bb45add1eb7cffe8258ef243948ff23` |
| Runtime options | `WINE_MANAGED_LAYOUT=v1:target:400000000000`; `WINE_SHARED_PRIVATE_BACKING=1`; `WINE_SHARED_KERNEL_MEMORY=1`; `WINE_EXPERIMENTAL_DRIVER_EXECUTOR=1`; `WINE_EXPERIMENTAL_ATTACH_RANGES=23000000:10000,24000000:10000`; `WINEARCH=win64`; `WINEDLLOVERRIDES=mscoree,mshtml=` |
| Windows reference | not run |

## Commands and artifacts

The authoritative results manifest is retained at
`/home/eric/repos/proton-build-vanguard/e05-dispatch-20261010T203000Z/evidence/dispatch-harness-results.json`
(SHA256 `8bf31a20d95fc00df5e3a751594c38b9202728c9959c29fb7448de614badec6b`).
It records the exact environment, per-run prefixes, commands, exit statuses,
source/artifact hashes, strict logs and default-off comparison. Raw logs and
binary artifacts remain in the scratch evidence directory and are not
published here. Do not treat the separate stock-`winedevice` high-relocation
smoke check as dispatch-chain evidence; it only covers loader bootstrap.

```bash
timeout --kill-after=15s 300s xvfb-run -a \
  /src/tools/runtest -v -T /build -M ntoskrnl.exe \
  -p /build/dlls/ntoskrnl.exe/tests/x86_64-windows/ntoskrnl.exe_test.exe \
  ntoskrnl
```

The container used the pinned SteamRT4 SDK shown above, mounted the scratch
`wine-src` at `/src` and `wine-obj` at `/build`. Fresh prefixes were
`/build/prefix-e05-strict-retry1-20261010T`,
`/build/prefix-e05-strict-run2-20261010T`, and
`/build/prefix-e05-strict-run3-20261010T`. Each run used `WINEARCH=win64`,
`WINEDLLOVERRIDES=mscoree,mshtml=`, and the runtime options listed above.

The broad source build ran in the scratch checkout under
`/home/eric/repos/proton-build-vanguard/e05-dispatch-20261010T203000Z`:

```bash
docker run --rm \
  --mount type=bind,src=/home/eric/repos/proton-build-vanguard/e05-dispatch-20261010T203000Z/wine-src,dst=/src \
  --mount type=bind,src=/home/eric/repos/proton-build-vanguard/e05-dispatch-20261010T203000Z/wine-obj,dst=/build \
  --workdir /build \
  registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64@sha256:97526b794ce1a9bed5f891084462260b3a02399569f7438a3a57b5a253001db9 \
  bash -lc 'make -j8 all'
```

Attempt 1 exited **2** after PETHREAD/PKTHREAD type errors; after correction,
attempt 2 exited **0**, log SHA256
`cadc9e258adc59e387ebb8ec0ddb61c87f17865f3fad999ad562af5fe8caa504`. It
predates the latest fixture revisions, including the uncaught-fault recovery
case. The final focused target rebuild command is:

```bash
docker run --rm \
  --mount type=bind,src=/home/eric/repos/proton-build-vanguard/e05-dispatch-20261010T203000Z/wine-src,dst=/src \
  --mount type=bind,src=/home/eric/repos/proton-build-vanguard/e05-dispatch-20261010T203000Z/wine-obj,dst=/build \
  --workdir /build \
  registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64@sha256:97526b794ce1a9bed5f891084462260b3a02399569f7438a3a57b5a253001db9 \
  bash -lc 'make -B -j1 V=1 -C dlls/ntoskrnl.exe'
```

The forced target build exited **0**, with `target-build.log` SHA256
`1dc4bc0f538bb04fbfa0c2e147acb8503ce4b9b8dd06ff46fc716cd277b57168`. The
focused tests build also exited **0**, with `tests-build.log` SHA256
`ce5e4b707fa4e087af7c424b4315240e4b76bfcff11a3d17aea7128aceb0e739`. These
are Wine target/test builds, not a complete Proton build or dispatch result.

The first strict runtime attempt ended with status **5**. Its retained log
SHA256 is `c96ba4f09fceb3b2421d536bbb8586597d18e17463abae493d233277059d277f`.
The cause was a strict-fixture null `memset`: strict mode omits execution-region
mapping, but the fixture initialized `regions[1]` and `[2]` unconditionally
before child setup. The run did not reach the E05 IOCTL. Retain it as a failed
fixture attempt, not as an implementation result.

Final working-source hashes supplied for the focused experiment:

| Wine file | SHA256 |
|---|---|
| `dlls/ntoskrnl.exe/ntoskrnl.c` | `7b4dfadc432d36abe1575fa609320410f71345307d77bec2f2ed4e89ef3a634a` |
| `dlls/ntoskrnl.exe/tests/driver.c` | `f3aa337a521000c7e04287f91e59f33bcd008d13df6fdfaf96bc1a216f7a6090` |
| `dlls/ntoskrnl.exe/tests/driver.h` | `fa51693581a2aa029635c7d919e491b656abd1881190b431d63f24aea7b59093` |
| `dlls/ntoskrnl.exe/tests/ntoskrnl.c` | `aafe83af5eae68fb5f1fc3957794674f6af206dd712f454c353dd22cfe1f22b4` |
| `dlls/ntdll/unix/loader.c` | `13cff151d4102c41fabe9e2b8793f845e85e6925e1639e55cce86a50c11a3194` |
| `programs/services/services.c` | `af7daca0af5abf65b631f38cbef8499a14872d8cc3a6659c4413a786d5bd0834` |

The focused runtime artifacts were hashed as follows:

| Artifact | SHA256 |
|---|---|
| `ntdll.so` | `e9ec1b10fc127513bd1e86824116c5e190f1ebd89aeed0578e8a3f6fe1905334` |
| `ntoskrnl.exe` | `7d7480715cb78a2d3e769aa417d9795af2002d751e33ec7fc8dd7fb2d2587f7c` |
| Test executable | `22e421c4d90364f51984a1c99acc5b94a95782ab6c8cb3d236d4d894b54eef58` |
| `driver.dll` | `f69b4cc828297406d2e23192ec9bbcd28bb45add1eb7cffe8258ef243948ff23` |
| `services.exe` | `e3db3f0014c9c6119a4a5d07a42ebd6ced36bc30926845d1e086087a7069eb82` |
| `wineserver` | `3fbe5722d30ce68d61137fcdb3b3002f75ccbdf6ee72298a930702bc8d43001f` |

The retained direct-load disassembly (`driver-direct-load-disassembly.txt`,
SHA256 `166fcf98c2382cc6503cbe0f3708a313930594a6444fc07dea171da562b4181b`)
shows the compiled byte loads in the final `driver.dll`:

```text
180007856: 0f b6 01    movzx eax,BYTE PTR [rcx]
18000786f: 0f b6 01    movzx eax,BYTE PTR [rcx]
```

These are actual loads through the common and target-only pointers, not remote
copy helper results. The harness patch snapshot is retained as
`dispatch-harness.patch` (SHA256
`59640e385df2bd9f8d73eabab0ccea113471083c12716e6df18cb576e202607c`).

## Results

The default-off full-suite candidate used a fresh prefix with all five
experimental variables unset. It reported **34,593 tests, 169 todos, 21
failures, 1 skipped**, exit **21**. The retained baseline from
`/home/eric/repos/proton-build-vanguard/a1b-managed-layout-20261010T/e05-off.log`
reported the same counts. Normalizing each `Test failed:` line by removing its
source file/line prefix produced an exact multiset match: 37 diagnostic lines /
25 unique messages, no baseline-only or candidate-only diagnostics. Candidate
log SHA256: `f69fc86f2ce000de43be8756f65238782f7ac92597806459f736b1467c9dcdcc`;
baseline SHA256: `c69bd2899e2c836662741768ba1972d5869fc1aa96fc7f3eaae2a82b41ebe001`;
comparison JSON SHA256:
`00dc6b8ab88d35d98094b03b177b8c154300fd4c3048ecd2b7fee0a008d629e9`. This
shows no added normalized failure in the default-off full suite. It is not a
green suite or a native Windows comparison.

The focused retry log is
`strict-run-retry1.log`, SHA256
`745775714bf0a4c6f274bae28c326b5eef16bfc1f8b77981777fe320cb883d56` (retained
under `/home/eric/repos/proton-build-vanguard/e05-dispatch-20261010T203000Z/evidence/`);
its runner exit was **0**. Follow-up strict run logs there are `strict-run-2.log`
(SHA256 `b46b12b128dd1411ef91828f3bf7d6001a430c82ec80c34d9857f409a6775303`)
and `strict-run-3.log` (SHA256
`5ec8c68ae7a2d8593a0d57cb1ba72ceddae335bf6f7c86fc36ca0b617f8c8cff`); both
also exited **0**. Each suite reported **173 tests, 1 todo, 0 failures, 0
skipped**. The lone todo is
the existing benign-driver `SignerSign` `E_NOTIMPL` result; all strict E05
assertions passed without todos or skips.

The five ordinary-load observations were:

| Phase | Common mapping | Target-only mapping |
|---|---:|---|
| Caller before attach | `0x59` | guarded read raised `STATUS_ACCESS_VIOLATION` |
| Attached to A | `0xa1` | `0xc3` |
| Nested attached to B | `0xb2` | `0xd4` |
| Detached to A | `0xa1` | `0xc3` |
| Detached to caller | `0x59` | guarded read raised `STATUS_ACCESS_VIOLATION` |

The fixture also caught the expected absent-target read while attached to A and
explicitly detached. Separately, its uncaught fault IOCTL observed A as the
attached process, returned `ERROR_NOACCESS` (998) with zero output bytes, and
was followed by a healthy E05 IOCTL that returned through the full nested
attach/detach chain. The strict assertions checked all eight state bits,
creator/current-process and pointer relationships, stable logical thread,
process references, KAPC storage and previous-process relations, IRP/stack/
SystemBuffer/global/pool/stack-cookie invariants.

| Run | Normal buffered dispatch | caller/A/B/A/caller loads | fault/cleanup follow-up | identity and kernel-state sentinels | Exit / summary |
|---|---|---|---|---|---|
| Retained default-off baseline | full suite, variables absent | prior default-off result | prior default-off result | same 37/25 failure multiset | exit 21; 34,593 tests, 169 todos, 21 failures, 1 skip |
| Current default-off candidate | full suite, variables absent | matches baseline | matches baseline | same 37/25 failure multiset; no unique diagnostics | exit 21; 34,593 tests, 169 todos, 21 failures, 1 skip |
| Executor candidate, strict run 1 | fixture setup failed before IOCTL | not reached | not reached | not reached | exit 5; retained fixture failure |
| Executor candidate, strict retry 1 | passed | all five phases as above | caught and uncaught fault paths plus healthy follow-up passed | strict assertions passed | exit 0; 173 tests, 1 unrelated todo, 0 failures, 0 skipped |
| Executor candidate, strict run 2 | passed | same five values | fault 998/0 and healthy follow-up passed | strict assertions passed | exit 0; 173 tests, 1 unrelated todo, 0 failures, 0 skipped |
| Executor candidate, strict run 3 | passed | same five values | fault 998/0 and healthy follow-up passed | strict assertions passed | exit 0; 173 tests, 1 unrelated todo, 0 failures, 0 skipped |
| Default-off full-suite comparison | complete | no E05 strict mode | no E05 strict mode | exact normalized diagnostic match | comparison JSON retained |

Three strict runs confirm the bounded single-thread contract for this opt-in
prototype on x64. Keep the caught fault with explicit detach separate from the
uncaught fault and wrapper recovery. The default-off full-suite candidate has
the same normalized failures as the retained baseline. The unrelated
SignerSign todo is retained and reported; the default-off full suite is not
green.

## Conclusion and next action

Three strict x64 runs now provide preliminary evidence for the bounded,
single-thread synchronous contract: normal buffered dispatch preserved the
compiled handler while ordinary loads observed caller → A → B → A → caller
memory, including a target-only mapping. The separate uncaught-fault request
returned the expected error and a following healthy request completed. Three
fresh strict runs passed, the exact default-off baseline comparison found no
candidate-only normalized failures, and the final source/build/artifact audit
is recorded above. Next, test two simultaneous logical driver threads with independent
nested attachments, protection changes and unmap/address reuse, target exit,
cancellation, and deterministic cleanup. Then validate x86/i386 ABI and
structure layout, native Windows reference behavior, broader address-space
semantics, and full Proton integration as separate gates. This does not
establish general Wine attach semantics or Vanguard acceptance.

## Limits and references

Concurrency, target-lifetime races, protection changes, address reuse, native
Windows behavior, i386, full Proton build, Vanguard operation and acceptance,
accepted sessions, and gameplay remain pending. See the
[attachment backing design](2026-10-10-a1b-attach-backing-design.md),
[original E05 falsifier](2026-10-10-e05-attachment-falsifier.md),
[architecture guide](../ARCHITECTURE.md#current-e05-result), and
[test-running guide](../TESTING.md#e05-buffered-dispatch-attachment-chain).
