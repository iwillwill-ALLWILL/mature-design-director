#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import importlib.metadata
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "references" / "capability-registry.json"
VALIDATOR_PATH = ROOT / "maintenance" / "validate_skill.py"

sys.path.insert(0, str(ROOT / "maintenance"))
SPEC = importlib.util.spec_from_file_location("validate_skill_v4", VALIDATOR_PATH)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class VerticalArchitectureTests(unittest.TestCase):
    def test_registry_is_the_only_routing_source(self) -> None:
        self.assertTrue(REGISTRY.is_file())
        self.assertFalse((ROOT / "references" / "specialist-router.md").exists())
        self.assertFalse((ROOT / "references" / "design-capability-manifest.json").exists())
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
        VALIDATOR.validate_capability_registry(data, ROOT)

    def test_registry_forms_a_complete_vertical_graph(self) -> None:
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], 4)
        self.assertEqual(data["skill"], "mature-design-director")
        flow = data["flow"]
        self.assertEqual(
            [stage["id"] for stage in flow],
            ["intent", "foundation", "direction", "selection", "production", "critique", "delivery-learning"],
        )
        self.assertEqual(len({stage["id"] for stage in flow}), len(flow))
        evidence_ids = set(data["evidence_types"])
        self.assertLessEqual(set(data["authority"]["release_evidence"]), evidence_ids)
        capability_ids = set()
        for capability in data["capabilities"]:
            capability_ids.add(capability["id"])
            self.assertTrue((ROOT / capability["contract"]).is_file())
            self.assertTrue(capability["accepts"])
            self.assertTrue(capability["outputs"])
            self.assertTrue(capability["foundations"])
            self.assertTrue(capability["evidence"])
            self.assertLessEqual(set(capability["evidence"]), evidence_ids)
            foundation_roles = {item["role"] for item in capability["foundations"]}
            delegate_roles = {item["role"] for item in capability["delegates"]}
            for output in capability["outputs"]:
                self.assertTrue(output["id"])
                self.assertLessEqual(set(output["requires_foundations"]), foundation_roles)
                self.assertLessEqual(set(output["requires_delegates"]), delegate_roles)
            for delegation in capability["delegates"]:
                self.assertTrue(delegation["role"])
                self.assertTrue(delegation["candidates"])
        self.assertEqual(len(capability_ids), len(data["capabilities"]))

    def test_validator_contains_schema_not_catalogued_names_or_release_pins(self) -> None:
        source = VALIDATOR_PATH.read_text(encoding="utf-8")
        forbidden = (
            "MODULE_IDS",
            "ABSORBED_SKILLS",
            "RETAINED_INDEPENDENT_SKILLS",
            "RETAINED_DESIGN_COMPOSITION",
            "RETAINED_ENFORCEMENT",
            "AUDIT_BASELINE_SHA256",
            "PINNED_SPDX_VERSION",
            "PINNED_SPDX_ID_COUNT",
            "PINNED_SPDX_IDS_SHA256",
        )
        for name in forbidden:
            with self.subTest(name=name):
                self.assertNotIn(name, source)

    def test_ecosystem_and_learning_sources_are_reachable_from_registry(self) -> None:
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
        for path in data["ecosystem"].values():
            self.assertTrue((ROOT / path).is_file(), path)
        self.assertTrue((ROOT / data["learning"]["contract"]).is_file())
        self.assertEqual(data["learning"]["project_record"], ".hermes/design/")

    def test_portable_bundle_manifest_covers_new_support_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "skill"
            shutil.copytree(ROOT, root)
            extra = root / "references" / "capabilities" / "future-medium.md"
            extra.write_text("# Future medium\n", encoding="utf-8")
            skill_text = (root / "SKILL.md").read_text(encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "bundle manifest omits"):
                VALIDATOR.validate_portable_bundle_manifest(root, skill_text)
            VALIDATOR.validate_portable_bundle_manifest(
                root, skill_text + "\n`references/capabilities/future-medium.md`\n"
            )

    def test_runtime_release_validator_and_dependencies_are_portably_packaged(self) -> None:
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        required = {
            "maintenance/validate_skill.py",
            "maintenance/spdx-license-ids.json",
            "maintenance/ecosystem-audit-baseline.json",
            "maintenance/audit_ecosystem.py",
        }
        for path in required:
            self.assertIn(f"`{path}`", skill_text)
            self.assertTrue((ROOT / path).is_file())

    def test_media_requirements_are_exact_and_match_installed_hermes(self) -> None:
        requirements = ROOT / "scripts" / "media-requirements.txt"
        pins = {}
        for line in requirements.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            match = re.fullmatch(r"([A-Za-z0-9_.-]+)==([^\s;]+)", line)
            self.assertIsNotNone(match, f"media requirement must use an exact pin: {line}")
            assert match is not None
            name, version = match.groups()
            self.assertNotIn(name.casefold(), pins)
            pins[name.casefold()] = version
        self.assertIn("pillow", pins)
        self.assertIn("numpy", pins)

        try:
            hermes_requirements = importlib.metadata.requires("hermes-agent") or []
        except importlib.metadata.PackageNotFoundError:
            return
        pillow_requirement = next(
            (item for item in hermes_requirements if item.casefold().startswith("pillow==")),
            None,
        )
        if pillow_requirement is not None:
            self.assertEqual(f"Pillow=={pins['pillow']}", pillow_requirement)


if __name__ == "__main__":
    unittest.main()
