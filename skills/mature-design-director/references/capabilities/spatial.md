# Spatial, 3D, and Realtime Capability

Use this capability for 3D scenes, product visualization, environments, installations, realtime visuals, spatial prototypes, and creative coding whose final experience is primarily spatial or time-reactive. Blender, Rhino, game engines, TouchDesigner, p5.js, Processing, and similar systems remain execution mechanics.

## Capability boundary

This capability owns:

- spatial thesis, scale, camera, light, material, movement, and viewer path;
- deciding what must be modeled, sourced, scanned, simulated, or generated;
- scene coherence across still, animation, and realtime output;
- visual and performance evidence at the intended display.

It does not own CAD correctness, structural engineering, manufacturing tolerances, engine/runtime APIs, or tool installation. A script that creates geometry is not art direction, and a technically valid scene is not a finished spatial experience.

## Spatial contract

Define before production:

- viewer and encounter: still image, orbit, walkthrough, stage, installation, AR/VR, or interactive screen;
- physical or imagined scale and the references that establish it;
- focal subject, camera language, horizon/perspective, and viewer movement;
- lighting motivation, material language, atmosphere, and color behavior;
- interaction inputs and the visual response they control;
- target hardware, resolution, frame budget, duration, loop, and export format;
- truth boundary for products, architecture, measurements, and simulated behavior.

## Mature foundation first

Prefer existing scene systems, licensed assets, material libraries, interchange standards, and engine primitives for solved layers. Verify scale, topology, UVs, material compatibility, rig/animation quality, license, and export path before adoption.

Model custom work where product identity, spatial composition, or interaction requires it. Do not rebuild commodity props or infrastructure for the appearance of craftsmanship.

## Scene production

1. Block scale, camera, focal hierarchy, and viewer path with simple geometry.
2. Prove one hero view and one difficult view before detailed production.
3. Establish light and material response with representative assets.
4. Replace blockout only where final geometry affects silhouette, shadow, reflection, interaction, or truth.
5. Keep scene collections/layers, names, pivots, units, origins, and asset provenance coherent.
6. Add motion and realtime behavior after static composition reads correctly.
7. Optimize after profiling the actual target, not from arbitrary polygon limits.

Use procedural systems for variation, simulation, or controllable structure. Do not present default primitives, noise fields, shader demos, or particle presets as the finished creative idea.

## Camera, light, and material

- Camera choice must express scale and subject, not merely fit the frame.
- Lighting needs a physical or narrative motivation and must preserve form.
- Materials need correct scale, roughness, edge response, and variation; texture detail cannot rescue weak geometry or light.
- Avoid uniform sharpness, perfect repetition, floating contact, implausible reflections, and depth-of-field used to hide defects.
- Preserve exact product geometry, labels, or architectural facts when the output claims fidelity.

## Realtime and interaction

Map each input to a legible visual consequence. Define idle, attract, active, transition, interruption, failure, and reset states. Test latency, frame pacing, resizing, reconnect, long-run stability, and safe fallback on actual hardware when possible.

One system must own final timing. Avoid parallel animation/timeline owners fighting over state.

## Evidence of completion

A spatial artifact is complete only when:

- scale, camera, light, material, and movement support one coherent thesis;
- hero, widest, closest, darkest/brightest, and transition views are inspected;
- no asset/license/scale/orientation ambiguity remains;
- native scene and exported interchange/runtime artifact reopen correctly;
- actual-target performance and interaction states are measured where relevant;
- final stills/video/realtime capture represent the real scene rather than a hidden local substitute.
