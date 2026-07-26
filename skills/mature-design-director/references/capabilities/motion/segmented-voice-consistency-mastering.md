# Segmented voice consistency: diagnosis and final mastering

Use this when a segmented narration already sounds broadly like one speaker but chapter boundaries still reveal subtle timbre differences.

## Diagnose before processing

Measure the same speech-window length for every chapter where possible.

1. **Speaker identity:** embeddings from an independent verification model; retain every pair, mean, minimum, and minimum-pair label.
2. **Pitch/prosody:** voiced-frame median F0 and spread. A chapter can be intentionally higher without being a different person.
3. **Level:** RMS or LUFS, peak, clipping, and DC offset.
4. **Tone color:** smoothed long-term spectral envelope over voiced frames.
5. **Human boundary test:** concatenate opening/middle/closing passages with normal pauses and listen across joins.

Do not use one metric to explain every perceptual difference.

## Canary matrix

Test every proposed post-process on opening/middle/closing chapters before touching all files:

| Candidate | Identity risk | Required comparison |
|---|---:|---|
| Voice conversion to one target | high | before/after speaker mean + minimum, artifacts |
| PSOLA/formant-preserving pitch shift | medium | speaker mean + minimum, naturalness |
| Shared spectral mastering | low when subtle | spectral spread, speaker budget, clipping |
| Loudness normalization only | low | LUFS/RMS, peak, pumping |

Reject a sophisticated transform when it makes the independent speaker gate worse. “Same target voice” and “formant-preserving” are implementation claims, not acceptance evidence.

## Conservative spectral-mastering pattern

A practical last-mile correction for brightness/darkness differences:

1. Load all chapters at their delivery sample rate.
2. Compute an STFT magnitude envelope for each chapter; use only frames above a voiced/energy threshold.
3. Convert to relative dB, take the median over selected frames, and smooth across frequency.
4. Use the cross-chapter median envelope as the shared target.
5. Compute `target - chapter`, smooth again, and clamp the EQ curve to roughly 1–2 dB unless listening supports more.
6. Convert the curve into a linear-phase FIR response; reflect-pad before convolution to avoid edge transients.
7. Preserve the exact source sample count, then apply a common loudness target and a conservative peak ceiling.
8. Recompute spectral spread, speaker embeddings, duration/sample count, clipping, and full-file decode.

This corrects chapter tone without changing wording, speed, pitch, or formants. Keep the mastering deterministic and save the curve/range metadata.

## Acceptance rule

Accept only when all hold:

- between-chapter spectral spread falls materially;
- no hard clipping, silence, truncation, or sample-count drift;
- mean speaker similarity and worst-pair similarity remain inside a declared non-regression budget;
- opening/middle/closing boundary listening improves;
- the complete remastered video is rendered and decoded again;
- the user’s approval applies to this exact audio/video artifact, not an earlier narration.

Always report mean **and** minimum deltas. A higher mean does not erase a lower worst pair; small trade-offs require explicit listening judgment rather than metric cherry-picking.

## Evidence from the July 2026 competition demo

A nine-chapter Qwen voice-clone narration reused one prompt and low-variance generation but retained subtle chapter differences. Three canaries were compared:

- OpenVoice tone conversion reduced speaker similarity and was rejected.
- Praat PSOLA pitch normalization also reduced speaker similarity and was rejected.
- Shared ±1.5 dB median-spectrum mastering reduced cross-chapter spectral spread by about 22.4%; mean speaker similarity improved slightly while the worst pair moved slightly downward but stayed inside the predeclared budget. Exact sample counts and 0% clipping were preserved.

The important reusable result is not the exact 1.5 dB value. It is the sequence: diagnose → canary competing transforms → reject regressions → apply the least invasive shared mastering → disclose both aggregate and worst-pair metrics → render/decode the actual final artifact.
