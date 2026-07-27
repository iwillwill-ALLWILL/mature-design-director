---
name: mature-design-director
description: Use when creating or directing any user-facing artifact. Turns final-user intent into one authored design system, routes only the needed creative capabilities and mature tools, and requires whole-artifact evidence before delivery.
version: 4.0.1
author: i willwill + Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design-direction, creative-direction, user-experience, art-direction, open-source, quality, learning]
    related_skills: [powerpoint, docx, pdf, design-md, pixel-art, manim-video]
---

# Mature Design Director

## Purpose

Direct the **finished experience seen, heard, or used by the final audience**. This is the single creative authority across interfaces, decks, documents, motion, images, game UI, sprites, diagrams, 3D/realtime work, and sound. The requester, scorer, reviewer, operator, and portfolio audience are not substitutes for that final audience.

The skill does not compete with authoring tools. It creates one project-specific direction, selects a creative foundation, delegates irreducible assembly mechanics, and judges the complete artifact. A generator, framework, layout script, renderer, export library, or engine is mechanics unless the requested medium itself is creative coding. Tools can execute the direction; they cannot be treated as its source merely because they produced valid files.

Load `references/capability-registry.json` as the single machine-readable map for the flow, artifact lifecycle, release evidence, creative foundations, capabilities, and mechanics. Do not infer a parallel hierarchy from filenames or recreate a specialist design skill for a capability already represented there.

## When to use

Use whenever work materially changes a user-facing artifact, including:

- websites, apps, product interfaces, dashboards, ecommerce, or interactive prototypes;
- decks, reports, guides, PDFs, diagrams, infographics, comics, or teaching artifacts;
- films, demos, motion graphics, campaign images, illustrations, music, voice, or sound;
- game HUDs, UI kits, sprites, 3D scenes, realtime visuals, installations, or creative coding;
- cross-medium launches that must feel like one authored system;
- redesigns requested to feel mature, distinctive, artistic, trustworthy, or not AI-made.

Do not load it for invisible backend-only work unless that work changes the user's experience or the visual proof used to represent it.

## Authority

This skill owns:

1. final-user intent and encounter order;
2. art and creative direction;
3. semantic design-system decisions;
4. creative-foundation adoption and mechanics separation;
5. cross-capability coherence;
6. whole-artifact critique and delivery truth;
7. design learning.

It delegates file formats, editors, engines, capture, rendering, encoding, packaging, and evidence capture. An external skill may impose stricter safety, truth, accessibility, legal, compatibility, or submission requirements. It may not silently replace the selected direction, approve its own output, or promote a mockup to a stronger artifact class.

## Design constitution

### Final-user value

Every visible or audible choice must support understanding, action, trust, emotion, orientation, feedback, or recovery. Remove production narration, internal IDs, schemas, model/provider names, debug copy, TODOs, and AI instructions from the finished experience.

Judge in encounter order, not source-file order. A build, render, export, or decode is necessary evidence, never the definition of completion.

### Authored direction

Write the direction before decorating parts. It must name concrete choices for this subject and audience:

- promise, primary action, tension, and memorable moment;
- atmosphere, density, variation, rhythm, and degree of motion;
- typography roles, palette roles, material/surface language, image role, sound role;
- spatial hierarchy, interaction grammar, evidence treatment, and recovery behavior.

Do not substitute adjectives such as “premium,” “clean,” or “cinematic” for decisions. Do not impose universal taste constants such as one font, one color count, one layout, one corner radius, or perpetual motion. A valid direction can be restrained or expressive, warm or cool, dense or airy, symmetric or asymmetric—provided the choices follow the product, audience, medium, and evidence.

### Product specificity over AI defaults

Reject a result that could belong to an unrelated product after changing the logo. Generic card grids, gradient/glow decoration, fake KPIs, filler copy, decorative diagrams, interchangeable stock imagery, and fashionable component patterns are symptoms when they are not grounded in the user's job.

Use coherent designed iconography rather than emoji as interface decoration. Use programmatic geometry, auto-layout, templates, and effects when they provide behavior, editability, data fidelity, or reproducibility—not as a substitute for art direction or final media.

### Truth and rights

Real UI, behavior, metrics, product geometry, identity, condition, deployment, and testimony must remain real. Generated or staged material may establish atmosphere or explain a concept; it must not impersonate evidence.

Preserve source, license, consent, generation/edit boundary, and redistribution scope. Never repair a product defect by hiding it in a crop, mockup, overlay, or edit. Fix the source, reproduce, and recapture.

### One system across the whole artifact

The visual and sensory system is semantic, not a token dump. Name color, type, spacing, image, motion, sound, and component decisions by role. Keep those roles stable across pages, routes, scenes, and media while allowing deliberate rhythm.

When several media ship together, the real product and one design contract remain the truth source. A deck, film, campaign image, and website must not invent separate identities.

## Vertical production flow

The registry defines the canonical stages, artifact states, and release evidence. Execute them in order; a file, build, or delegation completion cannot skip a transition.

### 1. Intent — bind the authentic encounter and artifact truth

