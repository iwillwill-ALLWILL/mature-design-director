#!/usr/bin/env python3
"""Read-only frontend project scanner for Codex skills."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


FRONTEND_EXTS = {".tsx", ".ts", ".jsx", ".js", ".vue", ".svelte", ".css", ".scss", ".sass", ".less", ".html"}
STYLE_EXTS = {".css", ".scss", ".sass", ".less"}
SKIP_DIRS = {
    "node_modules",
    ".git",
    "dist",
    "build",
    ".next",
    ".vite",
    "coverage",
    "vendor",
    "artifacts",
    "_source_extracts",
    "uploads",
    "logs",
}
COLOR_RE = re.compile(r"(#[0-9a-fA-F]{3,8}\b|rgba?\([^)]+\)|hsla?\([^)]+\))")


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def iter_frontend_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() in FRONTEND_EXTS:
            files.append(path)
    return files


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def detect_stack(pkg: dict[str, Any] | None, files: list[Path], root: Path) -> list[str]:
    deps: dict[str, str] = {}
    if pkg:
        deps.update(pkg.get("dependencies") or {})
        deps.update(pkg.get("devDependencies") or {})
    names = set(deps)
    stack: list[str] = []
    checks = [
        ("react", "React"),
        ("next", "Next.js"),
        ("vite", "Vite"),
        ("vue", "Vue"),
        ("svelte", "Svelte"),
        ("tailwindcss", "Tailwind CSS"),
        ("@radix-ui/react-dialog", "Radix UI"),
        ("lucide-react", "Lucide React"),
        ("framer-motion", "Framer Motion"),
        ("motion", "Motion"),
        ("gsap", "GSAP"),
        ("embla-carousel-react", "Embla Carousel"),
        ("swiper", "Swiper"),
        ("@tanstack/react-table", "TanStack Table"),
        ("@tanstack/react-query", "TanStack Query"),
        ("recharts", "Recharts"),
        ("echarts", "ECharts"),
        ("three", "Three.js"),
        ("phaser", "Phaser"),
        ("pixi.js", "PixiJS"),
    ]
    for dep, label in checks:
        if dep in names:
            stack.append(label)
    if (root / "components.json").exists():
        stack.append("shadcn/ui")
    if any(path.name == "tailwind.config.js" or path.name == "tailwind.config.ts" for path in root.iterdir() if path.is_file()):
        if "Tailwind CSS" not in stack:
            stack.append("Tailwind CSS")
    if any(path.suffix == ".tsx" for path in files):
        stack.append("TypeScript TSX")
    return stack


def collect_colors(files: list[Path]) -> list[dict[str, Any]]:
    colors: Counter[str] = Counter()
    for path in files:
        if path.suffix.lower() not in STYLE_EXTS:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        colors.update(match.group(1).lower() for match in COLOR_RE.finditer(text))
    return [{"color": color, "count": count} for color, count in colors.most_common(20)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan a frontend project and print JSON context.")
    parser.add_argument("root", nargs="?", default=".", help="Project root")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    package_json = load_json(root / "package.json")
    files = iter_frontend_files(root)
    style_files = [path for path in files if path.suffix.lower() in STYLE_EXTS]
    entry_candidates = [
        path for path in files
        if path.name in {"main.tsx", "main.jsx", "App.tsx", "App.jsx", "index.html", "page.tsx", "layout.tsx"}
    ]

    output = {
        "root": str(root),
        "package": {
            "name": package_json.get("name") if package_json else None,
            "scripts": package_json.get("scripts", {}) if package_json else {},
        },
        "detected_stack": detect_stack(package_json, files, root),
        "frontend_file_count": len(files),
        "style_file_count": len(style_files),
        "entry_candidates": [rel(path, root) for path in sorted(entry_candidates)[:30]],
        "largest_style_files": [
            {"path": rel(path, root), "bytes": path.stat().st_size}
            for path in sorted(style_files, key=lambda item: item.stat().st_size, reverse=True)[:10]
        ],
        "top_css_colors": collect_colors(style_files),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
