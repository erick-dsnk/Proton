# Testing and reporting compatibility

Test the behavior this fork claims, using its built Wine/Proton artifacts and
recorded inputs. The project currently has an x64 generic rundown-protection
increment; Vanguard execution, accepted session and League gameplay have no
demonstrated result. Consult the [implementation register](vanguard-implementation-progress.md)
for the initial evidence and the [roadmap](ROADMAP.md) for remaining gates.

## Run the isolated x64 generic driver suite

First follow [BUILDING](BUILDING.md#isolated-x64-wine-conformance-build). The
variables below come from that same Bash session. Use a unique prefix for each
attempt, including separate baseline and patched runs. Headless Xvfb is supplied
by the recorded SDK. The original Wineboot attempt opened an optional Mono
installer; disabling the unused CLR/HTML installers avoids that modal prompt.
The test wrapper adds `ntoskrnl.exe=b`; the generic driver imports remain active.

```bash
VANGUARD_RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)-$$"
VANGUARD_PREFIX="/build/prefix-$VANGUARD_RUN_ID"
set -o pipefail
docker run --rm \
  -v "$VANGUARD_BUILD/wine-src:/src" \
  -v "$VANGUARD_BUILD/wine-obj:/build" \
  -w /build --user "$VANGUARD_BUILD_USER" \
  -e HOME=/build/home -e XDG_CACHE_HOME=/build/cache \
  -e WINEPREFIX="$VANGUARD_PREFIX" -e WINEARCH=win64 \
  -e 'WINEDLLOVERRIDES=mscoree,mshtml=' \
  "$VANGUARD_SDK" \
  bash -lc 'timeout --kill-after=15s 300s xvfb-run -a \
    /src/tools/runtest -v -T /build -M ntoskrnl.exe \
    -p /build/dlls/ntoskrnl.exe/tests/x86_64-windows/ntoskrnl.exe_test.exe \
    ntoskrnl' \
  2>&1 | tee "$VANGUARD_BUILD/ntoskrnl-$VANGUARD_RUN_ID.log"
VANGUARD_RUN_STATUS="${PIPESTATUS[0]}"
printf '%s\n' "$VANGUARD_RUN_STATUS" > "$VANGUARD_BUILD/ntoskrnl-$VANGUARD_RUN_ID.exit"
sha256sum "$VANGUARD_BUILD/ntoskrnl-$VANGUARD_RUN_ID.log"
```

Use a Bash session without `errexit` for this block if you need to capture a
failing suite's status after the pipeline. A timeout, missing summary or stopped
attempt is incomplete evidence. Preserve it with its reason and rerun under a
new run ID only after understanding the cause.

Inspect the built PE exports inside the SDK, for example:

```bash
docker run --rm -v "$VANGUARD_BUILD/wine-obj:/build" "$VANGUARD_SDK" \
  x86_64-w64-mingw32-objdump -p \
  /build/dlls/ntoskrnl.exe/x86_64-windows/ntoskrnl.exe
```

Export presence verifies the artifact's export table, not function semantics.
Inspect all eight ordinary rundown names separately from the runtime result.

## Baseline and current observed result

| Initial experiment | Runner count | Todo | Failures | Skipped |
|---|---:|---:|---:|---:|
| Wine base `e60892cc2398b0a83c332a2078c7b85e47bdb42b` | 26,023 | 161 | 21 | 0 |
| Base plus published rundown patch | 34,156 | 161 | 21 | 0 |

After normalizing file/line prefixes, the initial run had identical sets of 37
failure diagnostics (25 unique messages). The patch added 8,133 checks without
new failures or skips in that comparison. The full suite was **not green**,
and these counts are not a native Windows or target-game comparison. A repeated
run can have different counts or diagnostics; record its actual result rather
than copying this table into a new report.

To create an uncontaminated baseline, choose a separate source/object directory,
materialize the exact base source (for the initial comparison, `git -C wine
archive e60892cc2398b0a83c332a2078c7b85e47bdb42b`), and repeat the same configure,
build and runtime recipe there. Keep SDK, settings and test inputs equivalent
while using distinct clean prefixes. For future API changes, retain the new
test cases on the unpatched implementation when useful to demonstrate the bug;
label test-source differences explicitly. Compare diagnostics and the affected
block, not only aggregate failure counts.

## Contract tests expected for contributions

Cover valid initialization, ownership and reference counts, wait ordering,
concurrency, admission after teardown starts, final release, exceptions/error
paths and unload/free behavior as relevant. A worker timeout needs bounded
cleanup; no test should leave threads accessing freed fixture state. Use native
Windows reference results for the claimed contract and record OS/build,
architecture, statuses, exceptions and ordering differences. Any driver signing
or test-lab configuration is part of that experiment's scope; it is not a
Vanguard platform-acceptance result.

The rundown checkpoint still needs ordinary Windows x64 comparison and i386
execution. Source review corrected FASTCALL declarations, but x64 execution
cannot establish 32-bit ABI conformance.

The next G2 experiment must test direct pointer reads after process attachment:
a mapping only in the target, two targets with the same address but different
bytes, correct restoration after detach, exceptions and cleanup. A skip or a
logical process-ID change cannot establish the required address-space contract.

## Record distinct outcomes

1. Source/build identity and artifact export presence.
2. Generic driver loader, API, device-transport and lifecycle conformance.
3. Unmodified Vanguard driver entry and actual service/device readiness.
4. Genuine platform evidence and an accepted anti-cheat session.
5. Completed connected League gameplay and later regression across reboot/update.

Record failures, `todo_wine`, flaky markers and skips separately from passes.
An exported API, reported `SERVICE_RUNNING`, rendered window or client login
does not establish later stages. Use the [experiment template](evidence/experiment-template.md)
for logs/hashes, provenance and limitations. Keep vendor binaries, credentials,
account identifiers, access tokens and private machine identifiers out of public
records. Public diagnostics should remain sufficient to review the claim.