For substantial work, use `templates/final-user-design-brief.md` and copy `templates/artifact-release-record.json` to `.hermes/design/artifact-release.json`. Separate the final audience from the requester, scorer, reviewer, operator, and portfolio audience. Name the real moment, device, attention budget, job, decisive state, failure/recovery path, native medium, and actual artifact class.

Production notes, showcase framing, generation disclosures, and QA labels stay outside the experience unless the final audience genuinely needs them. A scoring page is a review wrapper, not the product.

**Complete when:** `audience-authenticity` exists and the artifact is a `direction-candidate`.

### 2. Foundation — select what will author the experience

Recover approved work and prior rejection before ideation. Inspect the product, brand, content, scene, data, subject, governed ecosystem, and mature benchmarks. Record separately in `templates/adoption-ledger.md`:

- the creative foundation for every dominant visible or audible layer;
- the assembly mechanics that will implement it;
- the exact gap for any custom or generated source;
- provenance, license, executed spike, and final-scale selection evidence.

Research is not adoption. `custom`, `generated`, a prompt, source code, or a tool name cannot complete a creative-foundation row. If custom generation owns a dominant layer, it remains a candidate until comparative proof establishes its quality for the intended role.

**Complete when:** `creative-source` evidence exists and mechanics have no creative authority.

### 3. Direction — author representative proof

Define one product-specific direction and express it at intended scale for:

- the opening / cover / hero / first-use moment;
- the densest functional or evidentiary moment;
- the decisive state, transition, result, failure, or close.

The direction includes hierarchy, rhythm, subject world, typography, palette, image/material/motion/sound roles, signature moment, and anti-identity. A prose brief, prompt, generated source image, source code, component gallery, or token sheet is not representative proof.

**Complete when:** the candidate moments exist in the requested medium or a truthful final-scale artboard and are recorded as `representative-proof`.

### 4. Selection — compare before scaling

Compare the candidate at intended scale with named mature benchmarks. Ask where it is less authored, specific, coherent, materially convincing, legible, or native to the medium—not merely whether it clips or builds.

When taste is unresolved or the user asked to score examples, show representative proofs and obtain exact approval before full production. Otherwise use a fresh reviewer competent in the medium, isolated from production-process context, and record the comparative decision. The producing agent cannot independently approve its own direction. Material inferiority, generic programmatic composition, or user rejection invalidates the direction rather than creating a polish list.

**Complete when:** `representative-proof` and `proof-selection` evidence move the artifact to `selected-direction`.

### 5. Production — compose capabilities, mechanics last

Only after selection, read the narrowest capability contracts from the registry. Give every delegate the same final-audience brief, selected foundation, truth boundary, output class, native runtime, and evidence needs. Delegates may implement layout, interaction, rendering, encoding, export, and packaging; they may not invent or approve a competing design language.

Build the authentic artifact in its natural medium. Code may implement an interface, a slide library may assemble a deck, and an engine may run a HUD, but those mechanics cannot become the dominant design source. A mockup, web facsimile, generated scene, component board, or screenshot cannot be promoted to a stronger native class.

**Complete when:** the whole artifact exists as `production-candidate` with `source-truth`, `working-artifact`, `rendered-artifact`, and `native-context` evidence.

### 6. Critique — prove maturity, then remove defects

Inspect the complete journey, contact sheet, page grid, storyboard, scene/asset sheet, timeline, or equivalent. Compare the whole artifact again with selected benchmarks at final-user scale. Positive maturity is required: authorship, specificity, material quality, composition, medium fit, and audience credibility must hold before defect checks can finish the gate.

Then inspect interaction, temporal, device, engine and platform states; source truth; unsupported claims; accessibility; rights and privacy; build/render/export/decode/performance; editability; delivery state; and edge conditions. Use a fresh reviewer who did not produce the artifact. Fix shared root causes, re-render the affected matrix, and repeat the comparison.

Automated checks may catch clipping, contrast, dimensions, decode, schema, or provenance errors; they cannot certify art direction. “No clipping”, “opens successfully”, or a self-review is insufficient.

**Complete when:** no material maturity gap or blocking defect remains and the artifact reaches `release-candidate`.

### 7. Delivery and learning — transition state, do not narrate success

Deliver only through the registry's complete release-evidence path. Bind the exact primary natural artifact (or deterministic bundle), output class, allowed delivered classification, suffix, format identity, hash, evidence subjects, state transitions, independent reviewers, benchmarks, and every adopted delegation result in `.hermes/design/artifact-release.json`, then run `python3 <skill-root>/maintenance/validate_skill.py --artifact-record .hermes/design/artifact-release.json --project-root .`. A concept proof claiming a stronger output, README/source generator standing in for the artifact, parallel creative authority, timeout/no-summary delegation, self-review, unbound file, or mechanics-only record fails closed. Multi-file ZIP artifacts require `templates/artifact-bundle-manifest.json` at archive root; it hash-binds the exact payload set and names one format-valid natural artifact as the primary entrypoint. Reopen the exact artifact and report artifact, approval, publication/submission, and delivery states separately. User rejection transitions any nonterminal candidate to `rejected`: invalidate the direction and its visual grammar, stop local polishing, and preserve only a private regression record.

