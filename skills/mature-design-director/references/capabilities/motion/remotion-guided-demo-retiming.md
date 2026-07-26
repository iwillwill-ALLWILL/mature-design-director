# Guided Remotion retiming for product demos

Use this pattern when a technically clean browser demo still feels too fast or under-guided.

## Honest pipeline classification

Do not call a custom Playwright + FFmpeg capture a mature demo-editing project merely because the primitives are mature. Distinguish:

- **capture:** Playwright/browser recorder;
- **composition:** a real timeline engine such as Remotion;
- **encoding/verification:** FFmpeg;
- **manual editor:** an editor such as OpenCut/Recordly when human timeline work is the chosen workflow.

If the user explicitly asks whether a mature editing/generation project was used, answer literally. A home-grown director overlay is not equivalent to a mature composition timeline.

## Clean-source rule

When moving to programmatic composition, re-record a clean source if the old source has baked captions, chapter cards, or explanatory callouts.

The clean source may keep:

- genuine product UI;
- real cursor/click feedback;
- a neutral branded transition mask that hides asynchronous state changes;
- a stable branded outro if it is already correct.

The composition layer should own:

- chapter copy;
- progress navigation;
- numbered callouts and arrows;
- music and fades;
- scene-specific retiming.

This prevents two competing caption systems and lets guidance be revised without another product recording.

## Scene-specific retiming

Do not globally slow the whole video. Measure source scene boundaries, then assign output time according to comprehension needs.

A useful 55–65 second distribution is:

- hero: 4–6 s;
- input: 6–8 s;
- strongest proof: 9–12 s;
- action/transformation: 7–9 s;
- exception/conflict: 9–12 s;
- output: 6–8 s;
- outro: 5–7 s.

Calculate each segment's playback rate:

`playbackRate = sourceDuration / outputDuration`

Test that rates stay within a deliberate range. Around 0.45× is a practical lower guard for UI footage; below that, cursor and scroll motion often feel broken. Freeze a stable frame deliberately if more reading time is needed instead of driving playback arbitrarily slower.

## Guidance grammar

Use one consistent hierarchy:

1. **Progress rail:** small, persistent only during UI scenes; shows where the viewer is in INPUT → PROOF → ACTION → REVIEW → OUTPUT.
2. **Chapter card:** appears only during a branded transition mask; one headline and one detail sentence.
3. **Scene guidance:** at most one task-specific overlay per scene.
4. **Proof connector:** numbered source and destination boxes plus a single arrow. Make the relationship explicit (for example, selected fact → exact box on original PDF).
5. **Conflict card:** show the conflicting values themselves (`A ≠ B`) and state the safer policy.

Do not add generic captions that repeat visible UI text. Guidance must answer either “where should I look?” or “why does this matter?”

## Remotion timeline pattern

For a clean source video and a 30fps composition:

- represent every source interval as data: `sourceStart`, `sourceEnd`, `frames`, `kind`, `step`;
- derive contiguous output `start/end` frames from the array;
- render each interval inside a `Sequence`;
- use `Video trimBefore`, `trimAfter`, and `playbackRate` for independent retiming;
- keep overlays inside the same Sequence so `useCurrentFrame()` is scene-local;
- add music with `Audio` and frame-based fades.

In current Remotion media APIs, `trimBefore` and `trimAfter` are interpreted in composition-frame units. Confirm against the installed type/source before coding; API names have changed across Remotion versions.

## Pre-render validation

Before rendering the full composition:

1. render stills for hero, every chapter, every guided scene, and outro;
2. make a contact sheet;
3. fail closed on wrong pointer geometry, guidance overlap, clipping, or duplicate text;
4. run timing tests for total frames, contiguous segments, chapter count, and playback-rate limits;
5. run TypeScript compilation.

After full render:

- verify expected frame count and stable CFR;
- decode the whole file;
- scan literal white/black frames;
- inspect every transition at before/enter/middle/exit/after;
- inspect guidance at multiple animation phases;
- inspect first and final frames;
- verify audio peak and stream duration.

Container duration is not source truth for variable-frame-rate browser captures. Derive usable duration from decoded frames or normalized CFR output, then make audio and composition duration agree with that real timeline.
