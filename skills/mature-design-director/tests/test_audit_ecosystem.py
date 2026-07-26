#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import hashlib
import io
import json
import os
import subprocess
import sys
import unittest
import urllib.error
import tempfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "maintenance" / "audit_ecosystem.py"
CATALOG = ROOT / "references" / "ecosystem-catalog.json"
SPDX_POLICY = ROOT / "maintenance" / "spdx-license-ids.json"
sys.path.insert(0, str(ROOT / "maintenance"))
SPEC = importlib.util.spec_from_file_location("audit_ecosystem", SCRIPT)
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class AuditEcosystemTests(unittest.TestCase):
    def test_license_policy_is_exact_and_fail_closed(self) -> None:
        cases = [
            ("MIT", ["MIT"], False, "MATCH"),
            ("NOASSERTION", ["MIT"], False, "MANUAL_REVIEW"),
            ("LGPL-2.1", ["LGPL-2.1-or-later"], False, "MISMATCH"),
            ("GPL-3.0", ["GPL-3.0"], False, "MATCH"),
            ("MIT", ["MIT"], True, "MANUAL_REVIEW"),
        ]
        for live, accepted, manual, expected in cases:
            with self.subTest(live=live, accepted=accepted, manual=manual):
                self.assertEqual(AUDIT.license_status(live, accepted, manual), expected)

    def test_strict_exit_codes(self) -> None:
        self.assertEqual(AUDIT.strict_exit_code([{"status": "OK"}], []), 0)
        self.assertEqual(AUDIT.strict_exit_code([{"status": "LICENSE_REVIEW"}], []), 2)
        self.assertEqual(AUDIT.strict_exit_code([{"status": "REPOSITORY_REVIEW"}], []), 2)
        self.assertEqual(AUDIT.strict_exit_code([{"status": "OK"}], [{"error": "x"}]), 1)

    def test_repository_status_prioritizes_archived_and_stale_over_unknown_metadata(self) -> None:
        self.assertEqual(AUDIT.repository_status(True, 900, 730, "MATCH"), "ARCHIVED")
        self.assertEqual(AUDIT.repository_status(None, 900, 730, "MANUAL_REVIEW"), "STALE_REVIEW")
        self.assertEqual(AUDIT.repository_status(None, 1, 730, "MATCH"), "REPOSITORY_REVIEW")
        self.assertEqual(AUDIT.repository_status(False, 1, 730, "MANUAL_REVIEW"), "LICENSE_REVIEW")
        for archived in ("false", 0, [], {}):
            with self.subTest(archived=archived):
                self.assertEqual(
                    AUDIT.repository_status(archived, 1, 730, "MATCH"),
                    "REPOSITORY_REVIEW",
                )

    def test_main_strict_exit_rejects_non_boolean_archived_metadata(self) -> None:
        row = json.loads(CATALOG.read_text(encoding="utf-8"))[0]
        argv = [str(SCRIPT), "--layer", row["layer"], "--json"]
        with mock.patch.object(sys, "argv", argv), mock.patch.object(
            AUDIT, "gh_authenticated", return_value=True
        ), mock.patch.object(
            AUDIT, "repository_metadata",
            return_value={
                "pushed_at": "2026-07-25T00:00:00Z",
                "archived": "false",
                "license": {"spdx_id": row["accepted_spdx"][0]},
            },
        ), mock.patch("sys.stdout", new_callable=io.StringIO) as stdout:
            with self.assertRaises(SystemExit) as raised:
                AUDIT.main()
        self.assertEqual(raised.exception.code, 2)
        payload = json.loads(stdout.getvalue())
        self.assertTrue(payload["rows"])
        self.assertTrue(all(item["status"] == "REPOSITORY_REVIEW" for item in payload["rows"]))
        self.assertTrue(all("code_updated_at" in item for item in payload["rows"]))
        self.assertTrue(all("pushed_at" not in item for item in payload["rows"]))

    def test_gh_authentication_detection(self) -> None:
        with mock.patch.object(AUDIT.shutil, "which", return_value=None):
            self.assertFalse(AUDIT.gh_authenticated())
        completed = subprocess.CompletedProcess(["gh", "auth", "status"], 0, "", "")
        with mock.patch.object(AUDIT.shutil, "which", return_value="/usr/bin/gh"), mock.patch.object(
            AUDIT.subprocess, "run", return_value=completed
        ):
            self.assertTrue(AUDIT.gh_authenticated())

    def test_gh_path_retries_three_times_without_fallback(self) -> None:
        failed = subprocess.CompletedProcess(["gh", "api"], 1, "", "transient")
        with mock.patch.object(AUDIT.subprocess, "run", return_value=failed) as run, mock.patch.object(
            AUDIT.urllib.request, "urlopen"
        ) as urlopen, mock.patch.object(AUDIT.time, "sleep") as sleep:
            with self.assertRaisesRegex(RuntimeError, "transient"):
                AUDIT.gh_repo("owner/repo", use_gh=True)
        self.assertEqual(run.call_count, 3)
        self.assertEqual(sleep.call_count, 2)
        urlopen.assert_not_called()

    def test_rest_fallback_retries_then_succeeds(self) -> None:
        payload = io.BytesIO(json.dumps({"name": "repo"}).encode())
        with mock.patch.object(
            AUDIT.urllib.request,
            "urlopen",
            side_effect=[urllib.error.URLError("reset"), payload],
        ) as urlopen, mock.patch.object(AUDIT.time, "sleep") as sleep:
            self.assertEqual(AUDIT.gh_repo("owner/repo", use_gh=False), {"name": "repo"})
        self.assertEqual(urlopen.call_count, 2)
        self.assertEqual(sleep.call_count, 1)

    def test_gitlab_repository_metadata_is_normalized_and_url_encoded(self) -> None:
        project_payload = io.BytesIO(
            json.dumps(
                {
                    "path_with_namespace": "group/subgroup/project",
                    "last_activity_at": "2026-07-25T15:04:45.828Z",
                    "archived": False,
                }
            ).encode()
        )
        commit_payload = io.BytesIO(
            json.dumps([{"committed_date": "2024-01-02T03:04:05.000Z"}]).encode()
        )
        with mock.patch.object(
            AUDIT.urllib.request, "urlopen", side_effect=[project_payload, commit_payload]
        ) as urlopen:
            live = AUDIT.repository_metadata("group/subgroup/project", "gitlab", use_gh=False)
        self.assertEqual(live["pushed_at"], "2024-01-02T03:04:05.000Z")
        self.assertEqual(live["license"]["spdx_id"], "NOASSERTION")
        self.assertFalse(live["archived"])
        requests = [call.args[0].full_url for call in urlopen.call_args_list]
        self.assertIn("group%2Fsubgroup%2Fproject", requests[0])
        self.assertIn("group%2Fsubgroup%2Fproject/repository/commits", requests[1])
        self.assertIn("per_page=1", requests[1])

    def test_gitlab_repository_metadata_retries_transient_failures(self) -> None:
        project_payload = io.BytesIO(json.dumps({"archived": False}).encode())
        commit_payload = io.BytesIO(
            json.dumps([{"committed_date": "2026-07-25T15:04:45.828Z"}]).encode()
        )
        with mock.patch.object(
            AUDIT.urllib.request,
            "urlopen",
            side_effect=[urllib.error.URLError("reset"), project_payload, commit_payload],
        ) as urlopen, mock.patch.object(AUDIT.time, "sleep") as sleep:
            live = AUDIT.repository_metadata("scribus/scribus", "gitlab", use_gh=False)
        self.assertEqual(live["pushed_at"], "2026-07-25T15:04:45.828Z")
        self.assertEqual(urlopen.call_count, 3)
        self.assertEqual(sleep.call_count, 1)

    def test_gitlab_repository_metadata_retries_direct_timeout(self) -> None:
        project_payload = io.BytesIO(json.dumps({"archived": False}).encode())
        commit_payload = io.BytesIO(
            json.dumps([{"committed_date": "2026-07-25T15:04:45.828Z"}]).encode()
        )
        with mock.patch.object(
            AUDIT.urllib.request,
            "urlopen",
            side_effect=[TimeoutError("timed out"), project_payload, commit_payload],
        ) as urlopen, mock.patch.object(AUDIT.time, "sleep") as sleep:
            live = AUDIT.repository_metadata("inkscape/inkscape", "gitlab", use_gh=False)
        self.assertEqual(live["pushed_at"], "2026-07-25T15:04:45.828Z")
        self.assertEqual(urlopen.call_count, 3)
        self.assertEqual(sleep.call_count, 1)

    def test_catalog_schema_and_baseline(self) -> None:
        rows = json.loads(CATALOG.read_text(encoding="utf-8"))
        self.assertEqual(len(rows), 104)
        self.assertEqual(len({row["layer"] for row in rows}), 63)
        self.assertEqual(len({row["layer_family"] for row in rows}), 14)
        self.assertEqual(
            {provider: sum(row.get("repository_provider", "github") == provider for row in rows)
             for provider in ("github", "gitlab")},
            {"github": 102, "gitlab": 2},
        )
        self.assertEqual(len({row["name"] for row in rows}), len(rows))
        self.assertEqual(len({row["repository"] for row in rows}), len(rows))
        for row in rows:
            self.assertIsInstance(row["layer_family"], str)
            self.assertTrue(row["layer_family"])
            self.assertIsInstance(row["tags"], list)
            self.assertTrue(row["tags"])
            self.assertTrue(row["license_source_url"].startswith("https://"))
            self.assertRegex(row["license_verified_at"], r"^\d{4}-\d{2}-\d{2}$")
            self.assertIsInstance(row["accepted_spdx"], list)
            self.assertTrue(all(isinstance(value, str) for value in row["accepted_spdx"]))
            self.assertIsInstance(row["manual_license_review"], bool)

    def test_family_filter_keeps_related_layers_without_cross_family_rows(self) -> None:
        rows = json.loads(CATALOG.read_text(encoding="utf-8"))
        selected = AUDIT.select_catalog(rows, layer=None, family="game-development")
        self.assertEqual(len(selected), 7)
        self.assertEqual({row["layer"] for row in selected}, {"game-engine", "sprite-editor"})
        self.assertTrue(all(row["layer_family"] == "game-development" for row in selected))

    def test_unknown_layer_fails_before_network(self) -> None:
        env = {**os.environ, "PATH": "/nonexistent"}
        env.pop("GITHUB_TOKEN", None)
        env.pop("GH_TOKEN", None)
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--layer", "does-not-exist"],
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown layer", result.stderr)

    def test_custom_catalog_reuses_strict_validator_before_network(self) -> None:
        base = json.loads(CATALOG.read_text(encoding="utf-8"))[0]
        mutations = (
            ("unknown", lambda row: row.update({"unexpected": True})),
            ("future", lambda row: row.update({"last_verified": "2999-01-01"})),
            ("repository", lambda row: row.update({"repository": "group/subgroup/project"})),
            ("HTTPS", lambda row: row.update({"official_url": "http://invalid.example"})),
        )
        env = {**os.environ, "PATH": "/nonexistent"}
        env.pop("GITHUB_TOKEN", None)
        env.pop("GH_TOKEN", None)
        for expected, mutate in mutations:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as temp:
                row = json.loads(json.dumps(base))
                mutate(row)
                path = Path(temp) / "catalog.json"
                path.write_text(json.dumps([row]), encoding="utf-8")
                result = subprocess.run(
                    [sys.executable, str(SCRIPT), "--catalog", str(path), "--json"],
                    text=True,
                    capture_output=True,
                    env=env,
                    check=False,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stderr)

    def test_full_anonymous_audit_fails_before_network(self) -> None:
        env = {**os.environ, "PATH": "/nonexistent"}
        env.pop("GITHUB_TOKEN", None)
        env.pop("GH_TOKEN", None)
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("anonymous REST limit", result.stderr)

    def test_cli_rejects_tampered_spdx_policy_before_network(self) -> None:
        env = {**os.environ, "PATH": "/nonexistent"}
        env.pop("GITHUB_TOKEN", None)
        env.pop("GH_TOKEN", None)
        original_policy = json.loads(SPDX_POLICY.read_text(encoding="utf-8"))
        original_catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        for token in (
            "NOASSERTION", "LicenseRef-Private", "DocumentRef-X", "MIT OR Apache-2.0",
        ):
            with self.subTest(token=token), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                policy = json.loads(json.dumps(original_policy))
                policy["license_ids"].append(token)
                policy["license_ids"].sort()
                policy["license_ids_sha256"] = hashlib.sha256(
                    ("\n".join(policy["license_ids"]) + "\n").encode()
                ).hexdigest()
                policy_path = root / "policy.json"
                policy_path.write_text(json.dumps(policy), encoding="utf-8")
                catalog = json.loads(json.dumps(original_catalog))
                catalog[0]["accepted_spdx"] = [token]
                catalog_path = root / "catalog.json"
                catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
                result = subprocess.run(
                    [
                        sys.executable, str(SCRIPT), "--catalog", str(catalog_path),
                        "--spdx-policy", str(policy_path), "--layer", catalog[0]["layer"],
                    ],
                    text=True,
                    capture_output=True,
                    env=env,
                    check=False,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("invalid SPDX identifier policy", result.stderr)

    def test_tampered_policy_cannot_reach_any_network_entry_point(self) -> None:
        original_policy = json.loads(SPDX_POLICY.read_text(encoding="utf-8"))
        original_catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        for token in (
            "NOASSERTION", "LicenseRef-Private", "DocumentRef-X", "MIT OR Apache-2.0",
        ):
            with self.subTest(token=token), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                policy = json.loads(json.dumps(original_policy))
                policy["license_ids"].append(token)
                policy["license_ids"].sort()
                policy["license_ids_sha256"] = hashlib.sha256(
                    ("\n".join(policy["license_ids"]) + "\n").encode()
                ).hexdigest()
                policy_path = root / "policy.json"
                policy_path.write_text(json.dumps(policy), encoding="utf-8")
                catalog = json.loads(json.dumps(original_catalog))
                catalog[0]["accepted_spdx"] = [token]
                catalog_path = root / "catalog.json"
                catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
                argv = [
                    str(SCRIPT), "--catalog", str(catalog_path),
                    "--spdx-policy", str(policy_path), "--layer", catalog[0]["layer"],
                ]
                with mock.patch.object(sys, "argv", argv), mock.patch.object(
                    AUDIT, "gh_authenticated"
                ) as auth, mock.patch.object(AUDIT, "gh_repo") as repo, mock.patch.object(
                    AUDIT.urllib.request, "urlopen"
                ) as urlopen:
                    with self.assertRaisesRegex(SystemExit, "invalid SPDX identifier policy"):
                        AUDIT.main()
                auth.assert_not_called()
                repo.assert_not_called()
                urlopen.assert_not_called()

    def test_unknown_family_and_invalid_max_age_fail_before_network(self) -> None:
        env = {**os.environ, "PATH": "/nonexistent"}
        env.pop("GITHUB_TOKEN", None)
        env.pop("GH_TOKEN", None)
        unknown = subprocess.run(
            [sys.executable, str(SCRIPT), "--family", "does-not-exist"],
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )
        self.assertNotEqual(unknown.returncode, 0)
        self.assertIn("unknown family", unknown.stderr)
        invalid_age = subprocess.run(
            [sys.executable, str(SCRIPT), "--max-age-days", "0"],
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )
        self.assertNotEqual(invalid_age.returncode, 0)
        self.assertIn("greater than zero", invalid_age.stderr)


if __name__ == "__main__":
    unittest.main()
