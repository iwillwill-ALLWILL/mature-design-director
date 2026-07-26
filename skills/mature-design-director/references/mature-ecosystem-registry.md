# Living Mature-Ecosystem Registry

This is a **routing and due-diligence registry**, not a frozen claim that every listed project remains best. Versions, licenses, maintenance, pricing, and APIs change. Re-verify the applicable layer from official sources at task time.

## Coverage rule

For each materially relevant layer:

1. inspect this registry and the current project's existing stack;
2. query official docs, GitHub releases, package registries, and live examples;
3. compare at least three credible maintained candidates when three exist;
4. verify the actual license text, not a blog or GitHub classifier alone;
5. run the smallest useful integration spike for the leading candidate when fit is uncertain;
6. record adopted capability and rejection reason in the adoption ledger;
7. update this registry only when a candidate was meaningfully verified or adopted.

“All mature projects” means broad, current coverage of the relevant landscape—not installing every library or dumping search results into a final artifact.

## Candidate record schema

Each promoted candidate should record:

```text
Name · official URL · exact layer · layer family · tags · repository · repository provider when not GitHub
License hint · accepted live SPDX tokens · manual-review flag · license source · license verification date
Best for · Risk/not for · Repository-health verification date
```

Avoid hard-coded star counts in durable guidance; they stale quickly. Prefer release/version/date, archived state, current docs, and executed project fit.

## Structured catalog and live audit

`references/ecosystem-catalog.json` is the machine-readable candidate index. At its 2026-07-25 expanded baseline it contains **104 live repositories across 63 exact layers and 14 layer families**: 102 GitHub projects and 2 official GitLab projects. All 104 repository metadata queries and all 104 license-source checks completed; none was archived, none crossed the two-year stale-review threshold, and no repository query failed. Explicit `accepted_spdx` comparison produced **77 matches, 25 `LICENSE_REVIEW` results, and 2 `REPOSITORY_REVIEW` results**. The two repository reviews are the replayable result of the current public GitLab project responses omitting a boolean archived field; if that field becomes available, their fixed `NOASSERTION` license metadata will instead keep them in `LICENSE_REVIEW`. Manual review covers `NOASSERTION`, open-core, custom, multi-license, third-party-component, model, dataset, trademark, hosted-service, distribution, and asset-license boundaries.

`references/ecosystem-audit-baseline.json` preserves the full repository-metadata result with UTC audit time, catalog SHA-256, auditor SHA-256, repository identities, status counts, and zero operational failures. Deep validation fails when the catalog or auditor changes without a fresh live baseline. License-source reachability remains a separate URL canary because an accessible URL is provenance evidence, not a license decision.

