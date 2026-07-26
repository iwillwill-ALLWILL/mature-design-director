#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "references" / "capability-registry.json"
BRIEF = ROOT / "templates" / "final-user-design-brief.md"
ADOPTION = ROOT / "templates" / "adoption-ledger.md"
VALIDATOR_PATH = ROOT / "maintenance" / "validate_skill.py"
SPEC = importlib.util.spec_from_file_location("release_contract_validator", VALIDATOR_PATH)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VALIDATOR
SPEC.loader.exec_module(VALIDATOR)


class CreativeReleaseLifecycleTests(unittest.TestCase):
    def _release_record(self, project_root: Path) -> dict[str, Any]:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        capability = next(item for item in registry["capabilities"] if item["id"] == "interface")
        required = set(registry["authority"]["release_evidence"]) | set(capability["evidence"])
        primary_relative = "artifact/index.html"
        primary_path = project_root / primary_relative
        primary_path.parent.mkdir(parents=True, exist_ok=True)
        primary_path.write_text(
            "<!doctype html><html><head><title>artifact under test</title></head>"
            "<body>Ready</body></html>\n",
            encoding="utf-8",
        )
        primary_sha256 = hashlib.sha256(primary_path.read_bytes()).hexdigest()
        evidence: dict[str, list[dict[str, object]]] = {}
        for evidence_id in sorted(required):
            relative = f"evidence/{evidence_id}.txt"
            path = project_root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"evidence for {evidence_id}\n", encoding="utf-8")
            evidence[evidence_id] = [
                {
                    "ref": relative,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "subject_sha256": primary_sha256,
                    "description": f"bound {evidence_id} evidence",
                    "reviewer": "independent-reviewer" if evidence_id in {"proof-selection", "independent-critique"} else "",
                    "benchmarks": ["named-mature-benchmark"] if evidence_id in {"proof-selection", "comparative-quality"} else [],
                }
            ]

        transition_evidence = {
            (item["from"], item["to"]): list(item["requires"])
            for item in registry["artifact_lifecycle"]["transitions"]
        }
        history = [{"state": registry["artifact_lifecycle"]["initial_state"], "evidence": []}]
        route = [
            "representative-proof",
            "selected-direction",
            "production-candidate",
            "release-candidate",
            "delivered",
        ]
        previous = history[0]["state"]
        for state in route:
            new_evidence = transition_evidence[(previous, state)]
            if state == "release-candidate":
                attached = {value for row in history for value in row["evidence"]} | set(new_evidence)
                future = set(transition_evidence[("release-candidate", "delivered")])
                new_evidence = sorted(set(new_evidence) | (required - attached - future))
            history.append({"state": state, "evidence": new_evidence})
            previous = state

        return {
            "schema_version": 1,
            "registry_schema_version": registry["schema_version"],
            "registry_sha256": hashlib.sha256(REGISTRY.read_bytes()).hexdigest(),
            "artifact_id": "artifact-under-test",
            "capability_id": "interface",
            "producer": "production-agent",
            "creative_authority": "mature-design-director",
            "artifact_state": "delivered",
            "final_audience": "named product user",
            "requester_reviewer": "requester",
            "native_medium": {
                "requested": "real browser product",
                "actual": "real browser product",
                "classification": "native-product",
                "output_class": "responsive-product-interface",
            },
            "primary_artifact": {
                "ref": primary_relative,
                "sha256": primary_sha256,
            },
            "creative_foundations": [
                {
                    "role": "product-visual-system",
                    "source_class": "approved-artboards",
                    "source": "approved artboard system",
                    "evidence": "creative-source",
                }
            ],
            "assembly_mechanics": [
                {
                    "role": "runtime",
                    "candidate": "actual-project-framework",
                    "tool": "actual project framework",
                    "evidence": "technical-integrity",
                }
            ],
            "evidence": evidence,
            "state_history": history,
            "delegations": [],
            "rejection_reason": "",
        }

    def test_registry_defines_one_evidence_gated_artifact_lifecycle(self) -> None:
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))

        self.assertEqual(data["schema_version"], 4)
        lifecycle = data["artifact_lifecycle"]
        self.assertIn(lifecycle["initial_state"], lifecycle["states"])
        self.assertTrue(lifecycle["release_states"])
        self.assertTrue(lifecycle["rejected_states"])
        self.assertTrue(data["authority"]["release_evidence"])
        self.assertTrue(lifecycle["transitions"])

    def test_validator_rejects_a_release_path_missing_global_evidence(self) -> None:
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
        VALIDATOR.validate_capability_registry(data, ROOT)

        mutated = copy.deepcopy(data)
        mutated["artifact_lifecycle"]["transitions"][0]["requires"].remove("audience-authenticity")
        with self.assertRaisesRegex(ValueError, "release path omits"):
            VALIDATOR.validate_capability_registry(mutated, ROOT)

    def test_every_capability_separates_creative_foundations_from_mechanics(self) -> None:
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))

        for capability in data["capabilities"]:
            foundations = capability["foundations"]
            self.assertTrue(foundations, capability["id"])
            creative_sources = {
                source
                for foundation in foundations
                for source in foundation["sources"]
            }
            mechanics = {
                candidate
                for delegation in capability["delegates"]
                for candidate in delegation["candidates"]
            }
            self.assertTrue(creative_sources, capability["id"])
            self.assertTrue(mechanics, capability["id"])
            self.assertFalse(creative_sources & mechanics, capability["id"])

    def test_project_records_cannot_conflate_final_audience_foundation_and_mechanics(self) -> None:
        brief = BRIEF.read_text(encoding="utf-8")
        adoption = ADOPTION.read_text(encoding="utf-8")

        self.assertIn("## Final audience and authentic encounter", brief)
        self.assertIn("## Requester, reviewer, and operator", brief)
        self.assertIn("## Artifact state and native medium", brief)
        self.assertIn("## Creative foundation", adoption)
        self.assertIn("## Assembly mechanics", adoption)
        self.assertNotIn("| System / asset / tool |", adoption)

    def test_direction_selection_and_final_critique_are_distinct_transitions(self) -> None:
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
        transitions = {
            (transition["from"], transition["to"]): set(transition["requires"])
            for transition in data["artifact_lifecycle"]["transitions"]
        }

        self.assertIn(
            "proof-selection",
            transitions[("representative-proof", "selected-direction")],
        )
        final_critique = transitions[("production-candidate", "release-candidate")]
        self.assertIn("comparative-quality", final_critique)
        self.assertIn("independent-critique", final_critique)

    def test_state_contracts_require_whole_artifact_before_production_candidate(self) -> None:
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
        states = data["artifact_lifecycle"]["states"]
        transitions = {
            (transition["from"], transition["to"]): set(transition["requires"])
            for transition in data["artifact_lifecycle"]["transitions"]
        }

        self.assertFalse(states["direction-candidate"]["requires_output_foundations"])
        self.assertFalse(states["direction-candidate"]["requires_output_mechanics"])
        self.assertTrue(states["representative-proof"]["requires_output_foundations"])
        self.assertFalse(states["selected-direction"]["requires_output_mechanics"])
        self.assertTrue(states["production-candidate"]["requires_output_foundations"])
        self.assertTrue(states["production-candidate"]["requires_output_mechanics"])
        self.assertTrue(
            {"source-truth", "working-artifact", "rendered-artifact", "native-context"}
            <= transitions[("selected-direction", "production-candidate")]
        )
        self.assertFalse(
            {"working-artifact", "rendered-artifact", "native-context"}
            & transitions[("production-candidate", "release-candidate")]
        )

        lifecycle_mutations = [
            ("direction-candidate", "requires_output_foundations", True),
            ("representative-proof", "requires_output_foundations", False),
            ("selected-direction", "requires_output_mechanics", True),
            ("production-candidate", "requires_output_mechanics", False),
            ("delivered", "requires_output_foundations", False),
            ("rejected", "requires_output_mechanics", True),
        ]
        for state, field, value in lifecycle_mutations:
            with self.subTest(state=state, field=field):
                mutated = copy.deepcopy(data)
                mutated["artifact_lifecycle"]["states"][state][field] = value
                with self.assertRaisesRegex(ValueError, "lifecycle.*obligation"):
                    VALIDATOR.validate_capability_registry(mutated, ROOT)

        mutated = copy.deepcopy(data)
        mutated["authority"]["composition_rule"] = "   "
        with self.assertRaisesRegex(ValueError, "composition_rule"):
            VALIDATOR.validate_capability_registry(mutated, ROOT)

    def test_mechanics_only_record_cannot_claim_delivered(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            record = self._release_record(root)
            record["evidence"].pop("creative-source")
            for row in record["state_history"]:
                row["evidence"] = [value for value in row["evidence"] if value != "creative-source"]
            with self.assertRaisesRegex(ValueError, "creative-source"):
                VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

    def test_timeout_delegation_cannot_be_accepted_into_delivered_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            record = self._release_record(root)
            record["delegations"] = [
                {
                    "task_id": "delegated-task",
                    "status": "timeout",
                    "artifact_ref": "evidence/working-artifact.txt",
                    "artifact_sha256": "0" * 64,
                    "accepted_by": "mature-design-director",
                    "acceptance_evidence": "working-artifact",
                }
            ]
            with self.assertRaisesRegex(ValueError, "delegation.*completed"):
                VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

    def test_producing_agent_cannot_supply_selection_or_final_critique(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            record = self._release_record(root)
            record["evidence"]["proof-selection"][0]["reviewer"] = record["producer"]
            with self.assertRaisesRegex(ValueError, "reviewer.*producer"):
                VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

    def test_valid_release_record_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            VALIDATOR.validate_artifact_record(
                self._release_record(root),
                json.loads(REGISTRY.read_text()),
                root,
            )

    def test_one_evidence_claim_cannot_be_reused_across_lifecycle_stages(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            record = self._release_record(root)
            record["state_history"][2]["evidence"].append("audience-authenticity")
            with self.assertRaisesRegex(ValueError, "evidence.*more than one"):
                VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

    def test_rejection_cannot_follow_a_terminal_delivered_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            record = self._release_record(root)
            record["artifact_state"] = "rejected"
            record["rejection_reason"] = "user rejected the delivered claim"
            record["state_history"].append({"state": "rejected", "evidence": []})
            with self.assertRaisesRegex(ValueError, "terminal.*rejected"):
                VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

    def test_completed_delegation_binds_accepted_artifact_path_and_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            record = self._release_record(root)
            item = record["evidence"]["working-artifact"][0]
            record["delegations"] = [
                {
                    "task_id": "delegated-task",
                    "status": "completed",
                    "artifact_ref": item["ref"],
                    "artifact_sha256": item["sha256"],
                    "accepted_by": "mature-design-director",
                    "acceptance_evidence": "working-artifact",
                }
            ]
            VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

            record["delegations"][0]["artifact_sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "artifact_sha256.*bytes"):
                VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

            record = self._release_record(root)
            item = record["evidence"]["working-artifact"][0]
            record["delegations"] = [
                {
                    "task_id": "delegated-task",
                    "status": "completed",
                    "artifact_ref": item["ref"],
                    "artifact_sha256": item["sha256"],
                    "accepted_by": "mature-design-director",
                    "acceptance_evidence": "independent-critique",
                }
            ]
            with self.assertRaisesRegex(ValueError, "acceptance_evidence.*artifact_sha256"):
                VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

    def test_release_layers_must_bind_declared_capability_roles_and_classes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            record = self._release_record(root)
            record["creative_foundations"][0]["source_class"] = "self-declared-custom-css"
            with self.assertRaisesRegex(ValueError, "source_class.*declared"):
                VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

            record = self._release_record(root)
            record["assembly_mechanics"][0]["candidate"] = "self-declared-html-showcase"
            with self.assertRaisesRegex(ValueError, "candidate.*declared"):
                VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

    def test_output_class_requires_its_declared_foundation_and_mechanics_roles(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            record = self._release_record(root)
            record["native_medium"]["output_class"] = "self-declared-native-output"
            with self.assertRaisesRegex(ValueError, "output_class.*declared"):
                VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

            record = self._release_record(root)
            record["assembly_mechanics"] = []
            with self.assertRaisesRegex(ValueError, "requires mechanics roles.*runtime"):
                VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

    def test_delivered_output_rejects_concept_classification_and_parallel_authority(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            record = self._release_record(root)
            record["native_medium"]["classification"] = "concept-proof"
            with self.assertRaisesRegex(ValueError, "classification.*output_class"):
                VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

            record = self._release_record(root)
            record["creative_authority"] = "parallel-readme-authority"
            with self.assertRaisesRegex(ValueError, "creative_authority must be mature-design-director"):
                VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

            record = self._release_record(root)
            concept = root / "artifact" / "concept.md"
            concept.write_text("representative concept proof\n", encoding="utf-8")
            record["artifact_state"] = "direction-candidate"
            record["native_medium"]["classification"] = "concept-proof"
            record["primary_artifact"] = {
                "ref": "artifact/concept.md",
                "sha256": hashlib.sha256(concept.read_bytes()).hexdigest(),
            }
            record["creative_foundations"] = []
            record["assembly_mechanics"] = []
            record["evidence"] = {}
            record["state_history"] = [{"state": "direction-candidate", "evidence": []}]
            record["delegations"] = []
            VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

    def test_primary_artifact_type_and_evidence_subject_are_bound(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            record = self._release_record(root)
            readme = root / "artifact" / "README.md"
            readme.write_text("source-code generator concept\n", encoding="utf-8")
            readme_sha256 = hashlib.sha256(readme.read_bytes()).hexdigest()
            record["primary_artifact"] = {
                "ref": "artifact/README.md",
                "sha256": readme_sha256,
            }
            for items in record["evidence"].values():
                for item in items:
                    item["subject_sha256"] = readme_sha256
            with self.assertRaisesRegex(ValueError, "primary_artifact.*suffix"):
                VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

            record = self._release_record(root)
            disguised = root / "artifact" / "index.html"
            disguised.write_text("# README\nsource-code generator concept\n", encoding="utf-8")
            disguised_sha256 = hashlib.sha256(disguised.read_bytes()).hexdigest()
            record["primary_artifact"]["sha256"] = disguised_sha256
            for items in record["evidence"].values():
                for item in items:
                    item["subject_sha256"] = disguised_sha256
            with self.assertRaisesRegex(ValueError, "artifact format"):
                VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

            record = self._release_record(root)
            record["evidence"]["independent-critique"][0]["subject_sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "subject_sha256.*primary artifact"):
                VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

    def test_delivered_zip_requires_a_hash_bound_manifest_and_real_primary(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            record = self._release_record(root)
            bundle = root / "artifact" / "product.zip"
            with zipfile.ZipFile(bundle, "w") as archive:
                archive.writestr("README.md", "concept only")
                archive.writestr("generator.py", "print('component board')")
                archive.writestr("component-board.html", "<!doctype html><title>board</title>")
            bundle_sha256 = hashlib.sha256(bundle.read_bytes()).hexdigest()
            record["primary_artifact"] = {"ref": "artifact/product.zip", "sha256": bundle_sha256}
            for items in record["evidence"].values():
                for item in items:
                    item["subject_sha256"] = bundle_sha256
            with self.assertRaisesRegex(ValueError, "artifact bundle manifest"):
                VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

            payload = b"<!doctype html><html><head><title>Product</title></head><body>Ready</body></html>"
            manifest = {
                "schema_version": 1,
                "primary": "index.html",
                "files": [
                    {"path": "index.html", "sha256": hashlib.sha256(payload).hexdigest()},
                ],
            }
            with zipfile.ZipFile(bundle, "w") as archive:
                archive.writestr("artifact-manifest.json", json.dumps(manifest, sort_keys=True))
                archive.writestr("index.html", payload)
            bundle_sha256 = hashlib.sha256(bundle.read_bytes()).hexdigest()
            record["primary_artifact"]["sha256"] = bundle_sha256
            for items in record["evidence"].values():
                for item in items:
                    item["subject_sha256"] = bundle_sha256
            VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

            alias_cases = (
                ("index.html", "./index.html"),
                ("index.html", "INDEX.html"),
                ("cafe\u0301/index.html", "café/index.html"),
                ("foo/index.html", "foo//index.html"),
                ("index.html", "in\u200bdex.html"),
            )
            for case_index, (primary, alias) in enumerate(alias_cases):
                aliased_bundle = root / f"alias-{case_index}.zip"
                files = [
                    {"path": primary, "sha256": hashlib.sha256(payload).hexdigest()},
                    {"path": alias, "sha256": hashlib.sha256(b"shadow").hexdigest()},
                ]
                alias_manifest = {"schema_version": 1, "primary": primary, "files": files}
                with zipfile.ZipFile(aliased_bundle, "w") as archive:
                    archive.writestr("artifact-manifest.json", json.dumps(alias_manifest, sort_keys=True))
                    archive.writestr(primary, payload)
                    archive.writestr(alias, b"shadow")
                with self.subTest(primary=primary, alias=alias), self.assertRaisesRegex(ValueError, "bundle.*path|bundle.*alias"):
                    VALIDATOR.validate_artifact_format(aliased_bundle)

    def test_review_evidence_bytes_are_distinct_and_items_are_unique(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            record = self._release_record(root)
            record["evidence"]["representative-proof"].append(
                copy.deepcopy(record["evidence"]["representative-proof"][0])
            )
            with self.assertRaisesRegex(ValueError, "duplicate evidence item"):
                VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

            record = self._release_record(root)
            shared = copy.deepcopy(record["evidence"]["representative-proof"][0])
            shared["reviewer"] = "independent-reviewer"
            shared["benchmarks"] = ["named-mature-benchmark"]
            record["evidence"]["proof-selection"] = [shared]
            with self.assertRaisesRegex(ValueError, "distinct evidence.*proof-selection"):
                VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

    def test_record_types_delegation_ids_and_registry_identity_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            record = self._release_record(root)
            record["schema_version"] = True
            with self.assertRaisesRegex(ValueError, "schema_version must be 1"):
                VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

            record = self._release_record(root)
            record["evidence"]["proof-selection"][0]["benchmarks"] = [{}]
            with self.assertRaisesRegex(ValueError, "benchmarks must be a unique string list"):
                VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

            record = self._release_record(root)
            record["evidence"]["proof-selection"][0]["benchmarks"] = ["   "]
            with self.assertRaisesRegex(ValueError, "benchmarks must be a unique string list"):
                VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

            record = self._release_record(root)
            record["evidence"]["proof-selection"][0]["reviewer"] = record["producer"] + "\u200b"
            with self.assertRaisesRegex(ValueError, "reviewer must differ from producer"):
                VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

            for suffix in ("\x00", "\u034f"):
                record = self._release_record(root)
                record["evidence"]["proof-selection"][0]["reviewer"] = record["producer"] + suffix
                with self.subTest(identity_suffix=repr(suffix)):
                    with self.assertRaisesRegex(ValueError, "reviewer must differ from producer"):
                        VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

            record = self._release_record(root)
            record["producer"] = record["creative_authority"]
            with self.assertRaisesRegex(ValueError, "producer must differ from creative_authority"):
                VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

            for source in ("ａｃｔｕａｌ ｐｒｏｊｅｃｔ ｆｒａｍｅｗｏｒｋ", "actual project\u200b framework"):
                record = self._release_record(root)
                record["creative_foundations"][0]["source"] = source
                with self.subTest(source=source):
                    with self.assertRaisesRegex(ValueError, "foundation and assembly mechanics overlap"):
                        VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

            for malformed in ([], {}):
                record = self._release_record(root)
                record["assembly_mechanics"][0]["evidence"] = malformed
                with self.subTest(mechanics_evidence=type(malformed).__name__):
                    with self.assertRaisesRegex(ValueError, "assembly_mechanics.*evidence"):
                        VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

            record = self._release_record(root)
            item = record["evidence"]["working-artifact"][0]
            record["delegations"] = [{
                "task_id": "malformed-acceptance",
                "status": "completed",
                "artifact_ref": item["ref"],
                "artifact_sha256": item["sha256"],
                "accepted_by": "mature-design-director",
                "acceptance_evidence": [],
            }]
            with self.assertRaisesRegex(ValueError, "acceptance_evidence"):
                VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

            record = self._release_record(root)
            item = record["evidence"]["working-artifact"][0]
            delegation = {
                "task_id": "same-task",
                "status": "completed",
                "artifact_ref": item["ref"],
                "artifact_sha256": item["sha256"],
                "accepted_by": "mature-design-director",
                "acceptance_evidence": "working-artifact",
            }
            record["delegations"] = [delegation, copy.deepcopy(delegation)]
            with self.assertRaisesRegex(ValueError, "delegation task_id.*unique"):
                VALIDATOR.validate_artifact_record(record, json.loads(REGISTRY.read_text()), root)

            record = self._release_record(root)
            weakened = json.loads(REGISTRY.read_text())
            weakened["capabilities"][0]["evidence"].remove("technical-integrity")
            with self.assertRaisesRegex(ValueError, "installed registry"):
                VALIDATOR.validate_artifact_record(record, weakened, root)

            numeric_drift = json.loads(REGISTRY.read_text())
            numeric_drift["schema_version"] = 4.0
            with self.assertRaisesRegex(ValueError, "identity/schema"):
                VALIDATOR.validate_artifact_record(record, numeric_drift, root)


if __name__ == "__main__":
    unittest.main()
