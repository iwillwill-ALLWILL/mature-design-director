---
name: mature-design-director
description: Use when creating or directing any user-facing artifact. Turns final-user intent into one authored design system, routes only the needed creative capabilities and mature tools, and requires whole-artifact evidence before delivery.
version: 3.0.1
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

Direct the **finished experience seen, heard, or used by the final audience**. This is the single creative authority across interfaces, decks, documents, motion, images, game UI, sprites, diagrams, 3D/realtime work, and sound.

The skill does not compete with authoring tools. It creates one project-specific direction, selects the narrow creative capability contracts, delegates irreducible mechanics to mature systems, and judges the complete artifact. Tools own execution; this skill owns why the artifact exists, how it should feel and work, and what evidence makes it finished.

Load `references/capability-registry.json` as the single machine-readable map. Do not infer a parallel hierarchy from filenames or recreate a specialist design skill for a capability already represented there.

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
4. mature-foundation adoption;
5. cross-capability coherence;
6. whole-artifact critique and delivery truth;
7. design learning.

It delegates file formats, editors, engines, capture, rendering, encoding, and tool-specific operations. An external skill may impose stricter safety, truth, accessibility, legal, compatibility, or submission requirements. It may not silently replace the approved direction with its own aesthetic defaults.

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

The registry defines the canonical stages. Execute them in order and return when evidence invalidates an earlier decision.

### 1. Intent

Inspect supplied material and define audience, context, promise, action, emotion, trust, hesitation, failure, recovery, medium, and truth boundary. For substantial work, use `templates/final-user-design-brief.md`.

**Complete when:** another person can judge fit from the user's perspective without reading implementation code.

### 2. Foundation

Recover prior approved work before fresh ideation. Search project/session history for exact approvals and rejections. Research current mature creative skills, production tools, products, patterns, licensed assets, and design systems.

For every material layer, compare credible maintained candidates when alternatives exist. Verify official source, maintenance, license, capability fit, integration cost, accessibility/export behavior, and a smallest useful spike. Record actual adoption or rejection in `templates/adoption-ledger.md`.

**Complete when:** every material layer has an owner—an existing system, adopted mature capability/tool, authorized asset source, generated media path, or justified custom work.

### 3. Direction

Create one semantic design contract. If taste is unresolved, make two or three genuinely different directions rather than variations of one template. Translate vague input into functional roles and observable behavior; keep enough creative space for medium-specific interpretation.

**Complete when:** the direction is specific enough to constrain production but does not hardcode an arbitrary house style.

### 4. Proof

Before scaling, prove representative risk:

- the first/hero/cover/listening moment;
- the densest functional or evidence moment;
- the decisive transition, failure/recovery, or closing moment.

Use real copy and representative media. Inspect at intended scale. A rejected direction becomes non-final; do not keep polishing its visual grammar under another name.

**Complete when:** one direction has explicit evidence of fit or user approval.

### 5. Production

Read only the capability contracts selected from `references/capability-registry.json`. A task may compose several capabilities, but each output layer has one owner. Load external mechanics only after the direction, source truth, output contract, and evidence needs are known.

Let mature systems own the solved layer for which they were adopted. Custom work creates product-specific differentiation; it must not be an excuse to avoid mature foundations.

**Complete when:** the complete artifact exists in its real editable/playable/native form and the production stack matches the adoption record.

### 6. Critique

Evaluate the actual rendered, exported, playable, printable, or listenable candidate—not source confidence. Use the capability's evidence types from the registry.

At minimum:

1. technical integrity checks;
2. complete-artifact overview;
3. full-scale review of fragile moments;
4. realistic device/runtime/context checks;
5. truth, accessibility, rights, and privacy review;
6. independent adversarial critique;
7. defect fix and repeat of the same matrix.

Do not convert taste into shallow lint. Automated checks may catch clipping, contrast, dimensions, decode, schema, or provenance errors; they cannot certify art direction, emotional fit, or overall coherence.

**Complete when:** no unresolved defect materially harms comprehension, action, trust, identity, accessibility, truth, rights, or delivery compatibility.

### 7. Learning

Use `references/learning-system.md` and `templates/design-retrospective.md`. Keep raw task state and private assets in project-local `.hermes/design/`. Promote only an authorized, sanitized, reproducible lesson that changes future behavior and includes a regression gate.

Patch the narrowest capability contract. Change the constitution only for repeated cross-capability lessons or explicit durable doctrine. Add a new capability only when no existing contract can own a recurring output class cleanly.

