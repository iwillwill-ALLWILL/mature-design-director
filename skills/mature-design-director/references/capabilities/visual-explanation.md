# Visual Explanation Capability

Use this capability for architecture diagrams, system maps, process flows, timelines, infographics, knowledge comics, data stories, and educational animations. It owns the explanatory model and visual encoding; format-specific tools own Draw.io, Excalidraw, Mermaid, SVG, canvas, slide, or animation mechanics.

## Capability boundary

A visual explanation is a model made visible, not decorated boxes. This capability owns:

- selecting the right explanatory form;
- preserving entities, relationships, sequence, scale, uncertainty, and exceptions;
- visual encoding, annotation, progressive disclosure, and comprehension testing;
- editable source plus rendered proof.

It does not own the underlying architecture, dataset, scientific claim, or proprietary iconography. Confirm the semantic model with source evidence before polishing it.

## Choose the form from the question

| Reader question | Prefer |
|---|---|
| What happens, and in what order? | flowchart, sequence, storyboard, timeline |
| What connects to what? | architecture, network, relationship map |
| What contains or inherits what? | hierarchy, tree, class/entity model |
| Who owns each step? | swimlane |
| How does data change? | data-flow or transformation diagram |
| How do quantities compare? | chart or data story |
| How do ideas combine over time? | infographic, comic, or animated explanation |

Do not use a diagram when concise prose or a table is clearer. Split overview and detail rather than shrinking a crowded single canvas.

## Semantic model first

Write a small source model before drawing:

- entities and stable names;
- relationship type and direction;
- sequence/causality versus mere association;
- boundaries, actors, trust zones, or ownership;
- cardinality, units, scale, and time where material;
- happy path, exception, failure, and recovery;
- source and confidence for non-obvious claims.

Every visible node and connector must map back to this model. Decorative connections, unlabeled arrows, invented infrastructure, and icon-only meaning are failures.

## Visual encoding

- Use position and grouping for the strongest relationship.
- Give color, shape, line style, and iconography one stable semantic meaning each.
- Keep labels short but specific; preserve product/domain nouns.
- Put detail close to the item it explains.
- Use contrast and scale to guide encounter order, not to imply false importance.
- Keep crossings, detours, and long connector runs low; use ports, lanes, or repeated anchors when needed.
- Provide text equivalents for meaning encoded only by color or motion.

A hand-drawn style may increase approachability; a formal notation may increase precision. Choose based on reader and task, not the available tool.

## Production loop

1. Recover the canonical model and existing diagrams.
2. Choose one form and write the semantic source model.
3. Build a monochrome structural draft.
4. Test whether a new reader can answer the target question.
5. Apply the artifact's visual system and only meaningful icons/media.
6. Export editable source and a rendered preview.
7. Inspect labels, connectors, clipping, scale, contrast, and reading order.
8. Revise the semantic source when the picture exposes a model defect.

For animation or comics, prove the key stills/panels first, then add temporal progression. Motion must reveal order or causality; spectacle alone does not justify it.

## Evidence of completion

Deliver only when:

- the source model and final visual agree;
- every relationship and visual encoding has a defined meaning;
- overview and detail remain readable at delivery scale;
- the editable artifact opens in its native tool and the export matches it;
- rendered inspection finds no overlap, clipping, broken connector, pseudo-text, or inaccessible color-only distinction;
- an independent reader can answer the intended question without production narration.
