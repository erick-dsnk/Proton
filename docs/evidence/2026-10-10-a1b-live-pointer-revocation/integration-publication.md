# Published component and committed-source integration check

Date: 2026-10-10. This record follows the local-candidate runs in the
[original experiment bundle](README.md). It verifies that the same seven-file
Wine change is published, retrievable from a clean clone, and passes a targeted
rebuild and rerun from the committed source.

## Component publication and retrieval

Wine commit
[`9c389578ccc8c7111047dbb826debc102a8ddf26`](https://github.com/erick-dsnk/wine/commit/9c389578ccc8c7111047dbb826debc102a8ddf26)
is published on branch `vanguard-a1b-apc-cancellation`, based on
`d262e37075efc5ce8c7be8e85a547fbb6c03ad3d`. Its seven changed files are the
APC routing/cancellation trace, `/proc/thread-self/maps` observer repair, and
the MAP/REVOKE fixture and runner.

A fresh HTTPS clone fetched and checked out the exact commit detached. The
checkout was clean and `git fsck --connectivity-only --no-reflogs` exited 0.
The complete tracked source audit covered 11,163 paths with zero differences
between the frozen build source and clean clone; the canonical path/hash-list
digest is
`7af759389cb030176ea212641d3b9b301b4a58adc0848668d170c82e5be4f62a`. The
exact commands and per-file hashes are in
[clean-clone-verification.json](integration/clean-clone-verification.json)
and [committed-source-hashes.json](integration/committed-source-hashes.json).

## Build and runtime from the published source

The frozen integration source matches commit `9c389578` and used Linux AMD64,
`--enable-win64`, and the pinned SteamRT4 SDK image
`registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64@sha256:97526b794ce1a9bed5f891084462260b3a02399569f7438a3a57b5a253001db9`.
The forced server and ntdll build commands executed inside the pinned SDK
container and exited 0:

```sh
make -B -j1 V=1 -C server wineserver
make -B -j1 V=1 dlls/ntdll/ntdll.so
```

The first combined make invocation only reported `wineserver` up to date and
was inconclusive; it is not counted as a successful rebuild. The forced server
and ntdll builds above superseded it. The full captured outer Docker argv for
that inconclusive attempt, including SDK digest and source/build/fixture
mounts, is preserved in `integration-manifest.json`; the forced inner commands
and their full logs are recorded separately. The fixture was launched by the
host runner:

```sh
A1B_PROOF_ROOT=/path/to/frozen-integration python3 proof-runner.py build
```

The runner's exact fixture-build Docker argv is in
`integration/fixture-build-command.json`. The fixture was freshly built.
This is a targeted assembled Wine runtime check, not a fresh complete Wine or
Proton build. Compatible runtime modules from the recorded object tree were
reused.

| Run | Result | Trace result |
|---|---|---|
| Queued MAP and REVOKE cancellation | 52 checks, 0 failures, 0 skips; exit 0 | Passed. MAP APC 1 was cancelled for recipient TID `0164` before dequeue. REVOKE APC 5 was cancelled for TID `0170`; APC 6 retried to survivor TID `0174`, and native ACK sequence 33 followed. |
| Tracing-only control | 249 checks, 0 failures, 0 skips; exit 0 | Passed without the cancellation hold. |

Both runs recorded matching source and artifact SHA256 values before and after
execution. The exact command/result JSON, control record, logs, build outputs,
exit files, and integration manifest are retained in [`integration/`](integration/).

The original local-candidate experiment logs remain historical evidence. This
committed-source check establishes reproducibility of the bounded Linux
AMD64 Wine fixture behavior; it does not establish i386 behavior, native
Windows comparison, complete Proton integration, public attach semantics,
Vanguard acceptance, or League gameplay.
