# 2D Sprite and Frame-Animation Capability

Use this capability for characters, creatures, NPCs, props, spells, projectiles, impacts, summons, FX, pixel/HD sprites, animation grids, transparent frames, GIF previews, and engine atlases. Runtime/game assembly remains outside this capability.

Never replace requested final sprite art with circles, rectangles, SVG/PIL/Canvas drawings, crude silhouettes, or code-rendered placeholders. Scripts may create layout guides and postprocess generated art; they do not create the creative image.

## Quality floor

Deliver only assets plausible for a polished student project or commercial prototype. Regenerate or report a blocker when output is generic, inconsistent, cropped, noisy, off-style, poorly animated, or too rough to keep.

Strip watermarks, text, guide marks, fake shadows, reference residue, key spill, and demo artifacts. A missing asset is more honest than a weak temporary asset presented as final.

## Infer the plan

Infer from the request:

- asset type and role;
- action family;
- view: top-down, side, or three-quarter;
- art style based on project/reference;
- frame count and grid;
- anchor: center, bottom, or feet;
- bundle: single, unit, spell, combat, line, hero actions, or engine atlas;
- reference role and identity invariants;
- final engine/output size.

Read `references/capabilities/sprite/modes.md` when ambiguous. Choose the smallest useful bundle without forcing the user to specify rows, flags, or processor details.

## One action family per raw sheet

Do not generate unrelated idle/run/shoot/jump rows as one raw mixed-action atlas. For heroes and high-value characters:

1. generate separate action grids;
2. QC each action independently;
3. generate projectile, muzzle, slash, trail, dust, and impact as separate sheets when they materially widen the body bounding box;
4. assemble the engine atlas deterministically only after every source grid passes.

Default animated bodies to multi-row grids:

- 4 frames → 2×2;
- 6 frames → 2×3;
- 8 frames → 2×4;
- 9 frames → 3×3;
- 12 frames → 3×4 or 4×3;
- 16 frames → 4×4.

Raw 1×N character/body strips drift and crop too easily. If runtime needs a row strip, assemble it after QC. Canonical four-direction locomotion may use 4×4 because it is one coherent directional family.

Keep body center, feet/bottom anchor, scale, and safe padding stable. For attack/cast/shoot, reject outputs whose body is materially smaller than accepted idle/run because detached FX widened the cell.

## Prop and map geometry

Square prop packs are for compact objects such as rocks, shrubs, barrels, crates, lamps, pots, debris, and ornaments.

Do not place floors, platforms, bridges, walls, ladders, roads, rails, long hazards, gates, buildings, large trees, checkpoints, or collision-bearing objects into generic square packs. Use one-by-one generation, cap/middle/cap strips, custom wide cells, or tileset-like atlases.

A failed square pack should be reclassified and regenerated, not passed by relaxing edge QC.

## Prompt and reference contract

Read `references/capabilities/sprite/prompt-rules.md`. Use the configured image-generation/editing tool for raw art. In Hermes this is `image_generate`; in another agent use its supported equivalent without inventing a vendor backend.

Make visual references visible to the model before generation and state their role: exact identity/style, animation of the same subject, evolution/variant, or matching prop/FX.

Preserve silhouette, palette, face/eye markers, costume, accessories, and material language. Let only requested action/evolution change.

Every animated prompt must require:

- exact grid and frame count;
- one coherent action family;
- stable identity, scale, and bounding box;
- subject within central safe area;
- stable anchor;
- nothing crossing cell edges;
- no labels, guides, mockup borders, or watermarks;
- a removable key background or native alpha according to the chosen pipeline.

A deterministic layout guide may communicate slot count, spacing, center, and padding, never art direction:

```bash
python3 scripts/sprite/make_layout_guide.py \
  --rows <rows> --cols <cols> \
  --cell-width 384 --cell-height 384 \
  --output <run-dir>/references/layout-guide.png
```

Do not reproduce guide boxes or marks in the generated output.

## Postprocess

Keep the original generation. Process a copy with:

Use an isolated Python 3.11 environment with `scripts/media-requirements.txt` and clear inherited `PYTHONPATH` so incompatible system/Hermes binary packages cannot leak into the processor.

```bash
python3 scripts/sprite/process_sprite_sheet.py process <args from --help>
```

The processor may remove the key background, split frames, filter components, scale, align, calculate QC metadata, export transparent sheets, and build GIFs. It must not decide aesthetics.

For body grids, use largest-component filtering only when detached components are definitely unwanted. For projectile/impact/aura/slash FX, preserve intentionally detached components. Use shared scale whenever frame-to-frame consistency matters.

Process every hero action separately before final atlas assembly.

## QC

Inspect raw sheet, clean sheet, transparent sheet, every frame, GIF, and final atlas:

- no frame touches a cell edge;
- body/subject scale is stable;
- anchor and centerline do not drift;
- identity and palette remain coherent;
- motion reads as one sequence;
- no detached effect became noise;
- no meaningful effect was deleted by component filtering;
- attack/cast body scale matches idle/run;
- loops close cleanly and one-shots start/end usefully;
- no key spill, alpha fringe, labels, guide marks, or crop defects;
- final engine dimensions and pivots are practical.

Change processor settings only for deterministic extraction/alignment problems. Regenerate the raw art for pose, identity, style, animation, or containment failures. Do not relax QC to force a bundle.

## Delivery contract

A single animation normally includes:

- original raw sheet;
- cleaned raw sheet;
- transparent sheet;
- frame PNGs;
- animation GIF/contact sheet;
- prompt/identity contract;
- pipeline metadata and QC report.

A hero-action bundle includes one set per action, separate FX/projectile/impact where needed, and an optional engine atlas built after per-action approval.

Keep user references, project style images, and rejected raw generations project-local. Only sanitized prompt rules, processor improvements, and repeatable QC lessons belong in this shared capability.