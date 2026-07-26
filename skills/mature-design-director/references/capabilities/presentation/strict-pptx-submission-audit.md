# Strict PPTX Submission Audit

Use this for final competition, procurement, grant, or archival PPTX review when the user requires concrete pass/fail findings without modifying the target.

## Audit model

Run two separate gates:

1. **Visible artifact gate** — what judges see after rendering.
2. **Package gate** — what remains inside the OOXML ZIP, including dormant masters/layouts and metadata.

Do not collapse these into one “looks fine” judgment. State the governing interpretation: a literal requirement such as “no placeholder text” can fail on package-level residue even if no placeholder is visible.

## Read-only sequence

1. Record exact path, basename, byte size, SHA-256, and optionally MD5.
2. Run ZIP CRC/integrity validation; detect encryption and duplicate member names.
3. Parse `ppt/presentation.xml` and its relationships to determine presentation order and exact slide count. Do not infer count only from filenames.
4. For every slide, inspect the shape tree:
   - picture count;
   - other shapes, charts, frames, connectors, OLE objects;
   - hidden flags;
   - picture relationship (`embed` vs `link`);
   - offset/extent against slide size;
   - crop rectangle, rotation/flips, and stretch behavior.
5. Inspect masters and layouts structurally, not only by extracted text. Count `p:ph`, `p:sp`, `p:pic`, `p:graphicFrame`, and `p:cxnSp` separately. A requirement such as “no placeholder text or shapes” requires both zero residue text/placeholders and zero drawable shapes; an empty text extraction alone is insufficient.
6. Inventory all package parts and content types. Explicitly search for GIF, video, audio, APNG, ActiveX, OLE, embeddings, VBA/macros, comments, notes, custom XML, and hyperlinks. Distinguish the standard `docProps/thumbnail.*` preview from hidden slide media, but report it explicitly so the classification is reviewable.
7. Parse **every** `.rels` part and report all `TargetMode="External"` relationships, not just slide relationships. Resolve every non-external target and flag dangling relationship targets.
8. For PNGs, verify signature and dimensions, then walk chunks. `acTL`, `fcTL`, or `fdAT` means animated PNG even if the extension is `.png`; a static PNG normally uses only `IHDR`, `IDAT`, and `IEND` plus optional non-animation ancillary chunks.
9. Search `a:t` text across slides, active layouts, slide master, and unused layouts. Classify:
   - visible slide text;
   - active-layout/master placeholder residue;
   - unused-layout template residue.
10. Inspect metadata consistency:
   - `p:sldSz` dimensions and `type` hint;
   - `docProps/app.xml` slide count and presentation format;
   - creator/last modifier, created/modified dates, generator descriptions;
   - suspicious stale template dates or authors.
11. Render independently:
    - primary renderer or target PowerPoint when available;
    - at least one alternate path such as LibreOffice PDF export or macOS Quick Look;
    - verify rendered page count and aspect ratio.
12. Visually inspect a contact sheet and full-size risk pages for crop, ordering, unreadable evidence, placeholders, labels, and truth boundaries.
13. Crosswalk the authoritative competition requirements against explicit slide evidence. Mark each item `PASS`, `PARTIAL`, or `FAIL`; visual implication is not a substitute for required explanatory content.
14. If the deck prints test/build/smoke metrics, rerun only the commands necessary to verify those claims. Distinguish repository tests, focused tests, browser smoke, and runtime-error scope.
15. Hash the target again. Confirm it did not change. Remove temporary renderer outputs.

## Important package findings

### Full-slide raster decks

A valid image-backed slide generally has one `p:pic`, no other authored slide objects, an embedded image relationship, offset `(0,0)`, extent exactly matching `p:sldSz`, no crop rectangle, and no external link. Do not infer aspect-ratio exactness from `type="screen16x9"` or from full-slide placement alone. Use integer cross-products:

- image is exact 16:9 only when `width × 9 == height × 16`;
- slide is exact 16:9 only when `cx × 9 == cy × 16`;
- source and destination match only when `width × cy == height × cx`.

If the acceptance criterion says **exact**, any non-zero delta is a strict failure even when it is only one EMU or visually negligible. Quantify the implied stretch. `a:stretch` only says the image fills its picture container; it is not proof of distortion by itself.

Also report:

- text is not editable/searchable/accessibility-friendly;
- source pixel ratio versus slide ratio and any stretch percentage;
- one-image-per-slide fidelity advantage versus editability cost.

### Dormant placeholders

PowerPoint templates commonly retain strings such as:

- `Click to edit Master title style`
- `Click to edit Master text styles`
- `Second level` through `Fifth level`
- stale dates
- slide-number tokens

These may exist in `slideMaster*.xml` and `slideLayout*.xml` without rendering. Under strict packaging rules, report them concretely and identify whether the active layout also contains them.

### Metadata mismatch

Actual slide dimensions control most renderers, but conflicting `type="screen4x3"`, `PresentationFormat`, stale `Slides=0`, old author/date fields, or generator fingerprints are packaging and professionalism risks. Treat successful alternate rendering as compatibility evidence, not as proof that metadata is clean.

## Official-content crosswalk

For competition decks, retrieve the authoritative page live when possible. Extract exact required sections and evaluation dimensions. Typical proposal requirements include:

- project background;
- target users and scenarios;
- product functions and flow;
- Agent design (interaction, intent, memory, learning, planning, proactive service, device collaboration);
- technical solution (architecture, model, hardware integration, data path, security/privacy, dependencies/resources);
- business model and go-to-market;
- team background, roles, structure, and partner resources;
- originality/truthfulness statement and any required IP-liability wording.

Do not award a full pass merely because adjacent slides imply a capability. Name missing concepts explicitly.

## Compatibility evidence wording

Report exactly what was exercised:

- `ZIP integrity: PASS`
- `macOS Quick Look first-slide render: PASS`
- `LibreOffice headless PDF export: PASS, N pages`
- `Microsoft PowerPoint: NOT TESTED (not installed)`

Never generalize one renderer result into universal compatibility.

## Read-only discipline

Renderer exports go to a temporary directory. Avoid repository-local conversion outputs. Builds/tests can update ignored caches such as `.next`; only run them when they materially verify deck claims, and disclose that side effect. Never delete or reset pre-existing repository artifacts merely to make the audit appear clean.

## Report shape

Lead with one strict verdict, then separate compound requirements so a partial success cannot hide a strict defect—for example, report PNG dimensions/source ratio, crop/full-slide placement, and slide-to-image aspect matching as distinct PASS/FAIL rows. Include exact bytes, SHA-256, integer cross-product deltas, and any implied stretch. Then separate:

1. hard structural passes;
2. strict failures;
3. official-content crosswalk;
4. truth-boundary assessment;
5. compatibility/packaging risks;
6. measured size and hashes;
7. exact file-change statement.
