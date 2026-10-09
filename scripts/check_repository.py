#!/usr/bin/env python3
"""Validate first-party docs, links, issue forms, and basic workflow safeguards.

This is a repository hygiene check. It does not build Proton, load a driver, run
Vanguard, or establish platform acceptance. Remote links are intentionally not
requested. Submodules and vendored documentation are outside this check.
Requires Python 3 and PyYAML (CI pins the dependency).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required; install it in a virtual environment (see CI workflow).")

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def error(path: Path, message: str) -> None:
    errors.append(f"{path.relative_to(ROOT)}: {message}")


def prose(text: str) -> str:
    """Hide code blocks, where paths and markup are examples rather than links."""
    output = []
    fence = None
    for line in text.splitlines():
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            output.append("")
        else:
            output.append(line if fence is None else "")
    return "\n".join(output)


def anchors(text: str) -> set[str]:
    """GitHub heading anchors, duplicate suffixes, and explicit HTML anchors."""
    text = prose(text)
    found = set(re.findall(r"<(?:a|[a-z][a-z0-9]*)\b[^>]*\b(?:id|name)=[\"']([^\"']+)[\"']", text, re.I))
    counts: dict[str, int] = {}
    lines = text.splitlines()
    for index, line in enumerate(lines):
        atx = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        heading = atx.group(1) if atx else None
        if heading is None and line.strip() and index + 1 < len(lines):
            if re.fullmatch(r"\s{0,3}(?:=+|-+)\s*", lines[index + 1]):
                heading = line.strip()
        if heading is None:
            continue
        heading = re.sub(r"!?(?:\[([^\]]*)\])\([^)]*\)", r"\1", heading)
        heading = re.sub(r"<[^>]*>", "", heading).lower()
        slug = "".join(ch for ch in heading if ch.isalnum() or ch in " _-")
        slug = slug.replace(" ", "-")
        duplicate = counts.get(slug, 0)
        counts[slug] = duplicate + 1
        found.add(slug if duplicate == 0 else f"{slug}-{duplicate}")
    return found


def check_target(source: Path, target: str) -> None:
    target = target.strip()
    if target.startswith("<"):
        target = target.split(">", 1)[0][1:]
    else:
        target = re.split(r"\s+[\"']", target, maxsplit=1)[0]
    target = target.replace(r"\(", "(").replace(r"\)", ")")
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc:
        return
    if parsed.path.startswith("/"):
        error(source, f"non-portable absolute documentation link: {target}")
        return
    destination = (source.parent / unquote(parsed.path)).resolve() if parsed.path else source
    if not destination.is_relative_to(ROOT):
        error(source, f"link escapes repository: {target}")
    elif not destination.exists():
        error(source, f"missing local link target: {target}")
    elif parsed.fragment and destination.suffix.lower() == ".md":
        fragment = unquote(parsed.fragment)
        if fragment not in anchors(destination.read_text(encoding="utf-8")):
            error(source, f"missing Markdown heading/anchor: {target}")


def check_markdown(path: Path) -> None:
    text = prose(path.read_text(encoding="utf-8"))
    # Escaped parentheses are supported; raw nested parentheses should use <...>.
    for match in re.finditer(r"!?\[[^\]]*\]\((<[^>]+>|(?:\\.|[^)\n])+)\)", text):
        check_target(path, match.group(1))
    # Definitions are checked even if unused, preventing stale local references.
    for match in re.finditer(r"^\s{0,3}\[[^\]]+\]:\s*(<[^>]+>|\S+)", text, re.M):
        check_target(path, match.group(1))


def load_yaml(path: Path) -> dict:
    try:
        # BaseLoader retains 'on' as a string instead of YAML 1.1's boolean.
        value = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
        if not isinstance(value, dict):
            raise ValueError("expected a YAML mapping")
        return value
    except (yaml.YAMLError, ValueError) as exc:
        error(path, f"invalid YAML: {exc}")
        return {}


def check_github() -> None:
    forms = sorted((ROOT / ".github/ISSUE_TEMPLATE").glob("*.yml"))
    names = set()
    for path in forms:
        value = load_yaml(path)
        if path.name == "config.yml":
            if value.get("blank_issues_enabled") != "false":
                error(path, "blank issues must be disabled in favor of scoped forms")
            continue
        for field in ("name", "description", "body"):
            if not value.get(field):
                error(path, f"missing issue form field: {field}")
        name = value.get("name")
        if name in names:
            error(path, "duplicate issue form name")
        names.add(name)
        identifiers = set()
        for item in value.get("body", []):
            if not isinstance(item, dict) or item.get("type") not in {"markdown", "input", "textarea", "checkboxes", "dropdown"}:
                error(path, "invalid issue form body item")
                continue
            identifier = item.get("id")
            if identifier and identifier in identifiers:
                error(path, f"duplicate issue field id: {identifier}")
            identifiers.add(identifier)
            if not isinstance(item.get("attributes"), dict):
                error(path, "issue field attributes must be a mapping")
    for path in (ROOT / ".github/ISSUE_TEMPLATE").glob("*.md"):
        error(path, "obsolete Markdown issue template; use the scoped YAML forms")
    for path in sorted((ROOT / ".github/workflows").glob("*.yml")):
        workflow = load_yaml(path)
        events = workflow.get("on", {})
        if not isinstance(events, dict):
            error(path, "workflow events must be an explicit mapping")
            continue
        if {"pull_request_target", "workflow_run"} & events.keys():
            error(path, "privileged workflow triggers require a separately reviewed design")
        permissions = workflow.get("permissions", {})
        if not isinstance(permissions, dict) or any(value != "read" for value in permissions.values()):
            error(path, "repository checks must declare read-only permissions")
        for job in workflow.get("jobs", {}).values():
            if "permissions" in job and job["permissions"] != permissions:
                error(path, "job permissions must preserve the workflow's read-only scope")
            for step in job.get("steps", []):
                action = step.get("uses", "")
                if action and not action.startswith("./") and not re.search(r"@[0-9a-f]{40}$", action):
                    error(path, f"external action must use an immutable commit SHA: {action}")


def main() -> int:
    required = [
        "README.md", "CONTRIBUTING.md", "GOVERNANCE.md", "CODE_OF_CONDUCT.md",
        "SUPPORT.md", "SECURITY.md", "LICENSES.md", "CHANGELOG.md", "LICENSE",
        "LICENSE.proton", "AGENTS.md", "docs/README.md", "docs/ROADMAP.md",
        "docs/ARCHITECTURE.md", "docs/BUILDING.md", "docs/TESTING.md",
        "docs/vanguard-linux-feasibility.md", "docs/vanguard-implementation-progress.md",
        ".github/CODEOWNERS", ".github/pull_request_template.md",
        ".github/ISSUE_TEMPLATE/config.yml", ".github/workflows/repository-checks.yml",
        ".github/ISSUE_TEMPLATE/compatibility-bug.yml",
        ".github/ISSUE_TEMPLATE/conformance-gap.yml",
        ".github/ISSUE_TEMPLATE/research-proposal.yml",
        ".github/ISSUE_TEMPLATE/support-question.yml",
    ]
    for name in required:
        if not (ROOT / name).is_file():
            error(ROOT / name, "required project file is missing")
    docs = sorted(ROOT.glob("*.md"))
    for directory in ("docs", "docker", "symstore", ".github"):
        docs.extend(sorted((ROOT / directory).rglob("*.md")))
    docs.extend([ROOT / "fonts/ume/PROTON_NOTE.md", ROOT / "icu/README.md"])
    for path in docs:
        check_markdown(path)
    check_github()
    if errors:
        print("Repository checks failed:", file=sys.stderr)
        print("\n".join(f"- {message}" for message in errors), file=sys.stderr)
        return 1
    print(f"Repository checks passed: {len(docs)} first-party Markdown files, local links/anchors, project files, and GitHub YAML.")
    print("No remote link requests or Proton/Wine/Vanguard runtime validation performed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
