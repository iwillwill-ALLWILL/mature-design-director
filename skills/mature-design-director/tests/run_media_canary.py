#!/usr/bin/env python3
"""Run an isolated, non-creative integration canary for migrated media helpers."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def run(command: list[str], *, stdout: Path | None = None) -> None:
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    if stdout:
        with stdout.open("w", encoding="utf-8") as handle:
            result = subprocess.run(command, text=True, stdout=handle, stderr=subprocess.PIPE, env=env, check=False)
    else:
        result = subprocess.run(command, text=True, capture_output=True, env=env, check=False)
    if result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(command)}\n{result.stderr}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--keep", type=Path, help="Keep canary output at this path instead of a temporary directory")
    args = parser.parse_args()
    root = args.skill_root.expanduser().resolve()

    try:
        from PIL import Image, ImageDraw
        import numpy  # noqa: F401 - dependency and ABI canary
    except Exception as exc:
        raise SystemExit("Install scripts/media-requirements.txt in an isolated Python 3.11 environment") from exc

    temporary = None
    if args.keep:
        work = args.keep.expanduser().resolve()
        work.mkdir(parents=True, exist_ok=True)
    else:
        temporary = tempfile.TemporaryDirectory(prefix="mature-design-media-canary-")
        work = Path(temporary.name)
    ui_input = work / "ui-input"
    ui_input.mkdir(parents=True, exist_ok=True)

    sheet = Image.new("RGB", (128, 128), "#ff00ff")
    draw = ImageDraw.Draw(sheet)
    colors = ["#d8b56a", "#6fa8dc", "#93c47d", "#c27ba0"]
    for index, color in enumerate(colors):
        x = (index % 2) * 64
        y = (index // 2) * 64
        draw.rounded_rectangle((x + 20, y + 14, x + 44, y + 54), radius=6, fill=color, outline="#241b18", width=2)
    sheet.save(work / "sprite-sheet.png")

    ui = Image.new("RGBA", (160, 96), (255, 0, 255, 255))
    ui_draw = ImageDraw.Draw(ui)
    ui_draw.rounded_rectangle((20, 18, 140, 78), radius=14, fill=(48, 59, 73, 255), outline=(222, 181, 102, 255), width=5)
    ui.save(ui_input / "button_play_normal.png")
    selected_ui = ui.copy()
    ImageDraw.Draw(selected_ui).rounded_rectangle((24, 22, 136, 74), radius=10, outline=(255, 230, 150, 255), width=3)
    selected_ui.save(ui_input / "button_play_selected.png")

    py = sys.executable
    scripts = root / "scripts"
    run([py, str(scripts / "sprite" / "make_layout_guide.py"), "--rows", "2", "--cols", "2", "--cell-width", "64", "--cell-height", "64", "--safe-margin-x", "8", "--safe-margin-y", "8", "--output", str(work / "layout-guide.png")])
    run([py, str(scripts / "game-ui" / "suggest_key_color.py"), "--input", str(ui_input)], stdout=work / "key-color.json")
    run([py, str(scripts / "game-ui" / "clean_alpha_fringe.py"), "--input", str(ui_input), "--report-json", str(work / "alpha-report.json")])
    run([py, str(scripts / "game-ui" / "resize_assets_high_quality.py"), "--input", str(ui_input), "--output", str(work / "ui-resized"), "--max-side", "64"])
    run([py, str(scripts / "game-ui" / "package_ui_assets.py"), "--input", str(work / "ui-resized"), "--output", str(work / "ui-pack"), "--pack-name", "canary", "--engines", "generic", "--category-subdirs", "--write-manifest"])

    style_root = work / "project" / ".hermes" / "design" / "game-ui-style-library"
    ingest = scripts / "game-ui" / "ingest_style_reference.py"
    run([py, str(ingest), "--skill-root", str(style_root), "ingest", "--style", "canary", "--input", str(work / "layout-guide.png"), "--role", "anchor", "--notes", "temporary automated canary"])
    run([py, str(ingest), "--skill-root", str(style_root), "show", "--style", "canary", "--format", "json"], stdout=work / "style-show.json")

    run([py, str(scripts / "sprite" / "process_sprite_sheet.py"), "process", "--input", str(work / "sprite-sheet.png"), "--target", "player", "--mode", "idle", "--output-dir", str(work / "sprite-output"), "--rows", "2", "--cols", "2", "--cell-size", "64", "--fit-scale", "0.8", "--shared-scale", "--component-mode", "largest", "--reject-edge-touch"])
    run([py, str(scripts / "frontend" / "scan_frontend_project.py"), str(root.parents[1])], stdout=work / "frontend-scan.json")

    required = [
        work / "layout-guide.png", work / "key-color.json", work / "alpha-report.json",
        work / "style-show.json", work / "frontend-scan.json", work / "ui-pack", work / "sprite-output",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit(f"media canary missing outputs: {missing}")
    ui_manifest = json.loads(
        (work / "ui-pack" / "level_01_complete" / "ui-asset-manifest.json").read_text(encoding="utf-8")
    )
    button = next(component for component in ui_manifest["components"] if component["id"] == "button-play")
    if "selected" not in button["states"] or button["states"].get("hover") == button["states"]["selected"]:
        raise SystemExit("game UI canary did not preserve selected as an independent state")

    report = {
        "ok": True,
        "layout_size": Image.open(work / "layout-guide.png").size,
        "resized_size": Image.open(work / "ui-resized" / "button_play_normal.png").size,
        "sprite_pngs": len(list((work / "sprite-output").rglob("*.png"))),
        "ui_pack_pngs": len(list((work / "ui-pack").rglob("*.png"))),
        "alpha_processed": json.loads((work / "alpha-report.json").read_text())["processed"],
        "style_slug": json.loads((work / "style-show.json").read_text())["slug"],
        "selected_state": button["states"]["selected"],
        "kept_at": str(work) if args.keep else None,
    }
    print(json.dumps(report, indent=2))
    if temporary:
        temporary.cleanup()


if __name__ == "__main__":
    main()
