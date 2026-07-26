# Motion, Product Film, and Demo Capability

Use this capability for product walkthroughs, launch films, hackathon/competition demos, marketplace videos, pitches, and social cuts. It owns story, capture direction, timeline selection, viewer guidance, audio/caption discipline, technical media QA, privacy, and handoff.

A product film is not a screen recording with captions. It is a directed causal story using real product behavior.

## Story and scene contract

Recover prior approved cuts, capture scripts, timelines, source media, license records, and review notes before starting. Fork a reproducible approved foundation when it remains valid.

Write one sentence describing what the viewer should remember, then a timed scene plan. Each scene must have one job: pain, real input, proof, transformation, exception/safety, output, or close.

For a 45–75 second proof cut, a useful starting rhythm is:

- 0–5s: pain and promise;
- 5–15s: real input on the live product;
- 15–28s: strongest proof/traceability;
- 28–40s: transformation into action/result;
- 40–52s: exception, uncertainty, safety, or differentiation;
- 52–62s: export/integration/real-world output;
- final 5–8s: product identity and exact CTA.

Do not force every feature into the cut. Allocate the most time to the strongest proof and the scene most likely to build trust.

## Pipeline ownership

Separate the stack into:

- source/capture;
- capture intent/telemetry;
- timeline/composition;
- captions;
- motion graphics;
- audio;
- final encoding and validation.

Use `references/mature-ecosystem-registry.md` to choose one timeline owner. Playwright and FFmpeg are mature primitives, but a capture script plus filters is not automatically a mature editor.

Preserve deterministic real-browser capture when it exists. Emit scene markers, click points, target bounds, caption keys, and readiness signals as timeline data. Use a real composition layer when independent retiming, reusable overlays, keyframes, animation-state inspection, or deterministic rerendering matters.

An AI Director may operate only as a constrained sidecar: it can propose structured cut, hold, zoom, caption, and emphasis decisions inside an approved story, duration, framing, and truth contract. The compositor/timeline owner remains responsible for pixels and deterministic rendering. Keep Director and Reviewer roles separate—the Reviewer may reject continuity, evidence, pacing, privacy, or taste failures but must not silently rewrite the approved direction. A model response, Playwright trace, Remotion component, FFmpeg filter, or NLE command is production data, not proof of art direction.

Validate one 8–12 second proof scene before migrating the whole cut. Reject recorder-only tools when post-production is required, speech-analysis tools when there is no narration, and attractive but archived/custom-license projects without explicit review.

Programmatic and native timelines must not both own the final cut. A native NLE is an adapter choice, not a separate creative authority; prove its current import, edit, render, and reopen path with a disposable scene before adoption.

## Real-product capture

Use a production build and representative real input whenever possible. Built-in samples may support the story but cannot be the only proof.

If real input exposes parsing, title, layout, evidence, timing, or state defects:

1. stop editing;
2. reproduce with a failing test;
3. fix the product;
4. run its suite and production canary;
5. recapture the real product.

Do not hide product defects with crops, overlays, local mocks, or fabricated footage.

Direct capture deliberately:

- standardize viewport and clean account state;
- wait for asynchronous states to settle;
- use element bounds rather than only cursor coordinates;
- make pointer/click feedback visible when needed;
- capture evidence close enough to read;
- avoid long automated scrolls;
- record transitions and source intervals precisely.

## Composition and viewer guidance

Use chapter copy, progress, arrows, boxes, zoom, and retiming only when they answer “where should I look?” or “why does this matter?”. A good hierarchy is progress rail → chapter card → at most one scene-specific guide.

When a clean cut is too fast:

- do not globally slow the MP4;
- re-record clean source when prior captions/chapter cards are baked in;
- retime per scene;
- keep UI motion within natural playback bounds;
- use full view → short push → stable hold → short pull-out for proof scenes;
- render key stills and boundary phases before the full film.

Avoid competing caption systems and overlays covering the evidence they explain. Keep timing constants and source intervals in one importable contract, render boundary frames, and test source-duration × FPS against allocated frames before a full render.

A detector finding no pure-white frame does not prove there is no perceived white cut. Sample immediately before/during/after every cut, bridge, zoom entrance/hold/exit, and inspect semantic continuity.

When a later version becomes repetitive or over-directed, stop stacking patches. Compare accepted and rejected story beats, keep only the genuinely new proof, and rebuild privately from a fresh scene plan.

## Captions and muted-first design

Assume autoplay is muted. Captions must carry the story.

- concise kicker + headline + optional detail;
- maintain one fixed-height caption container during a narration window;
- fade the container once at entry/exit, not once per sentence;
- switch text at integer-frame cue boundaries;
- reserve two-line height to prevent layout jumps;
- test `boundary-1`, `boundary`, and `boundary+1` frames after final audio timing.

## Voice, music, and rights

Do not default to generic TTS. For important narration, compare the same short script across at least two credible voices. Judge naturalness, pacing, emphasis, numerals/English terms, long-passage stability, and rights.

Segmented narration needs a separate speaker-identity gate. Same preset name does not guarantee the same perceived person. Prefer one continuous narration master cut into chapters for a zero-drift target. Otherwise lock checkpoint/reference/seed/sampling policy and run opening/middle/closing canaries with human listening plus speaker-verification non-regression.

Reject codec-token exhaustion, implausible duration, repetition-to-cap, clipping, and identity drift. Shared subtle mastering may normalize loudness and smooth spectral differences only when it improves cross-boundary listening without degrading worst-pair identity metrics.

Any regenerated voice invalidates prior audiovisual approval.

Record provider/model/voice type, entitlement source, account tier, generation date, and consent. Free/non-commercial output stays private. Do not clone a real person without verified consent.

For music, retain official source URL, title, creator, direct-media URL when available, license, retrieval date, and hash. An inherited filename is not provenance. Raw stock media stays out of public code archives unless redistribution is permitted.

Select narration through a rights-first A/B canary on the actual target language and difficult terms. Keep model/checkpoint, preset/reference, seed/sampling policy, entitlement, source URLs, and hashes in the project record. Platform-specific install commands and version canaries belong to the chosen audio adapter, not this capability.

## Pixel privacy

Before finalizing footage, frames, contact sheets, or receipts, inspect browser/account chrome, modal backgrounds, upload dialogs, notifications, QR codes, and first/final frames for personal data, account IDs, email, legal name, school, OTPs, tokens, or unintended login state.

Use synthetic/clean accounts or crop before capture. If redaction is required, preserve the evidentiary message, record scope, recompute hashes, reopen the actual file, regenerate derivatives, and invalidate prior visual approval. Do not retain unredacted originals in review/submission archives or Git history.

## Final media gates

Before calling a cut final:

- platform duration and aspect requirements pass;
- intended resolution, CFR, codec/container, and audio codec pass;
- decoded frame count agrees with effective duration/FPS;
- audio and video end together;
- full-file decode has no errors;
- no literal or perceived flash/error frames;
- captions and evidence are readable at playback scale;
- real input, strongest proof, exception/safety, output, and designed close are visible;
- no private data or test credentials appear;
- contact sheet plus semantic boundary frames were inspected;
- the actual playable candidate was visibly delivered and reviewed.

Keep candidates private. A technically valid cut is not approved. Freeze one local master after approval, record hash, archive reproducible source without dependencies/caches/duplicate renders, and keep publication as a separate gate. After platform transcoding, verify playback, first/final frames, audio, captions/description support, and final URL/state.

## Learning

Store generalized capture, timeline, voice, privacy, and QA lessons here. Exact project paths, private footage, rejected cuts, customer data, and unlicensed media remain project-local.