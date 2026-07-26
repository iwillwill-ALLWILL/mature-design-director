# Architecture

## Design goal

The system must remain vertical: one creative authority delegates narrower output capabilities, which delegate mechanics. No layer may compete with the layer above it for the same decision.

## Layers

### 1. Constitution

`skills/mature-design-director/SKILL.md` owns final-user value, authored direction, truth/rights, cross-medium coherence, the seven-stage flow, and learning boundaries. It intentionally contains no universal font, color, radius, layout, density, or motion preset.

### 2. Capability graph

`references/capability-registry.json` is the only machine-readable route map. It declares:

- authority ownership and delegation boundary;
- ordered production stages and completion semantics;
- evidence types;
- capabilities with accepted requests, outputs, contract paths, adapter roles, and required evidence;
- ecosystem, resource, and learning paths.

The validator understands the registry schema, not the current capability names. Adding a valid output capability does not require editing validator constants.

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

### 4. Adapters and mature foundations

Delegation roles are portable concepts such as browser runtime, office authoring, game engine, 3D authoring, image generation, DAW, or renderer. An available runtime maps a role to an actual tool or external skill after direction and evidence needs are known.

Production projects live in `ecosystem-catalog.json`; creative Agent Skills live in `creative-skill-sources.json`. Neither file is a bulk-install list.

### 5. Evidence

Capabilities reference evidence IDs declared in the registry. Evidence comes from the actual editable, rendered, exported, playable, printable, or listenable artifact. Automated checks may establish technical facts but never certify taste or final-user fit.

### 6. Learning

Raw task state stays project-local. A lesson enters the shared skill only when it is authorized, sanitized, reproducible, changes future behavior, and has a regression test or evidence gate. It is promoted to the narrowest capability; the constitution changes only for durable cross-capability doctrine.

## Extension test

A proposed addition is architecturally valid only if all are true:

1. It owns a recurring output class that no existing capability can own cleanly.
2. Its inputs and outputs are concrete.
3. Its mechanics can be expressed as adapter roles.
4. Its completion can be proved with existing or new evidence IDs.
5. It does not duplicate constitution rules.
6. It does not require a validator name constant.
7. It does not expose private project state.

If the proposal is only a tool, pattern, provider, style preset, or one-off workflow, place it in the ecosystem, an adapter, a linked pattern, or nowhere.

## Trust boundaries

- Git history and review authenticate policy changes; the validator checks internal consistency and semantics.
- Live maintenance/license checks are point-in-time evidence, not permanent approval.
- Important publication remains a separate user-authorized state.
- The public repository is a manually reviewed mirror. It must never auto-pull private canonical content.
