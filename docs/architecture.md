# Architecture

## Design goal

The system must remain vertical: one creative authority delegates narrower output capabilities, which delegate mechanics. No layer may compete with the layer above it for the same decision.

## Layers

### 1. Constitution

`skills/mature-design-director/SKILL.md` owns the authentic final-audience encounter, authored direction, truth/rights, cross-medium coherence, the seven-stage flow, final acceptance, and learning boundaries. It intentionally contains no universal font, color, radius, layout, density, or motion preset.

### 2. Capability graph

`references/capability-registry.json` is the only machine-readable route map. It declares:

- authority ownership and delegation boundary;
- the global split between creative foundations and assembly mechanics;
- ordered production stages and completion semantics;
- one artifact lifecycle with evidence-gated transitions, state-driven foundation/mechanics obligations, release states, and a terminal rejection state;
- authority-level release evidence;
- capabilities with accepted requests, output contracts, contract paths, creative-foundation roles, mechanics roles, and medium-specific evidence. Each output contract declares the foundation/mechanics roles, delivered classifications, and primary-artifact suffixes required to claim that natural artifact class;
- ecosystem, resource, and learning paths.

The validator understands the registry schema, not the current capability names. Adding a valid output capability does not require editing validator constants. Recognizable natural-format probes are mechanics adapters keyed by format/container, never by capability or project name; a genuinely new opaque format needs one tested adapter rather than a suffix-only exception.

### 3. Capability contracts

`references/capabilities/` contains the narrow creative decisions that only one output class needs. Contracts may link patterns, but they do not restate the constitution or own file/engine mechanics.

Current capabilities:

- interface;
- presentation;
- document;
- motion;
- image;
- game UI;
- sprite;
- visual explanation;
- spatial/3D/realtime;
- sound/music/voice.

### 4. Creative foundations and mechanics

Creative foundations author the dominant visible or audible language: an approved product system, artboard, deck grammar, game art bible, real content/media, licensed asset system, or selected custom source that has passed representative proof. Assembly mechanics implement, render, export, encode, or run that foundation. A code library, generator, browser, office authoring API, game engine, DAW, or renderer does not become a creative foundation merely because it produced a file.

Mechanics roles remain portable concepts. An available runtime maps a role to an actual tool or external skill only after the creative foundation, native artifact class, and evidence needs are known.

Production projects live in `ecosystem-catalog.json`; creative Agent Skills live in `creative-skill-sources.json`. Neither file is a bulk-install list.

### 5. Evidence

Capabilities inherit authority release evidence and add medium-specific evidence IDs. Evidence comes from the actual editable, rendered, exported, playable, printable, or listenable artifact. Representative direction selection and complete-artifact critique are separate stages and require a reviewer other than the producing agent plus named mature benchmarks where declared. Automated checks may establish technical facts but never certify taste or final-user fit.

Each project instantiates the registry in `.hermes/design/artifact-release.json`. The generic validator binds the exact primary artifact, output class, delivered classification, artifact suffix and recognizable format/container identity, state history, evidence subject hashes, creative foundations, mechanics, reviewer identity, and any adopted delegation output. Multi-file ZIP artifacts additionally carry `artifact-manifest.json`, which binds the exact payload set and a format-valid natural primary entrypoint. Entering `production-candidate` already requires complete working/rendered/native-context evidence; whole-artifact comparison then controls `release-candidate`. A concept proof, renamed plain-text file, README/source generator, unmanifested bundle, parallel creative authority, timeout/no-summary delegation, or mechanics-only record cannot enter `delivered`.

### 6. Learning

Raw task state stays project-local. A lesson enters the shared skill only when it is authorized, sanitized, reproducible, changes future behavior, and has a regression test or evidence gate. It is promoted to the narrowest capability; the constitution changes only for durable cross-capability doctrine.

## Extension test

A proposed addition is architecturally valid only if all are true:

1. It owns a recurring output class that no existing capability can own cleanly.
2. Its inputs and outputs are concrete.
3. Its mechanics can be expressed as adapter roles.
4. Its creative foundations are distinct from those mechanics.
5. Its completion can be proved with existing or new evidence IDs inherited through the shared lifecycle.
6. It does not duplicate constitution rules.
7. It does not require a validator name constant.
8. It does not expose private project state.

If the proposal is only a tool, pattern, provider, style preset, or one-off workflow, place it in the ecosystem, an adapter, a linked pattern, or nowhere.

## Trust boundaries

- Git history and review authenticate policy changes; the validator checks internal consistency and semantics.
- Live maintenance/license checks are point-in-time evidence, not permanent approval.
- Important publication remains a separate user-authorized state.
- The public repository is a manually reviewed mirror. It must never auto-pull private canonical content.
