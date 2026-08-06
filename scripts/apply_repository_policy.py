#!/usr/bin/env python3
"""Apply and verify Dubnium Community repository protection through GitHub REST."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any

API = "https://api.github.com"
DEFAULT_REPOSITORY = "hackelia-micrantha/dubnium-community"
REQUIRED_CHECKS = [
    "Contract CI / contract-gate",
    "Contract Release CI / consume-release",
    "Repository Policy",
]


def repository_settings() -> dict[str, Any]:
    return {
        "allow_merge_commit": False,
        "allow_rebase_merge": False,
        "allow_squash_merge": True,
        "allow_auto_merge": False,
        "delete_branch_on_merge": True,
    }


def branch_protection() -> dict[str, Any]:
    return {
        "required_status_checks": {"strict": True, "contexts": REQUIRED_CHECKS},
        "enforce_admins": True,
        "required_pull_request_reviews": {
            "dismiss_stale_reviews": True,
            "require_code_owner_reviews": False,
            "required_approving_review_count": 0,
            "require_last_push_approval": False,
        },
        "restrictions": None,
        "required_linear_history": True,
        "allow_force_pushes": False,
        "allow_deletions": False,
        "block_creations": False,
        "required_conversation_resolution": True,
        "lock_branch": False,
        "allow_fork_syncing": False,
    }


def request(token: str, method: str, path: str, body: dict[str, Any] | None = None) -> Any:
    data = None if body is None else json.dumps(body, sort_keys=True).encode("utf-8")
    req = urllib.request.Request(
        API + path,
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "dubnium-community-policy-tool",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {method} {path} failed: {exc.code} {detail}") from exc
    return None if not raw else json.loads(raw)


def normalized_active(repo: dict[str, Any], protection: dict[str, Any]) -> dict[str, Any]:
    contexts = protection.get("required_status_checks", {}).get("contexts", [])
    reviews = protection.get("required_pull_request_reviews") or {}
    return {
        "repository": {
            key: repo.get(key)
            for key in repository_settings()
        },
        "main": {
            "strict": protection.get("required_status_checks", {}).get("strict"),
            "contexts": sorted(contexts),
            "enforce_admins": protection.get("enforce_admins", {}).get("enabled"),
            "dismiss_stale_reviews": reviews.get("dismiss_stale_reviews"),
            "required_approving_review_count": reviews.get("required_approving_review_count"),
            "required_linear_history": protection.get("required_linear_history", {}).get("enabled"),
            "allow_force_pushes": protection.get("allow_force_pushes", {}).get("enabled"),
            "allow_deletions": protection.get("allow_deletions", {}).get("enabled"),
            "required_conversation_resolution": protection.get("required_conversation_resolution", {}).get("enabled"),
        },
    }


def expected_active() -> dict[str, Any]:
    return {
        "repository": repository_settings(),
        "main": {
            "strict": True,
            "contexts": sorted(REQUIRED_CHECKS),
            "enforce_admins": True,
            "dismiss_stale_reviews": True,
            "required_approving_review_count": 0,
            "required_linear_history": True,
            "allow_force_pushes": False,
            "allow_deletions": False,
            "required_conversation_resolution": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("plan", "apply", "check"))
    parser.add_argument("--repository", default=DEFAULT_REPOSITORY)
    args = parser.parse_args()

    if args.mode == "plan":
        print(json.dumps({"repository": repository_settings(), "main": branch_protection()}, indent=2, sort_keys=True))
        return 0

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        parser.error("GH_TOKEN or GITHUB_TOKEN with repository administration permission is required")

    repo_path = f"/repos/{args.repository}"
    protection_path = f"{repo_path}/branches/main/protection"
    if args.mode == "apply":
        request(token, "PATCH", repo_path, repository_settings())
        request(token, "PUT", protection_path, branch_protection())

    active = normalized_active(
        request(token, "GET", repo_path),
        request(token, "GET", protection_path),
    )
    expected = expected_active()
    if active != expected:
        print("repository policy mismatch", file=sys.stderr)
        print(json.dumps({"expected": expected, "active": active}, indent=2, sort_keys=True), file=sys.stderr)
        return 1
    print("repository policy active and verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
