# A1b combined backing and kernel-arena integration

Date: 2026-10-10. Scope: one x64 generic `ntoskrnl.exe` runtime combining the
opt-in private-mapping backing and process-local kernel-allocation arena. This
is an assembled-artifact integration check, not a full current-tree Wine build,
ordinary process attachment, or Vanguard compatibility result.

## Observed result

The default-off run reported **34,593 tests / 169 todos / 21 failures / 1
skipped**, runner exit 21. The run with both
`WINE_SHARED_PRIVATE_BACKING=1` and `WINE_SHARED_KERNEL_MEMORY=1` reported
**34,942 / 169 / 21 / 1**, runner exit 21. The opt-in run exercised 349
additional generic checks. Both candidates match the retained GCC baseline's
37 `Test failed` diagnostic lines and 25 distinct diagnostics under the same
comparison rule: remove only each diagnostic's leading source-file and line
prefix, then compare the remaining diagnostic strings as a multiset. There
were no baseline-only or candidate-only diagnostics. The single skip is the
existing GCC limitation for the compiler-generated `__try`/`__finally`
fixture.

The runtime monitor sampled five actual `winedevice.exe` processes per run.
The two options were absent in each default-off process and both were present
in all five opt-in process environments. This verifies that the combined
fixture ran with both options delivered to the Windows service host. It does
not show a cross-process alias for the kernel arena or ordinary pointer access
after attachment.

E05 remains red as an implementation contract: all eight attachment
expectations are still `todo_wine`, and the attach-probe reads still fault
with access violations. `KeStackAttachProcess` and `KeUnstackDetachProcess`
remain unimplemented stubs. The 21 full-suite failures remain and are not
attributed to this combined feature based on the baseline comparison.

## Inputs and reproducibility

| Input | Value |
|---|---|
| Proton revision | `c3547256adf6801cb45299690ea96ce208be097c` |
| Wine revision | `2990a75de24c57ab0a8ff2dc3caab7d075d4df40` |
| SDK | `registry.gitlab.steamos.cloud/proton/steamrt4/sdk/x86_64@sha256:97526b794ce1a9bed5f891084462260b3a02399569f7438a3a57b5a253001db9` |
| Architecture | x86_64, `--enable-win64` |
| Configuration identity | `config.status` SHA-256 `109eddd17d099f8aed74ab7dcb3ff4ff50c977f6e8ae9ce79e910bf336ff64f5` in all three participating object trees |
| Build scope | No compilation in the integration step. Existing compiled modules were assembled from separate backing and arena artifact trees with identical configuration identity; this is not a complete current-source build. |
| Frozen evidence manifest | `/home/eric/repos/proton-build-vanguard/a1b-backing-arena-integrated-20261010T/integrated-runtime-evidence.json`, SHA-256 `e4855e4aff4d87407ef67a412d9c7ef7063b24043124681d43e9379d73dc57e6` |
| Exact executed command metadata | `/home/eric/repos/proton-build-vanguard/a1b-backing-arena-integrated-20261010T/executed-command.json`, SHA-256 `a44c3d1a6b5b777be29d2fe77d2a0f9ec5fe6f912d7cea8ff6c2a39a929f36b7` |

The command record preserves the exact Docker argument vector, inner shell,
explicit environment and distinct per-run prefixes. The test command inside
the container was:

```sh
timeout --kill-after=15s 300s xvfb-run -a /src/tools/runtest -v -T /build -M ntoskrnl.exe -p /build/dlls/ntoskrnl.exe/tests/x86_64-windows/ntoskrnl.exe_test.exe ntoskrnl
```

The container wrapper exited 0 after recording both individual runner exits;
each Wine test runner exited 21. The wrapper's captured stdout/stderr file is
empty and has SHA-256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

| Run | Local log | SHA-256 | Runner exit |
|---|---|---|---:|
| Both options unset | `/home/eric/repos/proton-build-vanguard/a1b-backing-arena-integrated-20261010T/wine-obj/integrated-off.log` | `e1553e3a2f6dd3a83c14d9804523566b3995d30c893a3e06bdd84f4fc89cad05` | 21 |
| Both options enabled | `/home/eric/repos/proton-build-vanguard/a1b-backing-arena-integrated-20261010T/wine-obj/integrated-on.log` | `7915f4dd0159b35451821dc4201e6e938fbf2c5508e67061a193be0bd9e4abc2` | 21 |

The assembled artifacts were `ntdll.so` SHA-256
`a1a47247ef2ec2008c26da2d5aef6324799b1db245fa0daaf3b7a935771c9c4b`,
`wineserver` `34786b32962cf532767edd91835e21893a8d50cb4e7b43b9ef794a554f26bf5e`,
`services.exe` `dd6a49d83e7f90fcc48a7606936c42df39e9f6aa71e5cb67829d3e8e3dd529e7`,
`ntoskrnl.exe` `77e317a7ac03f5b63503f8ed7f11a699ec424971a11446399e8ebf40d58f134b`,
the driver test PE `8c95db77482173be91a351c366adb5126d2c836a8af0b786ee819a1edc7f4fd3`,
and `driver.dll` `dee64057e924ceb80c8cf75c9998b4d6eb6285fc01fa14715d648279e2a17d0c`.
The full artifact and source SHA-256 inventory is in the frozen manifest.
The E05 `test_process_attachment()` extraction is 12,879 bytes with SHA-256
`c92e2e0eefb38997c2642444d99eb1af2152bf16107aceacd4d7c07a62b62079`; it
matches the live source and both tested source copies.

## Interpretation and next gate

The combined modules coexist in the tested x64 generic suite with the same
baseline diagnostics, and both opt-ins reach the real Windows service process.
The arena remains process-local; the backing primitive still has no foreign
view acquisition path. The integration adds no memory-alias or attach
semantics. E05's same-address/different-target probe therefore remains the
next decisive runtime gate after a managed executor can boot with the real
host RTL and a defined address-space contract. No Vanguard acceptance or
gameplay claim follows from this run.

This comparison uses the 37-line / 25-distinct-diagnostic normalization used
by the retained GCC baseline and arena record. The standalone private-backing
record used a different semantic-template normalization (18 templates); its
count is intentionally not combined with this comparison.
