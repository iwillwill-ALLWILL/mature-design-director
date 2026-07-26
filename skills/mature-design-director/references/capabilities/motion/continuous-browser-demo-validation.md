# Continuous browser-demo direction and validation

Use this reference when a real-browser product demo has been rejected for white-feeling cuts, gratuitous post-production, clipped overlays, or technically valid but aesthetically weak timing.

## Direction reset after rejection

When a user says a later cut is worse than an earlier one, do not keep patching the rejected timeline. Compare the story beats, identify which additions are actually new, and remove additions whose editorial cost exceeds their proof value. If the user requests a clean redesign, start a new private cut with a new scene plan rather than layering more fixes onto the old composition.

A strong evidence-driven product film can use this restrained structure:

1. product promise on the real hero;
2. real synthetic input on production;
3. one dominant proof/traceability moment;
4. actionable result;
5. one exception or safety differentiator;
6. real export/output;
7. designed close.

Do not repeat the same fact in page copy, a large caption, a zoom, and a pointer. Pick the minimum treatment that makes the claim visible.

## Avoiding perceived white cuts

A pure-white-frame detector is necessary but insufficient. A cut from a dark interstitial directly into a mostly white application state, or between two unrelated bright page positions, can feel like a white flash even when no frame is uniformly white.

Preferred approaches:

- Keep one continuous browser recording whenever practical.
- Hide state changes and asynchronous parsing under a branded deep-color chapter bridge.
- Fade the bridge in and out over a short controlled interval; do not reveal loading or half-rendered states.
- Keep the bridge visually native to the product: same palette, type hierarchy, spacing, and voice.
- Avoid global camera zoom when captions, pointers, or proof overlays are baked into the source. It magnifies safe-area mistakes and can clip text.
- Use one deliberate callout for the strongest proof scene and, at most, one for the exception/safety scene.

## Transition audit

For every transition, sample five semantic frames:

1. immediately before;
2. entering;
3. midpoint/hold;
4. exiting;
5. immediately after.

Review the resulting grid row-by-row. Fail on:

- perceived or literal white flash;
- blank/loading/error states;
- a bridge title clipped at any fade stage;
- the wrong destination after the bridge;
- captions fading over unrelated content;
- a pointer left behind on the next scene.

Also inspect the first four and last four frames. The film must start on a complete branded state and end on a complete readable close.

## Playwright capture readiness and selectors

For a SPA capture, do not use `page.goto(..., { waitUntil: "networkidle" })` as the only readiness gate. Analytics, long polling, service workers, or persistent browser connections can make a healthy app time out. Prefer this bounded sequence:

1. request the application's health endpoint and require success;
2. navigate with `domcontentloaded` and a finite timeout;
3. wait for one stable, product-specific heading or landmark;
4. wait for the exact API response associated with each asynchronous action.

Use exact accessible names for navigation controls (`getByRole(..., { name, exact: true })`) when another button contains the same phrase. Playwright strict-mode ambiguity should fail before recording, not after minutes of capture. Always clear prior partial WebM files before retrying.

## Detecting duplicated static spans

A Playwright WebM may contain a much longer repeated static scene than the scripted hold time, even when container duration and decoded frame count agree. Before narration muxing:

1. build a coarse time-sampled contact sheet;
2. run scene-change detection and record timestamps;
3. identify repeated static spans by pixels, not by the script's intended waits;
4. trim only the duplicated span, preserving continuous surrounding product actions;
5. normalize the remaining video to constant FPS, then recount frames and inspect the exact first/last frames.

Do not globally speed a long capture until the contact sheet proves that every scene is uniformly stretched. A single repeated span should be cut locally; global speed-up makes real interactions unnaturally fast.

## Stream-accurate duration validation

Container duration may exceed the effective video stream because browser-recorded WebM can have variable timestamps or trailing container time. Full-file decode alone does not prove that video and audio end together.

Validate all of the following:

- effective decoded video-frame count;
- expected frames from constant output FPS and intended duration;
- video stream duration;
- audio stream duration;
- final frame content;
- no player-dependent implicit freeze at the end.

For variable-frame-rate browser captures:

1. normalize with an explicit `fps` filter;
2. trim the opening by `start_frame` after measuring the first valid frame;
3. add explicit cloned outro frames only if required;
4. set music duration and fade to the effective video duration, not the source container duration;
5. decode the final MP4 and recount decoded frames after every timing change.

If the filtered frame count proves the real stream is shorter than the container metadata, prefer a truthful shorter final duration over padding to a misleading metadata duration.

## Proof-scene validation

Inspect the proof hold at full output resolution. Require the same frame to show:

- exact original-page label;
- readable source document context;
- aligned evidence overlay;
- matching selected ledger/fact card;
- callout fully inside the safe area without covering the evidence.

Do not treat a downscaled contact sheet as sufficient evidence for small page labels or geometry alignment.
