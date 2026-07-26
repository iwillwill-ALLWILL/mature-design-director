#!/usr/bin/env python3
"""Read-only live audit for governed repository sources in the design ecosystem catalog."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional

from validate_skill import load_spdx_ids, validate_catalog

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "references" / "ecosystem-catalog.json"
SPDX_POLICY = ROOT / "references" / "spdx-license-ids.json"


def audit_metadata(
    catalog_path: Path,
    catalog_count: int,
    rows: list[dict],
    failures: list[dict],
    max_age_days: int,
) -> dict:
    status_counts: dict[str, int] = {}
    for row in rows:
        status = row["status"]
        status_counts[status] = status_counts.get(status, 0) + 1
    return {
        "schema_version": 1,
        "audited_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "catalog_sha256": hashlib.sha256(catalog_path.read_bytes()).hexdigest(),
        "auditor_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "catalog_count": catalog_count,
        "selected_count": len(rows) + len(failures),
        "max_age_days": max_age_days,
        "status_counts": dict(sorted(status_counts.items())),
        "failure_count": len(failures),
    }


def gh_authenticated() -> bool:
    if not shutil.which("gh"):
        return False
    result = subprocess.run(
        ["gh", "auth", "status"], text=True, capture_output=True, check=False
    )
    return result.returncode == 0


def gh_repo(name: str, use_gh: bool) -> dict:
    last_error: Optional[Exception] = None
    for attempt in range(3):
        try:
            if use_gh:
                result = subprocess.run(
                    ["gh", "api", f"repos/{name}"], text=True, capture_output=True, check=False
                )
                if result.returncode:
                    raise RuntimeError(result.stderr.strip() or result.stdout.strip())
                return json.loads(result.stdout)

            headers = {
                "Accept": "application/vnd.github+json",
                "User-Agent": "mature-design-director-ecosystem-audit",
            }
            token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
            if token:
                headers["Authorization"] = f"Bearer {token}"
            request = urllib.request.Request(f"https://api.github.com/repos/{name}", headers=headers)
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            last_error = RuntimeError(f"GitHub API HTTP {exc.code}")
        except urllib.error.URLError as exc:
            last_error = RuntimeError(f"GitHub API unavailable: {exc.reason}")
        except (RuntimeError, json.JSONDecodeError) as exc:
            last_error = exc
        if attempt < 2:
            time.sleep(2**attempt)
    raise RuntimeError(str(last_error) if last_error else "unknown GitHub API failure")


def _gitlab_json(url: str) -> object:
    last_error: Optional[Exception] = None
    for attempt in range(3):
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "mature-design-director-ecosystem-audit"},
            )
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            last_error = RuntimeError(f"GitLab API HTTP {exc.code}")
        except urllib.error.URLError as exc:
            last_error = RuntimeError(f"GitLab API unavailable: {exc.reason}")
        except TimeoutError as exc:
            last_error = RuntimeError(f"GitLab API timed out: {exc}")
        except (RuntimeError, json.JSONDecodeError) as exc:
            last_error = exc
        if attempt < 2:
            time.sleep(2**attempt)
    raise RuntimeError(str(last_error) if last_error else "unknown GitLab API failure")


def gitlab_repo(name: str) -> dict:
    encoded = urllib.parse.quote(name, safe="")
    base = f"https://gitlab.com/api/v4/projects/{encoded}"
    live = _gitlab_json(base)
    commits = _gitlab_json(f"{base}/repository/commits?per_page=1")
    if not isinstance(live, dict):
        raise RuntimeError("GitLab project metadata is not an object")
    if not isinstance(commits, list) or not commits or not isinstance(commits[0], dict):
        raise RuntimeError("GitLab repository has no latest commit metadata")
    pushed_at = commits[0].get("committed_date")
    if not isinstance(pushed_at, str):
        raise RuntimeError("GitLab latest commit metadata has no committed_date")
    return {
        "pushed_at": pushed_at,
        "archived": live.get("archived"),
        "license": {"spdx_id": "NOASSERTION"},
    }


def repository_metadata(name: str, provider: str, use_gh: bool) -> dict:
    if provider == "github":
        return gh_repo(name, use_gh)
    if provider == "gitlab":
        return gitlab_repo(name)
    raise RuntimeError(f"unsupported repository provider: {provider}")


def age_days(timestamp: str) -> int:
    value = dt.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    return (dt.datetime.now(dt.timezone.utc) - value).days


def license_status(live_spdx: str, accepted_spdx: list[str], manual_review: bool) -> str:
    if live_spdx == "NOASSERTION" or manual_review:
        return "MANUAL_REVIEW"
    return "MATCH" if live_spdx in accepted_spdx else "MISMATCH"


def strict_exit_code(rows: list[dict], failures: list[dict]) -> int:
    if failures:
        return 1
    if any(row["status"] != "OK" for row in rows):
        return 2
    return 0


def repository_status(
    archived: object, age: int, max_age_days: int, live_license_status: str
) -> str:
    if archived is True:
        return "ARCHIVED"
    if age > max_age_days:
        return "STALE_REVIEW"
    if not isinstance(archived, bool):
        return "REPOSITORY_REVIEW"
    if live_license_status != "MATCH":
        return "LICENSE_REVIEW"
    return "OK"


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def select_catalog(catalog: list[dict], layer: Optional[str], family: Optional[str]) -> list[dict]:
    selected = [
        item for item in catalog
        if (not layer or item["layer"] == layer)
        and (not family or item["layer_family"] == family)
    ]
    if layer and not selected:
        available = ", ".join(sorted({item["layer"] for item in catalog}))
        raise ValueError(f"unknown layer {layer!r}; available layers: {available}")
    if family and not selected:
        available = ", ".join(sorted({item["layer_family"] for item in catalog}))
        raise ValueError(f"unknown family {family!r}; available families: {available}")
    return selected


def main() -> None:
    parser = argparse.ArgumentParser()
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--layer", help="Only audit one exact catalog layer")
    scope.add_argument("--family", help="Audit every layer in one catalog family")
    parser.add_argument("--max-age-days", type=positive_int, default=730)
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit JSON")
    parser.add_argument("--catalog", type=Path, default=CATALOG, help="catalog JSON path")
    parser.add_argument("--spdx-policy", type=Path, default=SPDX_POLICY, help="versioned SPDX policy path")
    args = parser.parse_args()

    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    try:
        allowed_spdx = load_spdx_ids(args.spdx_policy)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid SPDX identifier policy: {exc}") from exc
    if not isinstance(catalog, list):
        raise SystemExit("catalog must be a JSON list")
    try:
        validate_catalog(catalog, allowed_spdx=allowed_spdx)
    except ValueError as exc:
        raise SystemExit(f"invalid catalog: {exc}") from exc

    try:
        selected = select_catalog(catalog, args.layer, args.family)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    use_gh = gh_authenticated()
    has_api_token = bool(os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"))
    selected_github = sum(row.get("repository_provider", "github") == "github" for row in selected)
    if not use_gh and not has_api_token and selected_github > 50:
        raise SystemExit(
            "full catalog audit exceeds GitHub's anonymous REST limit; install and authenticate gh "
            "or set GITHUB_TOKEN/GH_TOKEN, or audit one --layer"
        )

    rows, failures = [], []
    for item in selected:
        try:
            provider = item.get("repository_provider", "github")
            live = repository_metadata(item["repository"], provider, use_gh)
            license_id = (live.get("license") or {}).get("spdx_id") or "NOASSERTION"
            live_license_status = license_status(
                license_id, item["accepted_spdx"], item["manual_license_review"]
            )
            code_updated_at = live.get("pushed_at") or live.get("updated_at")
            if not isinstance(code_updated_at, str):
                raise RuntimeError("repository metadata has no timestamp")
            age = age_days(code_updated_at)
            status = repository_status(
                live.get("archived"), age, args.max_age_days, live_license_status
            )
            rows.append(
                {
                    "name": item["name"],
                    "layer": item["layer"],
                    "layer_family": item["layer_family"],
                    "repository": item["repository"],
                    "repository_provider": provider,
                    "catalog_license": item["license_hint"],
                    "license_source_url": item["license_source_url"],
                    "license_verified_at": item["license_verified_at"],
                    "live_license": license_id,
                    "license_status": live_license_status,
                    "code_updated_at": code_updated_at,
                    "age_days": age,
                    "archived": live.get("archived"),
                    "status": status,
                }
            )
        except Exception as exc:  # keep auditing the remaining catalog
            failures.append({"repository": item["repository"], "error": str(exc)})

    if args.as_json:
        print(
            json.dumps(
                {
                    "audit_metadata": audit_metadata(
                        args.catalog, len(catalog), rows, failures, args.max_age_days
                    ),
                    "rows": rows,
                    "failures": failures,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print("| Project | Family | Layer | Live license | License check | Last code update | Age | Status |")
        print("|---|---|---|---|---|---|---:|---|")
        for row in rows:
            print(
                f"| {row['name']} | {row['layer_family']} | {row['layer']} | "
                f"{row['live_license']} | {row['license_status']} | "
                f"{row['code_updated_at'][:10]} | {row['age_days']}d | {row['status']} |"
            )
        if failures:
            print("\nFailures:")
            for failure in failures:
                print(f"- {failure['repository']}: {failure['error']}")
        issues = sum(row["status"] != "OK" for row in rows)
        print(f"Audited {len(rows)} projects; issues={issues}; failures={len(failures)}")
    raise SystemExit(strict_exit_code(rows, failures))


if __name__ == "__main__":
    main()