**Complete when:** the next related task starts from stronger evidence without exposing private work or accumulating duplicate rules.

## Routing rule

Use the registry, not a prose exception list:

1. match requested outputs against each capability's `accepts`;
2. read only the matching `contract` files;
3. use `delegates` to select available mechanics or mature projects;
4. require the referenced `evidence` types;
5. keep final creative authority here.

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

Lead with the actual artifact or preview. Distinguish generated, technically verified, perceptually reviewed, user approved, published, and externally submitted. Approval is bound to the exact artifact and reviewed dimension; it does not transfer across media or authorize publication by itself.

## Core references

- `references/capability-registry.json` — single source of truth for flow, capabilities, delegation, and evidence.
- `references/creative-skill-sources.json` — governed synthesis of mature public creative skills.
- `references/mature-ecosystem-registry.md` — production-tool adoption protocol and live-maintained shortlist.
- `references/ecosystem-catalog.json` — structured production-project catalog.
- `references/ecosystem-audit-baseline.json` — point-in-time live audit evidence.
- `references/open-design-skill-provenance.md` — source-level attribution and synthesis boundaries.
- `references/learning-system.md` — private task memory, promotion, redaction, and pruning.

<!--
Portable bundle support paths. This is a packaging adapter for GitHub skill
installers that fetch only files named directly by SKILL.md. Creative routing
continues to come exclusively from references/capability-registry.json.

- `references/LICENSE.txt`
- `references/capabilities/document.md`
- `references/capabilities/game-ui.md`
- `references/capabilities/game-ui/component-contract.md`
- `references/capabilities/game-ui/style-library.md`
- `references/capabilities/game-ui/toolchain.md`
- `references/capabilities/game-ui/ui-component-catalog.md`
- `references/capabilities/image.md`
- `references/capabilities/interface.md`
- `references/capabilities/motion.md`
- `references/capabilities/motion/continuous-browser-demo-validation.md`
- `references/capabilities/motion/final-video-handoff.md`
- `references/capabilities/motion/media-provenance-and-repository-isolation.md`
- `references/capabilities/motion/open-source-chinese-narration-macos.md`
- `references/capabilities/motion/palmier-pro-mcp-finishing-workflow.md`
- `references/capabilities/motion/remotion-guided-demo-retiming.md`
- `references/capabilities/motion/remotion-proof-scene-validation.md`
- `references/capabilities/motion/segmented-voice-consistency-mastering.md`
- `references/capabilities/motion/tts-licensing-and-remotion-macos.md`
- `references/capabilities/presentation.md`
- `references/capabilities/presentation/deck-preview-delivery-and-export-contract.md`
- `references/capabilities/presentation/judge-evidence-package-clean-room.md`
- `references/capabilities/presentation/motion-deck-direction-workflow.md`
- `references/capabilities/presentation/official-competition-rule-research.md`
- `references/capabilities/presentation/offline-dynamic-deck-delivery.md`
- `references/capabilities/presentation/static-pptx-package-sanitization.md`
- `references/capabilities/presentation/strict-pptx-submission-audit.md`
- `references/capabilities/sound.md`
- `references/capabilities/spatial.md`
- `references/capabilities/sprite.md`
- `references/capabilities/sprite/modes.md`
- `references/capabilities/sprite/prompt-rules.md`
- `references/capabilities/visual-explanation.md`
- `references/capability-registry.json`
- `references/creative-skill-sources.json`
- `references/ecosystem-audit-baseline.json`
- `references/ecosystem-catalog.json`
- `references/learning-system.md`
- `references/licenses/HIGGSFIELD-PRODUCT-PHOTOSHOOT.txt`
- `references/mature-ecosystem-registry.md`
- `references/open-design-skill-provenance.md`
- `references/spdx-license-ids.json`
- `scripts/audit_ecosystem.py`
- `scripts/frontend/scan_frontend_project.py`
- `scripts/game-ui/clean_alpha_fringe.py`
- `scripts/game-ui/ingest_style_reference.py`
- `scripts/game-ui/package_ui_assets.py`
- `scripts/game-ui/resize_assets_high_quality.py`
- `scripts/game-ui/suggest_key_color.py`
- `scripts/media-requirements.txt`
- `scripts/sprite/make_layout_guide.py`
- `scripts/sprite/process_sprite_sheet.py`
- `scripts/validate_skill.py`
- `templates/adoption-ledger.md`
- `templates/design-retrospective.md`
- `templates/final-user-design-brief.md`
-->