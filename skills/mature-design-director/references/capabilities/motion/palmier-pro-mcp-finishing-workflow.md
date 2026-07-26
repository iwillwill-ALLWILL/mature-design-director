# Palmier Pro MCP finishing workflow (versioned canary)

## Status and scope

Last validated on 2026-07-18 with the following bounded fixture. Treat every version, platform requirement, endpoint, export behavior, and ranking below as dated canary evidence; revalidate against official sources and a disposable proof scene before adoption.

- Palmier Pro `v0.6.11`, Apple Silicon DMG, GitHub release digest verified before install
- macOS `26.5.2`, arm64
- local MCP endpoint `http://127.0.0.1:19789/mcp`
- mcporter `0.12.3`
- sanitized product-film fixture: 1600×900, 30fps, 360-frame H.264/AAC render

Palmier is a professional NLE/finishing layer after deterministic Remotion scene rendering. It does not replace the truthful product capture or Remotion's reproducible typography/evidence compositions.

## Why this is useful

The local MCP server exposed and successfully executed real timeline operations, including:

- `manage_project`, `create_timeline`, `set_active_timeline`
- `import_media`, `get_media`, `inspect_media`
- `add_clips`, `split_clips`, `move_clips`, `remove_clips`
- `get_timeline`, `inspect_timeline`
- `set_clip_properties`, `set_keyframes`, `apply_layout`
- `detect_beats`, text/caption tools, audio cleanup
- `apply_color`, `.cube` LUT support, `apply_effect`
- `export_project` to H.264/H.265/ProRes/XML/FCPXML/self-contained `.palmier`

The dated canary proved local import, non-destructive timeline duplication, exact-frame splitting, per-shot grading, effects, motion keyframes, timeline inspection, H.264 export, and self-contained project export with `missingMedia: []`.

## Setup

1. Verify machine compatibility before installing: Apple Silicon and macOS 26+.
2. Fetch the latest official GitHub release from `palmier-io/palmier-pro`.
3. Verify the downloaded DMG against the release asset SHA-256 digest.
4. Mount, verify `codesign --verify --deep --strict` and `spctl -a -t exec -vv`, then copy `Palmier Pro.app` to `/Applications`.
5. Launch Palmier. Its local MCP server listens on `127.0.0.1:19789/mcp` by default.
6. If `mcporter` is absent, install it with npm. On this setup its binary was under the active Node prefix, not initially on PATH; use `$(npm prefix -g)/bin/mcporter` or repair PATH deliberately.
7. For the loopback HTTP endpoint, pass `--allow-http`; never use that exception for a remote server.

Example:

```bash
M="$(npm prefix -g)/bin/mcporter"
U='http://127.0.0.1:19789/mcp'
"$M" call "$U.manage_project" --allow-http --output json \
  --args '{"action":"create","name":"Film Finish Canary","fps":30,"aspectRatio":"16:9","quality":"1080p"}'
```

## Recommended production architecture

1. Keep Playwright capture as the truth source.
2. Keep Remotion as the deterministic design/evidence renderer.
3. Export scene-level handles, not one flattened final movie. Include enough head/tail handles for editorial overlaps.
4. Import those scene renders, licensed music, and SFX into a Palmier project.
5. Duplicate the timeline before each meaningful treatment using `create_timeline(from=...)`.
6. Use Palmier for:
   - scene assembly and pacing;
   - per-shot color continuity;
   - slow push/reframe keyframes;
   - restrained grain/vignette/glow;
   - music/beat alignment and sound finishing;
   - final H.264/ProRes and FCPXML exports.
7. Re-read `get_timeline` after duplicate/split operations because clip IDs change.
8. Use `inspect_timeline` and exported frames/video to verify edits. Do not trust mutation echoes alone.
9. Export a self-contained `.palmier` package and require `missingMedia: []`.
10. Fully decode the final video with FFmpeg and verify frame count, resolution, fps, duration, audio, and transition frames.

## Restrained treatment tested by the dated canary

The canary used these values only on cinematic intro/outro segments. They are evidence that the controls worked in that build, not reusable art-direction defaults:

- warm temperature near 6900–7100K;
- very low teal/green shadow push;
- warm highlight push;
- restrained S-curve / lifted toe;
- film grain amount `0.08`, size `1.35`;
- vignette amount `0.09`, feather `0.82`;
- centered slow push from 1.000 to 1.025, paired with position from 0 to −0.0125 on each axis.

