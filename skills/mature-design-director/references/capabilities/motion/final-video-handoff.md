# Final video handoff and publication gates

Use this after the user approves a private product-demo cut.

## Freeze the local master

1. Copy the approved MP4 into one clearly named final-media directory.
2. Remove rejected cuts from that directory; keep comparisons elsewhere only when useful.
3. Record:
   - local filename and byte size;
   - SHA-256 of the local source file;
   - composition duration and actual container duration separately;
   - resolution, output FPS, decoded frame count, codecs and audio peak;
   - white/black-frame scans, full-decode result and visual-audit artifacts;
   - approval status and publication status as separate fields.
4. Never call a candidate public merely because it was user-approved locally.

## Platform transcoding rule

Social platforms commonly transcode uploads. Therefore:

- verify the local SHA immediately before upload;
- do not expect the public/transcoded asset to preserve that hash;
- after publication, verify the public URL, full playback, audio, first/final frames and alt text;
- retain the public URL alongside the **local-source** checksum metadata.

Public documentation should distinguish composition duration (timeline intent) from MP4 container duration when they differ.

## Separate approval gates

Approval of the video does not automatically approve:

- participation-post copy;
- alt text after platform rendering;
- marketplace changes;
- the final submission form.

Track these as independent gates. Unknown account handles or form fields must remain explicitly unknown rather than guessed.

## Repository wording

When the video is intentionally outside the repository:

- state that the local final is approved but unpublished;
- avoid claiming detailed visual audits in public docs unless their artifacts are also published;
- keep detailed render/contact-sheet evidence in the private handoff;
- run an independent fail-closed documentation review for stale durations, old version names, misleading publication status and local-vs-public checksum ambiguity.

## Reproducible-project archive

Promote the successful composition project out of temporary storage, but exclude:

- `node_modules`;
- browser binaries and caches;
- render caches and duplicate output files.

Keep source assets, timeline/component code, lockfile, tests, capture script and a README with exact rebuild commands. Re-run tests and type checking from a clean dependency install, then remove installed dependencies from the archive.
