#!/usr/bin/env python3
from __future__ import annotations

import json
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "references" / "capability-registry.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class CreativeCapabilityTests(unittest.TestCase):
    def test_game_ui_selected_state_remains_distinct_from_hover(self) -> None:
        module = load_module(
            "mature_game_ui_packager",
            ROOT / "scripts" / "game-ui" / "package_ui_assets.py",
        )
        self.assertEqual(module.detect_state(module.tokenize("button_play_selected")), "selected")
        self.assertEqual(module.detect_state(module.tokenize("button_play_hover")), "hover")

    def test_sprite_processor_has_no_prompt_builder_and_detects_trimmed_edge_touch(self) -> None:
        script = ROOT / "scripts" / "sprite" / "process_sprite_sheet.py"
        help_result = subprocess.run(
            [sys.executable, str(script), "--help"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertNotIn("build-prompt", help_result.stdout)

        module = load_module("mature_sprite_processor", script)
        self.assertTrue(module.bbox_touches_edge((16, 16, 56, 40), 56, 56))
        source = script.read_text(encoding="utf-8")
        self.assertIn("bbox_touches_edge(bbox, qc_width, qc_height", source)

    def test_all_registered_helper_scripts_have_working_help(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        scripts = [
            ROOT / path for path in registry["resources"]
            if path.startswith(("scripts/frontend/", "scripts/game-ui/", "scripts/sprite/"))
            and path.endswith(".py")
        ]
        self.assertGreaterEqual(len(scripts), 8)
        for script in scripts:
            with self.subTest(script=script.name):
                result = subprocess.run(
                    [sys.executable, str(script), "--help"],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("usage:", result.stdout.lower())

    def test_style_ingest_requires_project_local_root(self) -> None:
        script = ROOT / "scripts" / "game-ui" / "ingest_style_reference.py"
        missing = subprocess.run(
            [sys.executable, str(script), "list"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("--skill-root", missing.stderr)

        canonical = subprocess.run(
            [sys.executable, str(script), "--skill-root", str(ROOT), "list"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(canonical.returncode, 0)
        self.assertIn("refusing to store", canonical.stderr)

        with tempfile.TemporaryDirectory() as temp:
            local_root = Path(temp) / ".hermes" / "design" / "game-ui-style-library"
            accepted = subprocess.run(
                [sys.executable, str(script), "--skill-root", str(local_root), "list"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(accepted.returncode, 0, accepted.stderr)
            self.assertFalse(local_root.exists())

    def test_game_ui_toolchain_uses_portable_backend_and_real_helper_paths(self) -> None:
        path = ROOT / "references" / "capabilities" / "game-ui" / "toolchain.md"
        text = path.read_text(encoding="utf-8")
        self.assertNotIn("`image_gen`", text)
        self.assertNotIn("Codex image viewing", text)
        self.assertNotIn("<codex-home>", text)
        for helper in (
            "scripts/game-ui/suggest_key_color.py",
            "scripts/game-ui/clean_alpha_fringe.py",
            "scripts/game-ui/resize_assets_high_quality.py",
        ):
            self.assertIn(helper, text)
            self.assertTrue((ROOT / helper).is_file(), helper)


if __name__ == "__main__":
    unittest.main()