This proves current repository health only. It does not prove product fit, output quality, asset rights, model rights, or a future license. Before a material adoption, run:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/audit_ecosystem.py
python3 scripts/audit_ecosystem.py --layer motion
python3 scripts/audit_ecosystem.py --family game-development
```

The audit uses authenticated `gh` for GitHub when available, otherwise standard-library GitHub REST with `GITHUB_TOKEN`/`GH_TOKEN`; anonymous mode is suitable only for a layer or family small enough to stay within GitHub's public rate limit. Explicit `repository_provider: gitlab` rows use the encoded official GitLab project endpoint. Unknown providers are rejected before network access. Exact `--layer` remains available while `--family` audits related layers such as all motion, visual-authoring, or game-development candidates. It compares live SPDX identifiers only against each catalog row's explicit `accepted_spdx` array—never against prose or substrings—and also honors `manual_license_review`. `accepted_spdx` itself is fail-closed against the 727 identifiers in the pinned official SPDX License List 3.28.0 snapshot at `references/spdx-license-ids.json`; `NOASSERTION`, `LicenseRef`, `DocumentRef`, arbitrary lookalikes, and license expressions are not accepted policy tokens. Every record carries `license_source_url` and `license_verified_at` for provenance. The audit flags archived, stale, inaccessible, unknown repository state, exact SPDX differences, every `NOASSERTION`, and every policy-mandated manual review. Such repositories are reported as `LICENSE_REVIEW` or `REPOSITORY_REVIEW`, not `OK`; strict audit intentionally exits nonzero, and a concrete adoption must record its separate manual license decision in the adoption ledger. Do not silently weaken the gate to make a degraded dependency pass.

## Frontend and interactive product routing

| Needed capability | Default route | Alternatives / escalation | Do not confuse it with |
|---|---|---|---|
| Broad React product UI | extend the project's existing system; otherwise compare MUI, Ant Design, Mantine, Chakra | shadcn/ui when source ownership matters | finished visual identity |
| Accessible custom behavior | Radix, React Aria, Ariakit, Floating UI | specialist native controls when the platform already solves it | art direction or information architecture |
| Dense data interface | TanStack Table plus one existing UI system | virtualization only when measured | making every datum visible at once |
| Standard interactive charts | ECharts or Recharts | Observable Plot for concise statistical views | infographic art direction |
| Novel explanatory visualization | D3 | authored SVG/canvas or a specialist infographic skill | an excuse to build every chart from scratch |
| Rich text/editor | Tiptap or Lexical after model and collaboration review | mature hosted/editor products when ownership cost is high | a weekend contenteditable implementation |
| Editable canvas | Excalidraw for hand-drawn; tldraw after license review | bespoke canvas only for a differentiating product behavior | a generic whiteboard bolted onto the product |
| Maps | Leaflet for light 2D; MapLibre for vector maps | deck.gl for GPU layers; CesiumJS for globe/3D tiles | free map tiles/geocoding/data rights |
| Product state motion | Motion | AutoAnimate for small layout continuity | decorative movement everywhere |
| Directed timeline/scroll | GSAP after current-license review; Lenis only when scroll is part of the concept | Swup for route transitions | accessibility-safe defaults |
| Web 3D | Three.js; Babylon.js for engine-level features | React Three Fiber for React scene ownership | a premium design by itself |
| Rich 2D canvas | PixiJS | p5.js for intentional creative coding | programmatic filler art |
| Component state/review workbench | Storybook | existing framework-native previews when already proven | a component gallery is not product IA or visual identity |
| Automated accessibility baseline | axe-core embedded in the real browser/component tests | Pa11y for repeatable page/CI audits | replacement for keyboard, screen-reader, cognitive, content, and motion review |
| Visual regression | existing Playwright screenshots first; reg-suit when review/storage workflow is needed | project-native snapshot infrastructure | proof of semantic correctness or permission to approve every pixel diff |
| Authored vector animation playback | Lottie Web when the product already owns a reviewed Lottie asset pipeline | CSS/Motion for native interface-state movement | an authoring system, reduced-motion policy, or license for embedded fonts/images |

Start with `references/capabilities/interface.md` and this registry, then live-verify. One primary system plus a few orthogonal primitives is healthier than parallel component libraries.

## Presentation, document, diagram, and image routing

| Delivery requirement | Default route | Alternatives / escalation | Critical boundary |
|---|---|---|---|
| Native editable PPTX | PptxGenJS with presentation mechanics and `references/capabilities/presentation.md` direction | python-pptx for Python inspection/manipulation | code assembles an authored system; rectangles are not art direction |
| Dynamic HTML deck | Slidev | reveal.js; Quarto for technical publishing | browser fidelity is not native PowerPoint editability |
| Fast Markdown deck | Marp | Quarto | not the default for high-end freeform visual narrative |
| Precision PDF/report | Typst | Quarto/Pandoc conversion pipeline | test the actual required editable source format |
| Office conversion/render check | LibreOffice | target Microsoft Office canary when required | LibreOffice output is not proof of Microsoft Office fidelity |
| Formal editable diagram | diagrams.net | D2 or Mermaid when text-defined source is valuable | auto-layout must be manually composed and inspected |
| Visual thinking | Excalidraw | specialist whiteboard/canvas | hand-drawn style is not always final-brand appropriate |
| Raster production | Sharp/libvips for scalable pipelines; ImageMagick for broad operations | native editor for nuanced retouching | batch processing is not visual authorship |
| Vector/interface authoring | Penpot for collaborative product design; Inkscape for mature desktop SVG/illustration | Graphite for procedural illustration; SVG-Edit for focused embeddable SVG editing | authoring software does not create hierarchy, identity, or illustration quality |
| Icon system | one coherent licensed family through Iconify | project-native icon package when already established | permission to mix unrelated visual languages or ignore per-set licenses/trademarks |
| Font engineering | FontTools for inspection, subsetting, and variable-font operations | project-native build integration | permission to embed or redistribute the selected typeface |
| Desktop publishing/prepress | Scribus when editable page layout and print controls matter | Typst/Quarto for code-first documents | PDF generation alone is not print, font, profile, bleed, or output-intent proof |
| Digital painting/illustration | Krita | specialist drawing/painting workflow and licensed brush/reference sources | brushes and generated texture are not an art direction |
| Raster compositing/retouching | GIMP after component/plug-in review | product-image specialist or a proven commercial editor | repository license is not permission for imported assets or client imagery |
| RAW photo development | darktable or RawTherapee after a color/export canary | target camera/vendor pipeline when profiles demand it | technical controls do not guarantee coherent grading across a set |
| SVG cleanup | SVGO | manual source preservation | aggressive optimization can break IDs, viewBoxes, animation, and accessibility |
| Background removal | rembg | `references/capabilities/image.md` plus configured image editing/generation for scene creation | inspect hair, transparency, shadow, reflection, and model license |
| Cross-platform tokens | `design-md` plus Style Dictionary | platform-native token tools | token machinery cannot decide semantics or taste |

Generated images are useful for illustrative scenes and concept-specific assets, but never as factual product evidence. Keep evidence crops, editorial art, icons, and decorative imagery semantically distinct.

Inkscape and Scribus are tracked from their official GitLab repositories instead of stale or unofficial GitHub mirrors. Their metadata is live-audited, but unknown archived/SPDX fields deliberately remain `REPOSITORY_REVIEW`; inspect the recorded official license source before adoption.

## Game engine, in-engine UI, and sprite routing

Do not confuse a web HUD, an engine-native interface, a sprite editor, and a complete game-production foundation:

| Need | Default comparison set | Narrow execution route | Boundary |
|---|---|---|---|
| General open 2D/3D engine | Godot; compare Bevy for Rust/code-first ownership | project guide plus engine-specific implementation | engine defaults and demo assets are not a finished game identity |
| UI-heavy cross-platform/mobile game | Godot, Cocos Creator, or GDevelop after terms review | game UI specialist only when producing the UI asset/behavior contract | hosted services, stores, trademarks, and exports may have separate terms |
| Compact Lua-driven 2D runtime | Defold after custom-license review | engine implementation plus the narrow UI/sprite specialist actually needed | source availability is not standard OSI licensing |
| Pixel-art sprite and frame animation | Pixelorama or LibreSprite | `references/capabilities/sprite.md` only when actual sprite/frame production is requested | do not load sprite production for layout-only HUD work |
| Engine HUD layout/interaction | existing engine UI system first | `references/capabilities/game-ui.md` for authored UI assets; `references/capabilities/interface.md` only for genuinely web-rendered HUDs | web components and engine scene/control systems are not interchangeable |

Run `--family game-development` before materially adopting an engine or sprite editor, then inspect official export, console, service, asset-store, and license terms separately.

## Video, motion, audio, and 3D routing

Choose **one timeline owner** for each production:

| Production shape | Timeline owner | Supporting layers | Boundary |
|---|---|---|---|
| Deterministic product film | Remotion, or the existing proven composition stack | Playwright truth capture, FFmpeg encode/probe, Whisper caption baseline | Remotion's entity-size license must be checked; automation footage is not a finished edit |
| TypeScript explanatory motion | Motion Canvas | Manim for mathematical grammar | neither is a general footage NLE |
| Greenfield programmable editing | Revideo after a spike | FFmpeg for final media operations | do not migrate a stable stack for novelty |
| Human/agent timeline finishing | Palmier Pro after MCP canary | Kdenlive or Shotcut for desktop fallback | timeline edits do not replace story direction |
| Full manual multitrack NLE | Kdenlive or Shotcut | FFmpeg for final verification | do not split final authority across two timelines |
| Desktop/product capture | OBS Studio with a locked scene/source/audio manifest | Playwright for deterministic browser truth capture | a recording setup is not story, edit, privacy clearance, or visual direction |
| Subtitle authoring/repair | Subtitle Edit after Whisper or human transcript | target-platform caption tools | automatic transcript text without timing, line-break, speaker, and language QA |
| Node compositing/VFX | Natron | the chosen NLE/compositor already owning the production | a way to hide product defects or bypass source-truth recapture |
| Timeline interchange | OpenTimelineIO when editorial metadata must cross supported tools | one timeline owner's native format when interchange adds no value | proof that effects, speed, color, relinking, or final render survived the round trip |
| Professional media review | OpenRV for sequence comparison, annotation, and color-aware inspection | target-platform playback and final decode canaries | final-user approval or permission to skip delivery-platform QA |
| 3D film/product scene | Blender | compositor, asset/license ledger, target renderer | primitives and stock materials are not authored 3D design |
| Mathematical/algorithmic explanation | Manim Community | authored typography and narration | do not force this visual grammar onto all videos |
| Traditional 2D animation | compare OpenToonz, Synfig, and Pencil2D by authored style and timeline need | image/paint specialists | third-party brushes/assets have separate licenses |
| Realtime installation/visual | TouchDesigner skill or compare openFrameworks, Processing, and Cinder | capture/encoding pipeline | requires latency, hardware, venue, distribution, and accessibility canaries |
| Generative media workflow | ComfyUI | model-specific pipelines | code, model, custom-node, dataset, likeness, and output rights are separate |
| Speech/captions | Whisper as draft timing/transcript | authored subtitle edit and actual decode inspection | names, numerals, jargon, line breaks, and rhythm need human correction |
| Audio repair/mix | Audacity for focused repair; Ardour when multitrack routing, automation, and finishing justify a DAW | loudness/true-peak measurement | processing cannot repair wrong speaker identity or missing rights |
| Color-managed image/VFX pipeline | OpenColorIO plus OpenImageIO where cross-tool transforms and metadata matter | application-native color management after a target canary | a generic LUT or assumed color space |
| 3D asset finishing | glTF-Transform for deterministic glTF optimization; MeshLab for mesh inspection/repair; Material Maker for procedural PBR authoring | Blender when it already owns scene/material/export authority | asset tooling as a substitute for art direction, source preservation, or target-renderer comparison |

A capture script plus FFmpeg filters is a primitive stack, not automatically a mature editing system. When editorial retiming, scene ownership, reusable overlays, keyframes, or animation-state inspection matter, use a real timeline/composition layer.

## License watchlist

- **GSAP, tldraw, Remotion:** source-visible/custom terms; re-read current license for the actual user/entity and usage.
- **Defold:** custom source-available license; do not describe it as standard SPDX/OSI open source.
- **Cocos Creator and GDevelop:** repository code has permissive portions, but GitHub reports `NOASSERTION`; tooling, services, extensions, assets, trademarks, and exports require separate review.
- **Bevy:** dual MIT/Apache licensing is permissive but the selected license path and notices must be explicit.
- **GIMP:** official development/license evidence lives on GNOME GitLab; components and plug-ins need their own review.
- **LibreOffice:** multi-license framework; inspect current `COPYING` rather than relying on one classifier.
- **FFmpeg:** effective obligations depend on build flags and included components.
- **Fonts, icons, templates, music, stock assets, models, LoRAs, and checkpoints:** project/code license never substitutes for asset/model/output rights.
- **Copyleft tools:** using a desktop tool to produce an artifact is different from distributing or embedding its code; review the actual integration.

## Promotion and removal

Promote a project when:

- official source and license were verified;
- maintenance is credible for the intended horizon;
- a real task or spike proved the capability;
- it fills a recurring layer better than custom reinvention.

Demote or remove when:

- archived, abandoned, or materially incompatible;
- license changes or conflicts with use;
- the capability remains README-only/TODO;
- a stronger maintained foundation replaces it;
- it repeatedly creates more cleanup than value.

Record historical case decisions in a specialist case reference, not as permanent clutter in this registry.