A/B review showed a real but subtle cinematic lift without clipping typography or truth labels. This is finishing, not an automatic redesign. Avoid applying the cinematic grade to product UI evidence; preserve its literal color/state fidelity.

## Verified audio-finishing caveat and robust workaround

In the dated full-film canary, Palmier `v0.6.11` accepted and displayed a music clip's `volume` keyframes, but the H.264 export did not attenuate the bed as expected: the first export measured `−7.9 LUFS` integrated and `+0.7 dBFS` true peak instead of the intended roughly `−18 LUFS`. Do not trust a successful `set_keyframes(property='volume')` echo or timeline read as proof that the exported mix honors the curve.

Robust workflow:

1. Render/import the visual master without audio.
2. Keep semantic SFX on a separate Palmier audio track with static clip volumes.
3. Pre-build the music bed as a deterministic audio asset with its source trim, exact duration, fades, and loudness baked in. Example:

```bash
ffmpeg -ss 11 -t 58 -i music.mp3 \
  -af "afade=t=in:st=0:d=2,afade=t=out:st=55.333:d=2.667,loudnorm=I=-19:TP=-3:LRA=7" \
  -ar 48000 -ac 2 -c:a pcm_s24le music-bed.wav
```

4. Import that asset at unity volume on its own track.
5. Export a private mix and measure the actual file with FFmpeg `ebur128=peak=true`.
6. Check short windows around every semantic event with `astats`; a present audio track is not proof that the intended transient survived or aligned.

The corrected dated export measured `−18.4 LUFS`, `1.6 LU` LRA and `−3.8 dBFS` true peak; all six SFX windows contained the intended transient. These are fixture results, not universal mastering targets.

Also note that Palmier project export collects unused media still present in the library. Removing a clip from the timeline does not remove its media asset. Before the final self-contained package, delete unused asset IDs with `organize_media(deletes=[...])`, re-export, and verify `missingMedia: []` plus the expected `collectedMediaRefs` list.

## Generation boundary

`get_timeline` reports `canGenerate`. In the verified no-login/no-subscription canary it was `false`; generation/upscale tools were not called. These tools can cost real money and are not undoable. Never call them without explicit payment authorization, and never use generated video to replace product evidence.

## Project/file hygiene

Palmier created projects under its default Documents location in the dated canary. Keep the authoritative archive under the active project's governed output directory instead:

1. Export a self-contained `.palmier` package into the actual project-controlled archive.
2. Confirm the package contains `project.json`, media metadata, and copied media, with no missing media.
3. Close the MCP project and quit Palmier before deleting the default Documents copy; deleting while Palmier is open can hang on file coordination.
4. Remove downloaded DMGs and temporary MCP schema dumps after the canary.

## Art-direction gate before finishing

Do not treat a successful Palmier grade/export as proof that the edit is artistically strong. The dated canary passed every technical gate but an independent frame/timeline audit found that persistent navigation, disclosure pills, a large bottom guidance layer, a full-screen UI grade, UI grain, and uniform crossfades competed with the product evidence.

The verified correction was to re-edit before finishing:

- recapture missing before/action/after truth states instead of explaining them in post;
- let photographs carry mood and keep product UI in original colors;
- remove UI grain and global cinematic tint;
- use semantic hard cuts or match cuts when they communicate the action better than a template transition;
- keep at most one short note and place it outside the evidence region;
- let real product states prove claims such as one rollback while two actions remain successful;
- use a camera pan or crop to reveal real UI evidence instead of placing a post-production number over it.

Only after the evidence-first edit passes representative-frame and exact decoded cut-boundary review should Palmier grade photographic shots, add restrained optical motion, perform sound finishing, and export. In the dated fixture, 285 UI frames were intentionally left ungraded; source-vs-export SSIM over that interval was `0.997616`, confirming that build did not materially alter the UI evidence. Recompute this gate for every adopted pipeline.

## Selection decision

This canary justifies keeping Palmier Pro as a candidate when a native NLE, exact-frame MCP control, grading/effects, composited inspection, and ProRes/FCPXML export fit the task. It does not establish a permanent winner over OpenCut, Buttercut, OpenReel, FireRed-OpenStoryline, or later candidates. Re-run the ecosystem, license, maintenance, compatibility, and proof-scene comparison at task time. An AI director/storyline consultant may propose constrained decisions, but must not render or rewrite truthful product evidence by default.
