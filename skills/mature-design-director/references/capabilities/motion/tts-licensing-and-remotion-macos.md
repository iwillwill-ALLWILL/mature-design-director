# Human-like TTS licensing and Remotion macOS fallback

Use this reference when a product-demo cut needs natural narration and a deterministic Remotion render.

## Voice A/B protocol

1. Write one 60–100-character test passage containing:
   - a short hook;
   - one pause or clause boundary;
   - a product name;
   - numerals or an English term if the final script contains them;
   - one long sentence to expose breath and cadence problems.
2. Generate the exact same passage with at least two mature voices. For stochastic models, retain a primary and alternate generation per voice.
3. Verify every file with a media probe and label it by provider, model, voice, variant, and duration. Never call a browser click “generated” until the resulting media URL/file exists and opens.
4. Compare naturalness, pace, emphasis, pronunciation, long-form stability, and fit with the product personality. Do not let a louder or faster sample win by accident.
5. Split the approved long script into scene-level files. Derive scene duration from the actual audio files rather than estimating timing from character count.

## Rights decision tree

- **Provider-owned/default stock voice:** confirm that the selected paid/student tier grants commercial use, then preserve the entitlement page and receipt.
- **User-owned/verified clone:** verify consent and ownership before generation; preserve that evidence.
- **Community-uploaded or celebrity-like voice:** do not infer commercial rights from the platform plan alone. Verify the voice-specific grant or replace it.
- **Free personal/non-commercial tier:** private review only. Put the review cut in a directory explicitly excluded from public/submission packaging and regenerate under commercial rights after approval.

For every candidate, record: provider, model, voice ID/title and type, account tier, generation date, source/terms URL, and whether publication is allowed. Recheck current terms at final export because provider plans change.

A safe layout is:

```text
review/
  README.md                 # PRIVATE REVIEW / NOT FOR SUBMISSION
  voice-samples/
  review-cut.mp4
production/
  narration-source.json
  commercial-audio/         # populated only after rights gate
submission/
  final-video.mp4            # never points at review audio
```

## Remotion verification ladder

Run the cheapest gates before a full 3–5-minute render:

```bash
npm test
npm run typecheck
npx remotion compositions src/index.ts
npx remotion still src/index.ts Composition out/poster.png --frame=120
npx remotion render src/index.ts Composition out/smoke.mp4 --frames=0-179
```

Render chapter-midpoint stills and a contact sheet before the full movie. Also sample immediately before/during/after transitions; uniform intervals alone miss short bad cuts.

If Remotion's downloaded headless browser cannot launch on a managed macOS host, use an already installed trusted Chrome executable instead of weakening host security:

```bash
CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
npx remotion still src/index.ts Composition out/poster.png \
  --frame=120 --browser-executable="$CHROME"
npx remotion render src/index.ts Composition out/final.mp4 \
  --codec=h264 --audio-codec=aac --crf=18 \
  --browser-executable="$CHROME"
```

Expose generic and `:mac` package scripts when the project must remain portable. Treat this as a fallback, not a permanent claim that bundled browsers are unusable.

## Nested test-runner boundary

A Remotion subproject may use `node:test` while the product root uses Vitest. Prevent root Vitest from treating the nested Node test file as an empty Vitest suite:

```ts
import {configDefaults, defineConfig} from 'vitest/config';

export default defineConfig({
  test: {
    exclude: [...configDefaults.exclude, 'video-v2/**'],
  },
});
```

Keep the video subproject's own `npm test` as a separate required gate; exclusion is test-runner ownership, not skipping validation.
