# Motion Deck Direction Workflow

Use this pattern when a submission-safe deck is correct but visually stiff, or when the user asks for stronger typography, motion, effects, imagery, and human authorship.

## 1. Preserve the safe version

- Keep the QA-passed static deck untouched.
- Create a new version/directory for the motion direction.
- Label the new work `direction`, `prototype`, or `preview`; do not let it silently replace the submission candidate.

## 2. Prove mature-project adoption

A mature-project claim needs evidence:

- actual runtime/template package in the project, not just search notes;
- pinned package versions and lockfile;
- license files copied into `third_party/` or equivalent;
- exact features used (motion directives, transition engine, export system, typography package);
- narrow wording when only a texture or isolated asset was reused.

A practical open stack is:

- Slidev or reveal.js for animated HTML source;
- an open font package for Latin display text plus a deliberate CJK fallback;
- static PNG/PDF/PPTX export for external submission compatibility.

## 3. Three-page direction gate

Build only:

1. **Cinematic cover** — dominant image, compressed type, one signature motion gesture.
2. **Product evidence** — real screenshots in an asymmetric editorial collage, never a generic card grid.
3. **Proof/closing** — grounded metrics, real audit/test evidence, and an emotional closing scene.

This tests the full visual grammar before spending time on the remaining pages.

## 4. Motion posture

Prefer motion that clarifies hierarchy:

- staged title entry;
- opposing x/y entrances for contrast;
- spring landing for one key object;
- restrained page transitions;
- extremely slow background push for cinematic continuity;
- a deliberate resting frame that remains strong in static export.

Avoid decorative loops, constant zooming, or motion that delays reading. Respect `prefers-reduced-motion`.

## 5. Generated-image discipline

For more human presence without credibility drift:

- show lived-in traces: bags, coats, cups, breakfast remains, shoes, open blank notebooks;
- avoid readable papers, active screens, fake UI, close hands, or implausible devices;
- inspect at full resolution before adoption;
- label every ambiguous scene `Generated concept scene / 非产品截图`;
- keep real product screenshots as the only capability evidence.

## 6. Slidev implementation details

- Set an explicit slide layout when custom pages are fully absolute-positioned. Theme wrappers such as `.my-auto` can collapse to zero height if every child is absolute; use `layout: default` and give the wrapper `height: 100%`.
- Pin `@slidev/cli`, theme, font, and exporter dependencies.
- PNG/PDF export requires a Playwright package such as `playwright-chromium`; do not report export success until the output files exist and have been visually inspected.
- Check the animated runtime in-browser and inspect direct slide routes individually; then inspect exported static pages together as a contact sheet.
- Verify intended fonts with `document.fonts` or equivalent rather than assuming a CSS declaration loaded.

## 7. Native PowerPoint animation boundary

Before promising native PPT animation:

1. check for an actual PowerPoint or Keynote authoring/playback environment;
2. if available, author and playback-test the native timeline;
3. if unavailable, deliver the verified animated web source plus static PPTX/PDF;
4. never inject unverified OOXML animation markup or imply that an image-backed PPTX is natively animated.

## 8. Final QA

- Build animated source successfully.
- Export static resting frames successfully.
- Inspect cover, evidence, and proof pages at full size.
- Run an adversarial contact-sheet review for clipping, awkward line breaks, evidence legibility, AI tells, and repeated-card composition.
- Fix at least one issue and re-export.
- Stop local servers and remove temporary environments.
- Only after the user approves the direction should the remaining deck be rebuilt.
