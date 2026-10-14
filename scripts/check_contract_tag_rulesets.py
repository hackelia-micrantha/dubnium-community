#!/usr/bin/env python3
"""Plan and READ-ONLY verify immutable public contract-tag GitHub rulesets.

No endpoint in this tool creates, edits, deletes, or tests writes to GitHub.
Ruleset administration requires a separately authorized operator action.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any

REPO = "hackelia-micrantha/dubnium-community"
TAG_PATTERN = "refs/tags/contract-v*"
CREATION_NAME = "contract-v-creation"
IMMUTABLE_NAME = "contract-v-immutability"
API = "https://api.github.com"
CREATOR_TYPES = ("User", "Team", "Integration")


def desired(creator_type: str, creator_id: int) -> list[dict[str, Any]]:
    if creator_type not in CREATOR_TYPES or creator_id <= 0:
        raise ValueError("release creator must be a specific User, Team or Integration ID")
    common: dict[str, Any] = {
        "target": "tag",
        "enforcement": "active",
        "conditions": {"ref_name": {"include": [TAG_PATTERN], "exclude": []}},
    }
    return [
        {**common, "name": CREATION_NAME,
         "bypass_actors": [{"actor_type": creator_type, "actor_id": creator_id, "bypass_mode": "always"}],
         "rules": [{"type": "creation"}]},
        {**common, "name": IMMUTABLE_NAME,
         "bypass_actors": [],
         "rules": [{"type": "update"}, {"type": "deletion"}]},
    ]


def validate_rulesets(found: list[dict[str, Any]], expected: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    active = [item for item in found if item.get("enforcement") == "active"]
    by_name: dict[str, dict[str, Any]] = {}
    for item in active:
        name = item.get("name")
        if name not in {CREATION_NAME, IMMUTABLE_NAME}:
            errors.append(f"unexpected active tag ruleset: {name!r}; review overlap explicitly")
        elif name in by_name:
            errors.append(f"duplicate active tag ruleset: {name}")
        else:
            by_name[name] = item

    for want in expected:
        name = want["name"]
        got = by_name.get(name)
        if got is None:
            errors.append(f"missing active tag ruleset: {name}")
            continue
        for field in ("target", "enforcement"):
            if got.get(field) != want[field]:
                errors.append(f"{name}: {field} mismatch")
        if got.get("conditions", {}).get("ref_name") != want["conditions"]["ref_name"]:
            errors.append(f"{name}: target pattern/exclusions mismatch")
        if sorted(r.get("type") for r in got.get("rules", [])) != sorted(r["type"] for r in want["rules"]):
            errors.append(f"{name}: creation/update/deletion restrictions mismatch")
        # GitHub omits bypass_actors unless the caller may manage the ruleset.
        # Missing is NOT an empty list: fail closed rather than claim immutability.
        if "bypass_actors" not in got:
            errors.append(f"{name}: bypass actors not visible; use admin-capable read access")
        elif got["bypass_actors"] != want["bypass_actors"]:
            errors.append(f"{name}: bypass actors mismatch")
    return errors


def get(token: str, endpoint: str) -> Any:
    req = urllib.request.Request(
        API + endpoint,
        method="GET",
        headers={"Accept": "application/vnd.github+json",
                 "Authorization": f"Bearer {token}",
                 "X-GitHub-Api-Version": "2022-11-28",
                 "User-Agent": "dubnium-community-tag-policy-check"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"GitHub ruleset read failed (HTTP {error.code})") from error


def read_tag_rulesets(token: str, repo: str) -> list[dict[str, Any]]:
    base = f"/repos/{repo}/rulesets"
    found: list[dict[str, Any]] = []
    for page in range(1, 5):
        summary = get(token, f"{base}?targets=tag&includes_parents=true&per_page=100&page={page}")
        if not isinstance(summary, list):
            raise RuntimeError("unexpected ruleset listing response")
        for row in summary:
            if row.get("target") != "tag":
                continue
            detail = get(token, f"{base}/{int(row['id'])}")
            if detail.get("target") != "tag":
                raise RuntimeError("ruleset target changed during read")
            found.append(detail)
        if len(summary) < 100:
            return found
    raise RuntimeError("ruleset listing exceeded bounded pagination; cannot prove completeness")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("plan", "check"))
    parser.add_argument("--creator-type", required=True, choices=CREATOR_TYPES)
    parser.add_argument("--creator-id", type=int, required=True)
    parser.add_argument("--repository", default=REPO)
    args = parser.parse_args(argv)
    expected = desired(args.creator_type, args.creator_id)
    if args.mode == "plan":
        print(json.dumps(expected, indent=2, sort_keys=True))
        return 0

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        parser.error("GH_TOKEN or GITHUB_TOKEN with ruleset read access is required")
    try:
        errors = validate_rulesets(read_tag_rulesets(token, args.repository), expected)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"contract tag ruleset verification failed: {error}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("contract tag rulesets active and verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
