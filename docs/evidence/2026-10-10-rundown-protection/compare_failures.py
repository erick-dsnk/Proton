#!/usr/bin/env python3
"""Normalize Wine test failure diagnostics from the two retained raw logs."""

from collections import Counter
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
PREFIX = re.compile(r"^([A-Za-z0-9_.-]+:\d+: )(Test failed: .*)$")


def failures(path: Path) -> Counter[str]:
    result: Counter[str] = Counter()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = PREFIX.match(line)
        if match:
            # Remove exactly the source-file and line-number prefix. Keep the
            # complete diagnostic text unchanged for set comparison.
            result[match.group(2)] += 1
    return result


patched = failures(HERE / "patched.log")
baseline = failures(HERE / "baseline.log")
shared = patched.keys() & baseline.keys()
report = {
    "normalization": "strip only leading source-file:line prefix from lines matching 'Test failed:'",
    "patched": {"diagnostic_lines": sum(patched.values()), "unique_messages": len(patched)},
    "baseline": {"diagnostic_lines": sum(baseline.values()), "unique_messages": len(baseline)},
    "shared_messages": len(shared),
    "patched_only": [
        {"message": message, "count": patched[message]}
        for message in sorted(patched.keys() - baseline.keys())
    ],
    "baseline_only": [
        {"message": message, "count": baseline[message]}
        for message in sorted(baseline.keys() - patched.keys())
    ],
    "shared": [
        {"message": message, "patched_count": patched[message], "baseline_count": baseline[message]}
        for message in sorted(shared)
    ],
}
print(json.dumps(report, indent=2, ensure_ascii=False))
