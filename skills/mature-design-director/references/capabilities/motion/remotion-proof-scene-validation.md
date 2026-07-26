# Remotion proof-scene validation

Use this pattern when wrapping real browser footage in a programmable composition layer.

## Timeline contract

Keep timing constants in one importable module and test them:

- composition FPS and exact frame count;
- each source interval's start/end time;
- source-interval duration × FPS equals its allocated composition frames;
- all shot frame counts sum to the composition duration;
- push scale remains inside the approved range;
- ease-in/ease-out duration remains inside 8–12 frames;
- push-out completes before the next source shot begins.

For a two-shot proof, prefer explicit constants such as `FIRST_SOURCE_START_SECONDS`, `FIRST_SHOT_FRAMES`, `SECOND_SOURCE_START_SECONDS`, and `SECOND_SHOT_FRAMES` over one broad interval that crosses an interstitial.

## Camera curve

Use four interpolation points:

```ts
const scale = interpolate(
  frame,
  [pushStart, pushStart + easeFrames, pushEnd - easeFrames, pushEnd],
  [1, pushScale, pushScale, 1],
  {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
);
```

The hold must cover the semantic evidence moment. Returning to `1` before the next scene prevents an action board or outro from inheriting an evidence close-up.

## Visual sampling

Generate both:

1. regular samples across the whole candidate; and
2. semantic samples at `cut-1`, `cut`, `cut+1`, `pushStart-1`, maximum-scale hold, `pushEnd-1`, and `pushEnd`.

Review at full resolution where text legibility matters. A five-up strip is useful for narrative flow but can hide small caption collisions.

## Technical verification

After the final render, verify from the artifact itself:

- exact duration and decoded frame count;
- expected H.264 dimensions/FPS and AAC stream;
- full audio/video decode to a null sink with error-level logging;
- source hash unchanged;
- contact-sheet dimensions and sampled frame list;
- no stale report from a previous render.

A passing decode does **not** prove a clean opening. Uniform sampling can skip short blank runs, especially when frame 0 is white rather than black. Always extract exact opening frames such as `0, 3, 15, 30` and inspect them together. For deterministic detection, run FFmpeg `signalstats` over the first 1–2 seconds and find the first frame whose luminance differs materially from blank white. If the first valid frame is `N`, trim exactly `N / fps` seconds from the completed composition so camera motion and content stay synchronized, then pad the designed outro by the same duration and re-run full verification.

When Remotion uses `Config.setBrowserExecutable()` to point at a wrapper script, `remotion browser ensure` may report the wrapper itself as the installed browser and skip downloading Headless Shell. The durable setup pattern is: provision a real matching Remotion Headless Shell first (or copy the already-verified same-version `.remotion` cache), then verify the wrapper directly with `wrapper.sh --version` before rendering. Capture the setup fix, not a blanket claim that Remotion browser installation is broken.

Store the verification report beside the candidate, but do not treat it as aesthetic approval.

## Approval gate

Copy the candidate into a chat-deliverable attachment location and confirm the user can actually see it. Do not infer approval from silence, an empty response, a failed attachment render, or a passing verification report. Important one-shot submissions remain private until explicit approval.
