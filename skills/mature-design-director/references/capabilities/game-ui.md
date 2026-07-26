# Game UI and UI-Asset Capability

Use this capability for game HUD layout, engine-native interface behavior, reusable UI kits, panels, buttons, bars, slots, icons, UI states, nine-slice textures, atlases, and simple UI feedback animation.

This capability does **not** own characters, enemies, projectiles, impacts, or long sprite animation; use `references/capabilities/sprite.md`. It also does not make every game HUD an interface task.

## Route by runtime and output

| Need | Route |
|---|---|
| Web-rendered HUD | umbrella + `references/capabilities/interface.md` + actual web stack |
| Godot/Unity/Cocos/native engine HUD layout/interaction | umbrella + this capability + actual engine mechanics/tooling |
| UI visual asset pack only | this capability; engine integration only when requested/project root exists |
| Character/prop/FX sprite | `references/capabilities/sprite.md` |
| Full game project guide or bug repair | the independent domain/course skill, which may call this capability |

Never load frontend implementation guidance for engine-native controls merely because both outputs are visual.

## Scope and engine detection

Identify:

- target engine/project root;
- input mode: prompt, reference, existing PNG, screenshot extraction, or project-local style library;
- output scope: full common kit, component subset, material/icon set, packaging, extraction, or integration;
- motion scope: static, state set, simple feedback loop/one-shot;
- component granularity and final pixel sizes.

Inspect a supplied project before asking. Detect Godot from `project.godot`, Unity from `Assets` plus `ProjectSettings`/manifest, Cocos from project/settings markers, and generic web from package/index/source markers. Stop when multiple roots are plausible.

## Style memory boundary

Persistent style references belong in the **project-local private design record**, not inside this shared skill. Use a path such as:

```text
.hermes/design/game-ui-style-library/
  index.json
  <style>/
    style-card.md
    palette.json
    prompts.json
    approved-references/
    rejected-lessons.md
```

Store only when the user explicitly asks to reuse/remember the material and repository governance permits it. Classify inputs as anchor, accepted output, support, prompt, rejected, or noise. Keep strongest positive references; turn rejected/noisy material into abstract avoid rules. Never copy customer-owned images or derivatives into this shared skill.

The ingestion helper requires an explicit project-local `--skill-root` and refuses this canonical skill root. Read `references/capabilities/game-ui/style-library.md` and run the script's `--help` before use.

## Component contract

Prefer one transparent PNG per semantic component/state:

```text
panel_inventory.png
button_play_normal.png
button_play_hover.png
button_play_pressed.png
progress_health_bg.png
progress_health_fill.png
```

Avoid baked labels unless text art is explicitly required. Design corners/borders for nine-slice. Generate static stretchable bases plus separate animated overlays when possible.

For complete kits, use `references/capabilities/game-ui/ui-component-catalog.md`, map requested product screens to actual component archetypes, and generate by coherent category. Do not create fake output levels merely to increase count.

Read `references/capabilities/game-ui/component-contract.md` for naming, split levels, nine-slice, scaling, and engine mapping.

## Generation and extraction

Use the configured image-generation/editing backend for creative art. Scripts may inspect, crop, clean, resize, package, and validate; they must not create the art direction.

For local helpers, use an isolated Python 3.11 environment with `scripts/media-requirements.txt`. Clear an inherited `PYTHONPATH` when creating/running the environment so Hermes or system site-packages cannot leak incompatible Pillow/NumPy binaries into it.

For generation:

- isolate the component orthographically;
- no mock screen/perspective scene/watermark;
- no cross-edge shadow;
- preserve palette, line weight, material, corners, glow, icon silhouette, and ornament density;
- choose native transparency when available;
- when keying is required, choose a color absent from the style rather than blindly using magenta.

For screenshot extraction:

- crop with conservative margin;
- expand/close masks before matting when edges are uncertain;
- preserve complete strokes and ornaments;
- strip unwanted text and background residue;
- mark approximate extraction honestly when source layers are occluded or blended;
- regenerate from the approved style contract when the screenshot cannot yield a clean reusable layer.

Do not assume generated sheets use a fixed grid. Detect real separators/cell/foreground bounds. Re-slice from the original when fixed-grid crops produce neighbors or missing parts.

Connected-component analysis identifies review candidates; it must not blindly keep only the largest blob. Frames and decorated controls can have valid disconnected ornaments.

## Size, alpha, and animation

Resolve final pixel size before packaging. Crop true bounds, add transparent padding, then resize. Prefer controlled 2×/3× sources and one high-quality downsample. For alpha, use premultiplication; for severe reductions, area pre-shrink plus Lanczos, mild denoise, and restrained sharpen.

```bash
python3 scripts/game-ui/resize_assets_high_quality.py \
  --input <clean-png-folder> --output <final-folder> \
  --max-side 512 --denoise auto --sampler area-lanczos --prefilter 0.18
```

When keying:

```bash
python3 scripts/game-ui/suggest_key_color.py --input <reference-or-folder>
python3 scripts/game-ui/clean_alpha_fringe.py \
  --input <folder-or-png> --backup <backup-folder> --report-json <qa.json>
```

Remove visible spill and key-colored RGB in alpha-zero pixels.

For simple UI motion, keep canvas, anchor, padding, component bounds, static design, and style contract stable. Prefer subtle glow, scale pulse, highlight sweep, fill, state transition, or small particles. Export frames, static fallback, GIF/contact sheet, timing, and engine note. Engine tweens/shaders should own purely mechanical alpha/scale/rotation when cleaner than baked frames.

## Packaging and integration

```bash
python3 scripts/game-ui/package_ui_assets.py \
  --input <png-folder> --output <output-folder> \
  --pack-name <slug> --engines auto --project <project-root> --category-subdirs
```

Use explicit engine when auto-detection is ambiguous or the user overrides it. Public output should remain focused on semantic PNG folders, overview/contact sheets, and requested engine scaffolding; debug manifests are opt-in.

Godot stretch assets map to `NinePatchRect`, `TextureButton`, or `TextureProgressBar`; other engines use their native primitives. Integrate only into the requested project and keep gameplay changes out of scope.

## QA

Inspect root/level overviews and each asset at 100% on light and dark target backgrounds. Block delivery for:

- chroma spill or hidden key RGB;
- cropped frame/ornament;
- background fragments or neighbor pieces;
- multiple unintended semantic components;
- muddy/noisy one-step scaling;
- inconsistent states or style drift;
- missing normal state or required bg/fill pair;
- invalid nine-slice margins;
- unstable animation anchor/canvas;
- bad loop seam or no idle/static fallback;
- accidental text;
- approximate extraction presented as exact.

Run script `--help` and compile/smoke tests after changes. Read `references/capabilities/game-ui/toolchain.md` for backend/tool selection.