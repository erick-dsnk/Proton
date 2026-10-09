# Ordinary rundown protection test evidence

This directory publishes the exact retained logs from the first x86_64 Wine
rundown-protection implementation run and its clean unpatched baseline. These
are generic Wine `ntoskrnl.exe` driver tests. They do not contain Riot software,
Vanguard binaries, or a Vanguard session, and they establish no Vanguard
acceptance or League gameplay result.

## Contents and integrity

`patched.log` and `baseline.log` are byte-for-byte copies of the retained
original logs. No redaction or other transformation was applied. Their SHA256
hashes and byte lengths are in [`results.json`](results.json). The generic
Wine log content was reviewed before publication; its one occurrence of the
word `vanguard` is part of the temporary local Wine prefix path. The published
logs are each about 29 KB.

Verify the logs and regenerate the normalized failure comparison from this
directory:

```sh
sha256sum patched.log baseline.log
python3 compare_failures.py > /tmp/failure-comparison.json
cmp failure-comparison.json /tmp/failure-comparison.json
```

The comparison script removes only a leading `source-file:line:` prefix from
lines containing Wine's `Test failed:` diagnostic. It retains the message text
and counts exact messages. The result is 37 diagnostic lines and 25 unique
messages in each run, with no patch-only or baseline-only messages. The summary
is in [`failure-comparison.json`](failure-comparison.json).

## Result interpretation

The patched suite reports 34,156 executed tests, 161 todo, 21 failures, and 0
skips. The unpatched baseline reports 26,023 executed tests, 161 todo, 21
failures, and 0 skips. The additional 8,133 executed checks exercise the new
rundown implementation; no new failure or skip appears in the normalized
comparison. Both suites have existing failures, so this is not a green-suite
claim. The process exit statuses for these two test runner invocations were
not retained and are recorded as unknown. Do not infer them from the summaries.

A full configured x64 Wine `make -j8 all` completed with exit status 0. The
experiment did not build complete Proton, run on native Windows, or validate
32-bit behavior. Full commands, four source-file hashes, build provenance,
known failures, and next gates are recorded in the top-level
[`implementation progress record`](../../vanguard-implementation-progress.md).
The implementation is in Wine commit
[`2990a75`](https://github.com/erick-dsnk/wine/commit/2990a75de24c57ab0a8ff2dc3caab7d075d4df40),
based on Wine commit `e60892c`.

Vanguard platform acceptance, an accepted Vanguard session, and playable
League remain unproven. See the [project roadmap](../../ROADMAP.md) and
[testing conventions](../../TESTING.md) for the remaining evidence gates and
how to record future experiments.
