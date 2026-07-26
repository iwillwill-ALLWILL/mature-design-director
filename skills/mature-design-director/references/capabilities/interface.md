# Interface and Product Experience Capability

Use this capability for websites, web apps, dashboards, ecommerce, admin products, and **web-rendered** game HUDs. It owns interface-specific product design and real-browser verification. The umbrella `SKILL.md` remains authoritative for final-user intent, art direction, ecosystem adoption, approval, and learning.

Do not load this capability merely because an engine-native game HUD is visual. Godot Control, Unity UI Toolkit/uGUI, Cocos UI, and other engine-native systems use the actual engine implementation path plus `references/capabilities/game-ui.md`. Load this interface capability only when the HUD is genuinely rendered with web technology or the task also includes a separate web product surface.

## Choose the mode

| Observable request | Mode | Structural freedom |
|---|---|---|
| Named component, page, state, or isolated problem | Targeted polish | Change only that surface and its necessary states |
| Preserve routes, sections, content, or core flow | Structure-locked upgrade | Replace internals and primitives; preserve visible architecture |
| Comprehensively redesign or de-AI the product | Full product optimization | Recompose the journey when evidence supports it |
| Prior pass produced little visible/user value | Failed-polish recovery | Stop incremental styling; re-scope the visible delta |

Explicit constraints win. “Do not change structure” does not prohibit accessible wrappers, new component files, or replacing a weak implementation, but it does prohibit silent information-architecture changes.

## Context and scope gate

Before editing:

1. inspect Git status and preserve unrelated work;
2. run the read-only scanner:

```bash
python3 scripts/frontend/scan_frontend_project.py <repo-root>
```

3. inspect package scripts, routes, tokens, theme, fonts, assets, current primitives, data flow, and design specs;
4. run the actual product and inspect desktop plus phone before deciding the direction;
5. identify the product promise, primary action, hesitation, success signal, failure/recovery path, and locked behavior;
6. list auth/session, persistence, payment, purchase/claim, save/export/delete, and API contracts that visual work must not break.

Completion criterion: the scope states what may change, what is locked, and what visible/user delta will prove the work mattered.

## Information-budget contract

Treat the interface as a decision surface, not a database renderer.

Every visible element must support at least one of:

- current action;
- decision;
- trust/evidence;
- status/feedback;
- recovery;
- essential domain meaning.

Delete, defer, group, or progressively disclose everything else. Remove repeated explanations, raw API/schema names, provider/model labels, internal IDs, fake metrics, speculative fields, and developer narration. More backend capability is not a reason to expose more UI.

Preserve enough context for orientation and recovery; minimalism must not erase state, provenance, safety, or a required comparison.

## Product-specific art direction

Write the direction in product terms before styling:

- audience and operating context;
- dominant content/action;
- typography roles;
- palette roles grounded in product material or meaning;
- surface and spacing rhythm;
- media role and crop behavior;
- motion/feedback grammar;
- one signature memory point.

Reject a direction that could be pasted unchanged onto an unrelated AI SaaS page. Remove card soup, arbitrary bento grids, gradient-orb heroes, universal glow, excessive pills, icon circles, fake KPI blocks, and repeated equal-weight sections.

When a final-quality visual asset is materially needed, define its job, source truth, composition, crop, palette, and responsive placement, then use `references/capabilities/image.md` or the applicable illustration pipeline. Do not downgrade the design to gradients or empty placeholders because no asset was supplied.

## Mature foundations

Keep and extend the current system when it is sound. Otherwise use `references/mature-ecosystem-registry.md` and the catalog to compare focused candidates for the actual missing layer:

- accessible primitives;
- forms and validation;
- tables/virtualization;
- charts/visualization;
- editor/canvas/map/3D;
- motion and transitions;
- token/export tooling.

Adopt one primary system plus a small number of orthogonal primitives. Do not run parallel component libraries for taste variety. Record concrete capability, version, license, spike result, bundle/runtime cost, and why custom code is still necessary.

A component library owns behavior and accessibility; it does not own information architecture or product identity.

## Implementation passes

Implement in this order unless the product demands another dependency order:

1. content deletion and progressive disclosure;
2. information hierarchy and product composition;
3. typography and responsive rhythm;
4. accessible primitives and component behavior;
5. initial, loading, empty, disabled, unavailable, error, success, undo, and recovery states;
6. real media, trust, and evidence treatment;
7. motion, feedback, pointer/coarse-pointer behavior, reduced motion, and sensory polish;
8. final-user copy and removal of demo/developer residue.

Do not present a CSS palette, shadow, glow, or hover pass as a premium redesign. The visible delta must affect comprehension, action, trust, continuity, or product identity.

## Structure-locked gate

For a structure-locked upgrade, record before/after inventories of:

- routes;
- visible sections and their order;
- primary actions;
- content meaning;
- navigation model;
- required states.

Internal decomposition may change. The before/after gate fails when a route, section, primary action, or meaning disappeared, moved, or changed without explicit authorization.

## Failed-polish recovery

When a prior pass had little effect:

1. stop adding micro-effects;
2. compare the current product with the previous accepted baseline at the same viewports;
3. identify whether the real cause is weak hierarchy, unchanged composition, bad media, generic typography, missing states, or an implementation not visible in the actual runtime;
4. define 3–5 observable changes with screenshots/journey evidence;
5. build one representative route before propagating;
6. discard the rejected grammar rather than renaming it.

## Real-browser release matrix

A substantial frontend task is incomplete until the real running product passes:

- project typecheck, lint, tests, and production build;
- production/local-server canary using the intended build mode;
- desktop, tablet when relevant, and phone viewports;
- every primary route at consistent dimensions;
- the primary journey end to end, including input, process, result, return, and recovery;
- long labels, sparse/empty data, disabled/unavailable, loading, error, and success states;
- keyboard, focus, pointer, coarse pointer, safe area, sticky UI, virtual keyboard, and reduced motion where applicable;
- font/media loading, crop/focal point, overlays, responsive action reachability, and performance sufficient for context.

Create a same-size route contact sheet and inspect the whole product for cross-route identity, density, margins, hero scale, chrome, imagery/control harmony, and rhythm. Headless screenshots and DOM geometry are supplemental; they do not replace interactive visual inspection.

Any route that looks like a separate template blocks completion even when the suite is green.

## Writeback

Interface-specific lessons go into this capability or a linked sanitized case. Tool/repository maintenance belongs in the ecosystem registry. Cross-medium doctrine belongs in the umbrella. Temporary route screenshots, private project paths, and customer assets remain project-local.