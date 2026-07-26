# Mature Design Director

**One creative authority. Ten output capabilities. Tools stay tools.**

Mature Design Director is a portable Agent Skill for directing complete user-facing artifacts across interfaces, decks, documents, motion, images, game UI, sprites, diagrams, 3D/realtime work, and sound.

It separates the final audience from the requester or scorer, establishes an adopted creative foundation before implementation, routes only the capabilities the artifact needs, delegates file/engine mechanics to mature tools, and requires a hash-bound release record from the real artifact before any delivered claim.

## Give it to your AI

After installation, ask naturally:

> Use `mature-design-director` to redesign this product for its real end user. Recover the strongest existing foundation, define a specific direction, use mature systems for solved layers, produce the actual artifact, and show me the rendered result after a defect-fix-recheck loop.

For cross-medium work:

> Use `mature-design-director` so the product, deck, film, and campaign images share one design contract. Keep generated atmosphere separate from real product evidence.

## Install

### Hermes Agent

```bash
hermes skills tap add iwillwill-ALLWILL/mature-design-director
hermes skills install mature-design-director
```

Or install directly from the GitHub tap path:

```bash
hermes skills install iwillwill-ALLWILL/mature-design-director/mature-design-director
```

### Codex or another Agent Skills-compatible runtime

Clone the repository, then expose `skills/mature-design-director/` through that runtime's skill directory. The skill follows the open `SKILL.md` convention and keeps runtime-specific tools behind adapter roles.

## The vertical model

```text
final-user intent
      ↓
mature-design-director constitution
      ↓
authentic audience encounter and creative foundation
      ↓
representative proof selected against named mature benchmarks
      ↓
capability registry selects narrow output contracts and mechanics
      ↓
native artifact + independent whole-artifact critique
      ↓
hash-bound lifecycle record → delivered or rejected
      ↓
authorized, sanitized learning returns to the narrowest layer
```

The validator does not contain a list of capabilities, absorbed skills, retained local skills, project names, or an aesthetic blacklist. A new capability is a declarative contract with inputs, outputs, creative-foundation roles, mechanics roles, and evidence. The validator checks the graph and project release records; human or independent comparative review still owns taste.

## What is included

- Seven-stage production flow: intent, foundation, direction, selection, production, critique, delivery and learning.
- Ten capabilities: interface, presentation, document, motion, image, game UI, sprite, visual explanation, spatial/realtime, and sound.
- One cross-medium artifact lifecycle with separate creative-foundation and assembly-mechanics layers.
- Hash-bound project release records that bind the primary natural artifact, verify recognizable format/container identity, require an exact payload manifest for multi-file ZIPs, and reject concept-proof promotion, README/source-generator stand-ins, mechanics-only evidence, self-review, timeout delegation output, and native-medium overclaims.
- Governed research over mature public creative skills and 104 production projects.
- Truth, rights, accessibility, privacy, editability, and delivery-state discipline.
- Whole-artifact review rather than source-code confidence.
- Project-local private learning with explicit promotion and redaction rules.
- Offline contract tests and an optional manual live ecosystem audit.

## What it is not

- not a universal house style;
- not a bulk collection of upstream skills;
- not a replacement for PowerPoint, Blender, FFmpeg, game engines, image generators, or design systems;
- not a claim that GitHub or its creative ecosystem is permanently exhaustive;
- not an automated approval or publication bot.

## Verify

```bash
python3 skills/mature-design-director/maintenance/validate_skill.py
python3 -m unittest discover -s skills/mature-design-director/tests -p 'test_*.py'

# Before claiming a project artifact is delivered:
python3 skills/mature-design-director/maintenance/validate_skill.py \
  --artifact-record /path/to/project/.hermes/design/artifact-release.json \
  --project-root /path/to/project
```

Architecture and extension rules are in [`docs/architecture.md`](docs/architecture.md). Source and licensing boundaries are documented inside the skill.

## License

MIT. Third-party source/data notices remain under their original terms; see [`NOTICE.md`](NOTICE.md).
