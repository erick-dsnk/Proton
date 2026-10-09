# YYYY-MM-DD — experiment name

Status: planned / completed / failed / incomplete. Claim label:
Observed / Documented / Hypothesis / Conditional / Unknown.

## Question and scope

- Contract or falsifiable hypothesis:
- Related epic/gate and issue/PR:
- Intended result and negative control:
- Explicit limits (generic conformance, local target operation, acceptance, gameplay):

## Inputs

| Input | Exact value |
|---|---|
| Proton SHA / Wine SHA | |
| Other relevant gitlinks and working diff | |
| SDK digest / toolchain | |
| OS, kernel, architecture, relevant runtime/hardware | |
| Test build/architecture and configuration | |
| Vendor version/hash and selected mode, if relevant | |
| Windows reference OS/build/configuration, if relevant | |

## Commands and artifacts

Provide commands with portable path variables, build/run exit codes, and
separate fresh prefix/run IDs. Identify artifacts and SHA256 values. State which
logs are public, linked, sanitized, or retained locally; local paths alone are
not accessible evidence for contributors.

```bash
# Exact commands and recorded exit codes
```

## Results

| Run | Total | Todo | Flaky | Failures | Skips | Exit / summary available |
|---|---:|---:|---:|---:|---:|---|
| Baseline/reference | | | | | | |
| Changed implementation | | | | | | |

Record relevant statuses, exceptions, ordering, lifetime/race behavior and
normalized diagnostic differences. Describe excluded attempts and why they are
not valid comparisons. A timeout, skip or todo is not a demonstrated pass.

## Conclusion and next action

What exactly was established? What failed or remains unknown? Which gate, if
any, moved and what observation is needed next? Keep build, generic behavior,
driver entry, service readiness, accepted session and gameplay distinct.

## References

Link source/contract documents and access dates. Do not include vendor binaries,
secrets or private account/machine identifiers.
