# Media Provenance and Repository-Isolation Pattern

## Recover exact music provenance

An inherited filename/provider label is not enough, but an absent per-track landing page does not always mean the source is unrecoverable.

1. Search the provider's current genre/category pages and inspect embedded JSON-LD or structured page data.
2. Recover exact title, creator, duration, direct-media URL and copyright/license field.
3. Download the official media again.
4. Compare the fresh download and local asset with SHA-256 and a byte comparison.
5. If byte-identical, record the category page, direct URL, creator, license URL, retrieval date and hash.
6. Keep raw stock music/SFX out of public source archives when redistribution is not explicitly permitted; distribute only the combined rendered film and the provenance note.
7. If identity cannot be proven, keep the old render private and replace or fully source the track before public use.

Provider search pages may expose only the first few structured records; scan adjacent genre/mood categories when the title is known but the first category is wrong. Do not infer rights from the title alone.

## Migrate a media project into a larger repository

Before migration, search adjacent project-owned scripts/archive/review directories so a source workspace is not falsely declared lost. Copy only durable material: timeline source, capture script, source media, tests, lockfile, NLE project, exact third-party notices and rebuild instructions. Exclude dependencies, browser binaries, caches, old QA and duplicate renders.

After migration:

- run clean install, focused tests, typecheck and a full render from the new path;
- decode the full output and compare semantic marker intervals/SSIM against the earlier candidate;
- verify the host application still passes its own lint/build;
- make the host `tsconfig`/ESLint ignore the standalone media project, or create a real workspace/project-reference boundary;
- keep the media project responsible for its own tests/typecheck/render gates;
- do not weaken host or media type safety just to silence cross-project glob pollution.

A different encoded hash after a clean render is expected across browser/encoder versions; verify visual/semantic equivalence, then freeze the accepted review binary by its own exact hash.
