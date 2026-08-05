#!/usr/bin/env python3
"""Enforce the public-repository GitHub Actions trust boundary."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
USES = re.compile(r"^(?P<indent>\s*)uses:\s*(?P<target>[^\s#]+)", re.M)
JOB_KEY = re.compile(r"^  (?P<name>[A-Za-z0-9_-]+):\s*$")
CHECKOUT_LINE = re.compile(r"uses:\s*actions/checkout@[0-9a-f]{40}(?:\s+#.*)?$")


def display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.name


def is_pull_request_workflow(text: str) -> bool:
    return bool(
        re.search(r"^\s{2}pull_request:\s*$", text, re.M)
        or re.search(r"^on:\s*\[[^\]]*\bpull_request\b", text, re.M)
    )


def parse_jobs(lines: list[str]) -> list[tuple[str, list[str]]]:
    try:
        start = next(index for index, line in enumerate(lines) if line == "jobs:")
    except StopIteration:
        return []

    jobs: list[tuple[str, list[str]]] = []
    current_name: str | None = None
    current_lines: list[str] = []
    for line in lines[start + 1 :]:
        if line and not line.startswith(" "):
            break
        match = JOB_KEY.match(line)
        if match:
            if current_name is not None:
                jobs.append((current_name, current_lines))
            current_name = match.group("name")
            current_lines = []
        elif current_name is not None:
            current_lines.append(line)
    if current_name is not None:
        jobs.append((current_name, current_lines))
    return jobs


def validate_workflow(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    name = display_path(path)

    if re.search(r"^\s{2}pull_request_target:\s*$", text, re.M):
        errors.append(f"{name}: executable pull_request_target is prohibited")

    if not re.search(r"^permissions:\s*$", text, re.M):
        errors.append(f"{name}: top-level permissions block is required")

    pr_capable = is_pull_request_workflow(text)
    if pr_capable and re.search(r"^\s+[A-Za-z0-9_-]+:\s*write\s*$", text, re.M):
        errors.append(f"{name}: pull-request workflow must not request write permissions")
    if pr_capable and re.search(r"^\s+id-token:\s*write\s*$", text, re.M):
        errors.append(f"{name}: pull-request workflow must not request OIDC")

    for match in USES.finditer(text):
        target = match.group("target")
        if target.startswith("./") or target.startswith("docker://"):
            continue
        if "@" not in target:
            errors.append(f"{name}: action is not pinned: {target}")
            continue
        action, revision = target.rsplit("@", 1)
        if not FULL_SHA.fullmatch(revision):
            errors.append(f"{name}: action must use a full immutable SHA: {action}@{revision}")

    for index, line in enumerate(lines):
        if not CHECKOUT_LINE.search(line):
            continue
        indent = len(line) - len(line.lstrip())
        block: list[str] = []
        for following in lines[index + 1 :]:
            following_indent = len(following) - len(following.lstrip())
            if following.strip() and following_indent <= indent:
                break
            block.append(following)
        if not any(re.search(r"persist-credentials:\s*false\s*$", item) for item in block):
            errors.append(f"{name}: checkout must set persist-credentials: false")

    jobs = parse_jobs(lines)
    if not jobs:
        errors.append(f"{name}: workflow must define at least one job")
    for job_name, job_lines in jobs:
        job_text = "\n".join(job_lines)
        if not re.search(r"^\s{4}timeout-minutes:\s*\d+\s*$", job_text, re.M):
            errors.append(f"{name}: job {job_name} requires timeout-minutes")
        if re.search(r"runs-on:.*\bself-hosted\b", job_text):
            errors.append(f"{name}: public repository jobs must not use self-hosted runners")

    return errors


def validate(root: Path = WORKFLOWS) -> list[str]:
    errors: list[str] = []
    if not root.is_dir():
        return [f"missing workflow directory: {root}"]
    workflows = sorted([*root.glob("*.yml"), *root.glob("*.yaml")])
    if not workflows:
        return ["no GitHub Actions workflows found"]
    for path in workflows:
        errors.extend(validate_workflow(path))
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("workflow security check failed:", file=sys.stderr)
        for error in sorted(set(errors)):
            print(f"- {error}", file=sys.stderr)
        return 1
    print("workflow security check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
