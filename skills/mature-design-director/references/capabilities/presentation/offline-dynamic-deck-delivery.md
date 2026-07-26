# Offline dynamic competition deck delivery

Use when a competition/pitch deck is expected to contain visible motion outside the authoring browser.

## Correct artifact hierarchy

1. **Offline dynamic PPTX** — primary deck when the user asked for motion. It must contain real playable motion.
2. **MP4 demo fallback** — guarantees motion survives viewers that suppress PPT animation/GIF playback.
3. **Static PDF/PPTX** — compatibility and layout fallback only; never present it as the dynamic main artifact.
4. **Slidev/reveal.js source** — editable motion source and review runtime, but localhost alone is not an offline submission deliverable.

A different viewer cannot reveal animation that is absent from the file. Before installing or recommending a viewer, inspect whether the PPTX itself contains animation/media/transitions.

## Official-requirement gate

Inspect the official submission page before finalizing the slide outline. Capture:

- accepted primary formats;
- file-size cap;
- whether supplementary video/Demo/ZIP is allowed;
- naming rules;
- every required content section;
- deadline and timezone.

Do not assume a visually complete product story satisfies a business-plan requirement. Common missing sections include business model, team introduction, originality statement, and sensitive-information treatment.

## GIF-backed PPTX workflow

This preserves browser-grade kinetic typography without rebuilding every element as native PowerPoint shapes.

1. Build and approve the motion source in Slidev or another browser runtime.
2. Warm fonts and images in Playwright.
3. Capture every slide at a fixed viewport/cadence.
4. Inspect early frames. Vue/browser mounts often yield one or two black/loading frames; drop them.
5. Add several copies of the final frame for a readable resting state.
6. Encode a **one-shot** GIF with palette generation. Example:

```bash
ffmpeg -framerate 13.333 -start_number 2 \
  -i frame-%03d.png \
  -vf "split[s0][s1];[s0]palettegen=max_colors=128:stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle" \
  -loop -1 slide.gif
```

7. Insert each GIF full-slide with `python-pptx`.
8. For broadly compatible page transitions, unpack the PPTX and insert `p:transition` after `p:cSld` / optional `p:clrMapOvr` in each slide XML. Prefer `fade`, `push`, and `wipe`.
9. Repack and verify the OOXML ZIP.

## Motion verification

- Decode and inspect first/middle/final GIF frames.
- Assert every GIF has more than one frame.
- Assert the PPTX embeds the expected number of `.gif` media files.
- Assert every slide XML has the expected transition.
- Open the result in an actual target viewer and wait for import/conversion to finish.
- Keep the animated PPTX under the platform limit.
- Generate an H.264 MP4 from the same motion assets.
- Sample the MP4 at the **actual midpoint of each encoded segment**. Nominal 5-second segments may become 4.96 seconds after concatenation; fixed 5-second sampling can drift into fades and falsely report dark slides.
- Static PDF reverse rendering proves layout only, not motion.

## Submission bundle

If multiple files are allowed, package:

```text
01-...-动态方案书.pptx
02-...-演示视频.mp4
03-...-静态方案书.pdf
README-播放说明.txt
```

Use deterministic UTF-8 ZIP packaging, strip macOS metadata, verify size and members, and keep the platform submission state separate from local completion.

## Failure patterns to prevent

- Calling a full-slide PNG PPTX “dynamic.”
- Giving the user only localhost when they asked for the submitted artifact.
- Installing a PPT viewer before checking whether the deck contains animation.
- Defending a static fallback after the user asked for motion.
- Building a dynamic deck that omits official business-plan sections.
- Treating a GIF file count as enough; verify multi-frame content and decoded visual states.
