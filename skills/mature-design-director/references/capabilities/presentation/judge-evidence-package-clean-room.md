# Judge-Evidence Package Clean-Room Gates

Use this when a competition permits supplementary demo/code/evidence files and a deck-only minimum leaves rubric points unproved.

## 1. Ordinary-scale evidence legibility

Do not accept “high-resolution screenshot” as proof of readability. Validate the **composed page at final export scale**.

1. Render the actual page/PDF/PPT candidate.
2. OCR the final rendered risk pages, not only source screenshots.
3. Assert that judge-critical phrases are recognized: source fact, consent state, execution state, rollback state, audit change, safety boundary.
4. When text fails, create a lossless tight crop from the real artifact, record crop coordinates/source, and replace the tiny full-page screenshot.
5. Re-export and re-run OCR. Never recreate product text as editorial overlay and call it product evidence.
6. Check content boundaries/positions so larger text did not overflow.

OCR is a regression signal, not a substitute for human visual review. Use final-page OCR to compare before/after and to freeze must-remain-readable phrases.

## 2. Review output must not overwrite approved/final material

Packaging/build/verification scripts should accept explicit page/input/output overrides, for example environment variables or CLI arguments. Defaults may target the normal final path, but win-max iterations must write under `review/` until the exact-artifact approval gate passes.

Verify a review binary as strictly as a final binary without enforcing “final directory contains exactly one file.” This prevents a verifier from forcing an unauthorized final overwrite merely to run QA.

## 3. Supplemental code evidence: minimum honest snapshot

Prefer a small reproducible vertical slice over a whole historical repository dump.

Include:

- exact feature source and focused tests;
- minimum app/build shell and pinned lockfile;
- AI-oriented README with one run prompt;
- architecture, validation and source/packaging map;
- explicit truth boundary (simulated vs real, planned vs implemented);
- per-file SHA-256 manifest.

Exclude:

- `.git`, `.env*`, credentials, `node_modules`, caches, browser binaries;
- old competition copy and unrelated product surfaces;
- deck/video projects, review/final submissions, receipts;
- raw licensed music/SFX unless redistribution is explicitly allowed.

If the snapshot adapts host-shell metadata or routing for reviewer convenience, document every packaging-only change. Never hide that a vertical slice was built on an existing codebase.

## 4. Clean-room verification

Copy the snapshot to a fresh temporary directory and run the commands promised in its README:

```text
fresh install / lockfile install
focused tests
lint
production build
production dependency audit
secret scan
real server start + content canary
```

Do not reuse the source repository's `node_modules` or build cache. Start the built server, request the real route, and assert product identity plus truth-boundary copy in the returned page.

A custom minimal `package.json` can accidentally drop security overrides from the tested source repository. Run a production dependency audit after generating the new lockfile. Preserve only evidence-backed overrides; do not follow a broken automated “fix” that downgrades a framework to an unrelated major version.

After every documentation/report update, regenerate the file manifest and rerun the snapshot contract.

## 5. Monorepo/toolchain boundary

When media/deck projects are migrated into an application repository, the root TypeScript/ESLint glob may start scanning their independent sources and break the app build. Treat each toolchain as an explicit boundary:

- root app config excludes standalone media/submission workspaces, or the repo is converted to a real workspace with project references;
- each excluded project retains its own tests/typecheck/render/build gates;
- run both the root app gate and each artifact-project gate after migration.

Do not “fix” cross-project warnings by weakening type safety inside the wrong project.
