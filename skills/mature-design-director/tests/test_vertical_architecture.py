#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "references" / "capability-registry.json"
VALIDATOR_PATH = ROOT / "scripts" / "validate_skill.py"

sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location("validate_skill_v3", VALIDATOR_PATH)
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
        self.assertEqual(data["schema_version"], 3)
        self.assertEqual(data["skill"], "mature-design-director")
        flow = data["flow"]
        self.assertGreaterEqual(len(flow), 5)
        self.assertEqual(len({stage["id"] for stage in flow}), len(flow))
        evidence_ids = set(data["evidence_types"])
        capability_ids = set()
        for capability in data["capabilities"]:
            capability_ids.add(capability["id"])
            self.assertTrue((ROOT / capability["contract"]).is_file())
            self.assertTrue(capability["accepts"])
            self.assertTrue(capability["outputs"])
            self.assertTrue(capability["evidence"])
            self.assertLessEqual(set(capability["evidence"]), evidence_ids)
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


if __name__ == "__main__":
    unittest.main()
