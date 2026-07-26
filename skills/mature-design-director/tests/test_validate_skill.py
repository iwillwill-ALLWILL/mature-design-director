#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "maintenance" / "validate_skill.py"
SKILL = ROOT / "SKILL.md"
REGISTRY = ROOT / "references" / "capability-registry.json"
CATALOG = ROOT / "references" / "ecosystem-catalog.json"
SPDX = ROOT / "maintenance" / "spdx-license-ids.json"
AUDIT = ROOT / "maintenance" / "ecosystem-audit-baseline.json"
CREATIVE_SKILLS = ROOT / "references" / "creative-skill-sources.json"
sys.path.insert(0, str(ROOT / "maintenance"))
SPEC = importlib.util.spec_from_file_location("validate_skill", SCRIPT)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class ValidateSkillTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rows = json.loads(CATALOG.read_text(encoding="utf-8"))
        self.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_current_contracts_are_valid(self) -> None:
        VALIDATOR.validate_frontmatter(VALIDATOR.parse_frontmatter(SKILL.read_text(encoding="utf-8")))
        allowed = VALIDATOR.load_spdx_ids(SPDX)
        VALIDATOR.validate_catalog(self.rows, allowed_spdx=allowed)
        VALIDATOR.validate_capability_registry(self.registry, ROOT)
        VALIDATOR.validate_audit_baseline(json.loads(AUDIT.read_text(encoding="utf-8")), self.rows, ROOT)

    def test_json_loader_rejects_duplicate_keys_and_excessive_depth(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "input.json"
            path.write_text('{"value": 1, "value": 2}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                VALIDATOR.load_json_strict(path)
            path.write_text("[" * 2_000 + "0" + "]" * 2_000, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "JSON nesting"):
                VALIDATOR.load_json_strict(path)
            for constant in ("NaN", "Infinity", "-Infinity"):
                path.write_text(f"[{constant}]", encoding="utf-8")
                with self.subTest(constant=constant), self.assertRaisesRegex(ValueError, "non-standard JSON constant"):
                    VALIDATOR.load_json_strict(path)

    def test_creative_source_registry_types_fail_closed(self) -> None:
        data = json.loads(CREATIVE_SKILLS.read_text(encoding="utf-8"))
        bad = copy.deepcopy(data)
        bad["sources"][0]["url"] = 7
        with self.assertRaisesRegex(ValueError, "url"):
            VALIDATOR.validate_creative_skill_sources(bad)
        bad = copy.deepcopy(data)
        bad["sources"][0]["stars_at_verification"] = True
        with self.assertRaisesRegex(ValueError, "non-negative integer"):
            VALIDATOR.validate_creative_skill_sources(bad)
        bad = copy.deepcopy(data)
        bad["schema_version"] = True
        with self.assertRaisesRegex(ValueError, "schema_version"):
            VALIDATOR.validate_creative_skill_sources(bad)

    def test_natural_artifact_format_probes_reject_plain_text_with_allowed_suffixes(self) -> None:
        direct_suffixes = {
            suffix
            for capability in self.registry["capabilities"]
            for output in capability["outputs"]
            for suffix in output["artifact_suffixes"]
            if suffix != ".zip"
        }
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for suffix in sorted(direct_suffixes):
                artifact = root / f"disguised{suffix}"
                artifact.write_text("# README\nsource generator concept only\n", encoding="utf-8")
                with self.subTest(suffix=suffix):
                    with self.assertRaisesRegex(ValueError, "artifact format"):
                        VALIDATOR.validate_artifact_format(artifact)

    def test_registry_accepts_a_new_vertical_capability_without_validator_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "skill"
            shutil.copytree(ROOT, root)
            contract = root / "references" / "capabilities" / "haptic.md"
            contract.write_text("# Haptic Capability\n", encoding="utf-8")
            extended = copy.deepcopy(self.registry)
            extended["capabilities"].append(
                {
                    "id": "haptic",
                    "contract": "references/capabilities/haptic.md",
                    "accepts": ["tactile-feedback"],
                    "outputs": [
                        {
                            "id": "haptic-system",
                            "requires_foundations": ["tactile-language"],
                            "requires_delegates": ["runtime"],
                            "allowed_classifications": ["native-product"],
                            "artifact_suffixes": [".zip"],
                        }
                    ],
                    "foundations": [
                        {"role": "tactile-language", "sources": ["approved-haptic-pattern"]},
                    ],
                    "delegates": [{"role": "runtime", "candidates": ["actual-device-runtime"]}],
                    "evidence": ["working-artifact", "device-context"],
                }
            )
            VALIDATOR.validate_capability_registry(extended, root)

    def test_registry_rejects_unknown_evidence_duplicate_ids_and_escaping_paths(self) -> None:
        bad = copy.deepcopy(self.registry)
        bad["capabilities"][0]["evidence"].append("invented-proof")
        with self.assertRaisesRegex(ValueError, "unknown evidence"):
            VALIDATOR.validate_capability_registry(bad, ROOT)
        bad = copy.deepcopy(self.registry)
        bad["capabilities"][1]["id"] = bad["capabilities"][0]["id"]
        with self.assertRaisesRegex(ValueError, "unique slug"):
            VALIDATOR.validate_capability_registry(bad, ROOT)
        bad = copy.deepcopy(self.registry)
        bad["capabilities"][0]["contract"] = "../outside.md"
        with self.assertRaisesRegex(ValueError, "escapes"):
            VALIDATOR.validate_capability_registry(bad, ROOT)
        bad = copy.deepcopy(self.registry)
        bad["artifact_lifecycle"]["initial_state"] = []
        with self.assertRaisesRegex(ValueError, "initial_state"):
            VALIDATOR.validate_capability_registry(bad, ROOT)
        bad = copy.deepcopy(self.registry)
        bad["artifact_lifecycle"]["transitions"][0]["from"] = []
        with self.assertRaisesRegex(ValueError, "transition.*invalid state"):
            VALIDATOR.validate_capability_registry(bad, ROOT)
        bad = copy.deepcopy(self.registry)
        bad["artifact_lifecycle"]["rejection_transition"]["to"] = []
        with self.assertRaisesRegex(ValueError, "rejection transition"):
            VALIDATOR.validate_capability_registry(bad, ROOT)

    def test_audit_baseline_binds_inputs_rows_and_status_semantics(self) -> None:
        baseline = json.loads(AUDIT.read_text(encoding="utf-8"))
        bad = copy.deepcopy(baseline)
        bad["audit_metadata"]["catalog_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "catalog hash"):
            VALIDATOR.validate_audit_baseline(bad, self.rows, ROOT)
        bad = copy.deepcopy(baseline)
        bad["audit_metadata"]["status_counts"]["OK"] += 1
        with self.assertRaisesRegex(ValueError, "status counts"):
            VALIDATOR.validate_audit_baseline(bad, self.rows, ROOT)
        bad = copy.deepcopy(baseline)
        bad["rows"][0]["name"] = "tampered"
        with self.assertRaisesRegex(ValueError, "catalog fields differ"):
            VALIDATOR.validate_audit_baseline(bad, self.rows, ROOT)
        bad = copy.deepcopy(baseline)
        bad["rows"][0].pop("archived")
        with self.assertRaisesRegex(ValueError, "fields are missing"):
            VALIDATOR.validate_audit_baseline(bad, self.rows, ROOT)
        bad = copy.deepcopy(baseline)
        bad["rows"][0]["live_license"] = "NOASSERTION"
        with self.assertRaisesRegex(ValueError, "license status is inconsistent"):
            VALIDATOR.validate_audit_baseline(bad, self.rows, ROOT)

    def test_frontmatter_is_strict_and_versioned(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicates name"):
            VALIDATOR.parse_frontmatter("---\nname: one\nname: two\n---\n")
        frontmatter = VALIDATOR.parse_frontmatter(SKILL.read_text(encoding="utf-8"))
        frontmatter["version"] = "3.0"
        with self.assertRaisesRegex(ValueError, "semantic"):
            VALIDATOR.validate_frontmatter(frontmatter)
        malformed = [
            ("---\nname: x\n    child: y\n---\n", "jumps or attaches"),
            ("---\n\tname: x\n---\n", "contains a tab"),
            ('---\nname: "unterminated\n---\n', "unterminated"),
            ("---\nplatforms: [linux\n---\n", "unterminated inline list"),
        ]
        for text, message in malformed:
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                VALIDATOR.parse_frontmatter(text)

    def test_catalog_rejects_schema_repository_url_date_and_license_drift(self) -> None:
        row = copy.deepcopy(self.rows[0])
        row.pop("layer_family")
        with self.assertRaisesRegex(ValueError, "missing"):
            VALIDATOR.validate_catalog([row])
        mutations = [
            ("repository", "not-a-repository", "repository"),
            ("official_url", "http://example.com", "HTTPS"),
            ("license_source_url", "http://example.com/license", "HTTPS"),
            ("last_verified", "not-a-date", "ISO"),
            ("license_verified_at", "not-a-date", "ISO"),
            ("accepted_spdx", ["not-valid"], "SPDX"),
            ("accepted_spdx", [{}], "SPDX"),
        ]
        for field, value, message in mutations:
            with self.subTest(field=field):
                row = copy.deepcopy(self.rows[0])
                row[field] = value
                with self.assertRaisesRegex(ValueError, message):
                    VALIDATOR.validate_catalog([row])
        row = copy.deepcopy(self.rows[0])
        row["license_verified_at"] = (date.today() + timedelta(days=1)).isoformat()
        with self.assertRaisesRegex(ValueError, "future"):
            VALIDATOR.validate_catalog([row])

    def test_catalog_identity_is_provider_aware_and_casefolded(self) -> None:
        github = copy.deepcopy(self.rows[0])
        gitlab = copy.deepcopy(github)
        gitlab.update(
            {
                "name": f"{github['name']} GitLab mirror",
                "repository_provider": "gitlab",
                "license_source_url": f"https://gitlab.com/{github['repository']}/-/raw/main/LICENSE",
            }
        )
        VALIDATOR.validate_catalog([github, gitlab])
        github["repository"] = "group/subgroup/project"
        with self.assertRaisesRegex(ValueError, "repository shape"):
            VALIDATOR.validate_catalog([github])
        for repository in ("owner/.", "owner/..", "./repo", "../repo", "owner/_bad"):
            with self.subTest(repository=repository):
                github["repository"] = repository
                with self.assertRaisesRegex(ValueError, "repository"):
                    VALIDATOR.validate_catalog([github])
        first = copy.deepcopy(self.rows[0])
        second = copy.deepcopy(first)
        second["name"] = f"{first['name']} case mirror"
        second["repository"] = first["repository"].swapcase()
        with self.assertRaisesRegex(ValueError, "provider/repository identity"):
            VALIDATOR.validate_catalog([first, second])

    def test_spdx_policy_is_self_describing_and_fail_closed(self) -> None:
        allowed = VALIDATOR.load_spdx_ids(SPDX)
        self.assertIn("MIT", allowed)
        self.assertNotIn("NOASSERTION", allowed)
        for token in ("Definitely-Not-SPDX", "NOASSERTION", "LicenseRef-Private", "MIT OR Apache-2.0"):
            row = copy.deepcopy(self.rows[0])
            row["accepted_spdx"] = [token]
            row["manual_license_review"] = False
            with self.subTest(token=token), self.assertRaisesRegex(ValueError, "SPDX"):
                VALIDATOR.validate_catalog([row], allowed_spdx=allowed)
        with tempfile.TemporaryDirectory() as temp:
            policy = json.loads(SPDX.read_text(encoding="utf-8"))
            policy["license_ids"].append("Definitely-Not-SPDX")
            policy["license_ids"] = sorted(policy["license_ids"])
            path = Path(temp) / "spdx.json"
            path.write_text(json.dumps(policy), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "differs from the declared set"):
                VALIDATOR.load_spdx_ids(path)
            policy["license_ids"] = sorted(policy["license_ids"])
            policy["license_ids_sha256"] = hashlib.sha256(
                ("\n".join(policy["license_ids"]) + "\n").encode()
            ).hexdigest()
            path.write_text(json.dumps(policy), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "forbidden"):
                policy["license_ids"].append("NOASSERTION")
                policy["license_ids"] = sorted(policy["license_ids"])
                policy["license_ids_sha256"] = hashlib.sha256(
                    ("\n".join(policy["license_ids"]) + "\n").encode()
                ).hexdigest()
                path.write_text(json.dumps(policy), encoding="utf-8")
                VALIDATOR.load_spdx_ids(path)

    def test_internal_links_reject_missing_and_escape_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            doc = root / "commands.md"
            doc.write_text("[missing](missing.md)\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "broken local link"):
                VALIDATOR.validate_internal_links(root)
            doc.write_text("[escape](../outside.md)\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "outside skill"):
                VALIDATOR.validate_internal_links(root)
            (root / "scripts").mkdir()
            (root / "scripts" / "real.py").write_text("pass\n", encoding="utf-8")
            doc.write_text("```bash\npython <skill-root>/scripts/real.py\n```\n", encoding="utf-8")
            VALIDATOR.validate_internal_links(root)
            doc.write_text("```bash\npython <skill-root>/scripts/missing.py\n```\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "broken local link"):
                VALIDATOR.validate_internal_links(root)

    def test_cli_returns_nonzero_for_invalid_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "skill"
            shutil.copytree(ROOT, root)
            skill = root / "SKILL.md"
            skill.write_text(
                skill.read_text(encoding="utf-8").replace(
                    "name: mature-design-director", 'name: "unterminated', 1
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(root)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("validation failed", result.stderr)


if __name__ == "__main__":
    unittest.main()