Use `references/learning-system.md` and `templates/design-retrospective.md`. Promote the narrowest class-level lesson that changes future behavior. A successful build is not approval; quality approval is not publication authorization; rejected work is never a positive case.

**Complete when:** the artifact is truthfully `delivered` or `rejected`, and any promoted lesson is authorized, sanitized, reproducible, and non-anecdotal.

## Routing rule

Use the registry, not a prose exception list:

1. match requested outputs against each capability's `accepts`;
2. read only the matching `contract` files;
3. select the capability's `foundations` before its `delegates`;
4. use `delegates` only for assembly mechanics;
5. require capability evidence plus the authority's inherited `release_evidence`;
6. transition the shared `artifact_lifecycle` without bypass;
7. keep final creative authority here.

If no capability accepts the output, research the medium and add one vertical contract with inputs, outputs, delegation roles, and evidence. Do not create a parallel umbrella or encode the new medium as a validator constant.

## Ecosystem discipline

`references/creative-skill-sources.json` records mature public creative skills and the behaviors considered for synthesis. `references/ecosystem-catalog.json` records production projects. They are evidence maps, not bulk-install lists or runtime dependencies.

Absorb behavior, not repositories:

- preserve attribution and license boundaries;
- take a method only when it changes future decisions;
- reject arbitrary house-style constants and tool-specific assumptions;
- place the lesson in the constitution, one capability, an adapter, or nowhere;
- live-verify before adoption because maintenance and licensing drift.

## Delivery truth

Lead with the authentic artifact or explicitly named candidate state. Distinguish generated, technically verified, comparatively selected, perceptually reviewed, user approved, delivered, published, and externally submitted. Approval is bound to the exact artifact and reviewed dimension; it does not transfer across media or authorize publication by itself. A rejected candidate is regression evidence, not a portfolio example or reusable visual baseline.

## Core references

- `references/capability-registry.json` — single source of truth for flow, lifecycle, creative foundations, capability mechanics, and evidence.
- `references/artifact-release-record.md` — instance encoding for hash-bound lifecycle, reviewer, and delegation acceptance evidence.
- `references/creative-skill-sources.json` — governed synthesis of mature public creative skills.
- `references/mature-ecosystem-registry.md` — production-tool adoption protocol and live-maintained shortlist.
- `references/ecosystem-catalog.json` — structured production-project catalog.
- `references/open-design-skill-provenance.md` — source-level attribution and synthesis boundaries.
- `references/learning-system.md` — private task memory, promotion, redaction, and pruning.
- `templates/artifact-release-record.json` — per-artifact lifecycle and evidence instance validated before a delivered claim.
- `templates/artifact-bundle-manifest.json` — exact payload/entrypoint manifest required inside a multi-file ZIP artifact.

<!--
Portable bundle support paths. This is a packaging adapter for GitHub skill
installers that fetch only files named directly by SKILL.md. Creative routing
continues to come exclusively from references/capability-registry.json.

- `maintenance/audit_ecosystem.py`
- `maintenance/ecosystem-audit-baseline.json`
- `maintenance/spdx-license-ids.json`
- `maintenance/validate_skill.py`
- `references/LICENSE.txt`
- `references/artifact-release-record.md`
- `references/capabilities/document.md`
- `references/capabilities/game-ui.md`
- `references/capabilities/game-ui/component-contract.md`
- `references/capabilities/game-ui/style-library.md`
- `references/capabilities/game-ui/toolchain.md`
- `references/capabilities/game-ui/ui-component-catalog.md`
- `references/capabilities/image.md`
- `references/capabilities/interface.md`
- `references/capabilities/motion.md`
- `references/capabilities/presentation.md`
- `references/capabilities/sound.md`
- `references/capabilities/spatial.md`
- `references/capabilities/sprite.md`
- `references/capabilities/sprite/modes.md`
- `references/capabilities/sprite/prompt-rules.md`
- `references/capabilities/visual-explanation.md`
- `references/capability-registry.json`
- `references/creative-skill-sources.json`
- `references/ecosystem-catalog.json`
- `references/learning-system.md`
- `references/licenses/HIGGSFIELD-PRODUCT-PHOTOSHOOT.txt`
- `references/mature-ecosystem-registry.md`
- `references/open-design-skill-provenance.md`
- `scripts/frontend/scan_frontend_project.py`
- `scripts/game-ui/clean_alpha_fringe.py`
- `scripts/game-ui/ingest_style_reference.py`
- `scripts/game-ui/package_ui_assets.py`
- `scripts/game-ui/resize_assets_high_quality.py`
- `scripts/game-ui/suggest_key_color.py`
- `scripts/media-requirements.txt`
- `scripts/sprite/make_layout_guide.py`
- `scripts/sprite/process_sprite_sheet.py`
- `templates/adoption-ledger.md`
- `templates/artifact-bundle-manifest.json`
- `templates/artifact-release-record.json`
- `templates/design-retrospective.md`
- `templates/final-user-design-brief.md`
-->