# Open-source Chinese narration on Apple Silicon

Use this when a polished demo needs a zero-cost, commercially usable Chinese male voice and a hosted TTS free tier is personal/non-commercial.

## Rights-first selection

- Verify the checkpoint's **official model card and upstream LICENSE**, not a roundup.
- Prefer built-in preset speakers; do not clone a public/personality voice or use a human reference recording without consent.
- Record model ID, preset, package version, generation instruction, license URLs, sample rate/channels/bit depth, and rejected-review sources in the media ledger.
- Keep free-plan private-review audio outside the active composition, source archive, manifest, and submission artifact.

A proven option is `Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice` (`license: apache-2.0`) with built-in Chinese male preset `Uncle_Fu`. Its model card describes the preset as a seasoned male voice with mellow timbre. Use the current official card and LICENSE at execution time; do not treat this note as a frozen legal guarantee.

## Isolated macOS canary

```bash
uv venv --python 3.11 .venv
uv pip install --python .venv/bin/python qwen-tts soundfile
# qwen-tts 0.1.1 / transformers compatibility seen in July 2026:
uv pip install --python .venv/bin/python 'tokenizers==0.22.2'
```

Hermes can inject its own venv through `PYTHONPATH`, causing `importlib.metadata` to see the wrong package version even when `uv pip list` looks correct. Launch the isolated interpreter with:

```bash
export HF_HOME="$PWD/hf"
export PYTORCH_ENABLE_MPS_FALLBACK=1
env -u PYTHONPATH .venv/bin/python generate_canary.py
```

For Apple Silicon PyTorch inference:

```python
model = Qwen3TTSModel.from_pretrained(
    "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice",
    device_map="mps",
    dtype=torch.float32,
    attn_implementation="sdpa",
)
```

Generate the **same 15–25 second script** with two candidate preset voices before the full narration. Compare pronunciation of numerals/English product names, pacing, long-sentence stability, and unwanted broadcast cadence. A useful instruction is calm, restrained, trustworthy product explanation with slightly slow pacing and natural pauses.

## Segmented-speaker consistency

`CustomVoice` preset identity is not a sufficient consistency guarantee. In `qwen-tts 0.1.1`, `_merge_generate_kwargs()` falls back to stochastic defaults equivalent to `do_sample=True`, `top_k=50`, `top_p=1.0`, `temperature=0.9`, with the sub-talker also at `top_k=50`, `top_p=1.0`, `temperature=0.9`. Separate chapter calls can therefore sound like different people even when every call uses the same preset name. Inspect the installed version's defaults rather than assuming these values remain frozen.

For a zero-cost stable-identity repair:

1. Choose one rights-cleared anchor clip. A chapter generated from an Apache-2.0 stock preset can be the anchor; do not use an unconsented human recording.
2. Load `Qwen/Qwen3-TTS-12Hz-0.6B-Base` once and call `create_voice_clone_prompt(ref_audio=..., ref_text=..., x_vector_only_mode=False)` once.
3. Reuse that exact prompt for every chapter or pause-delimited part. Keep one checkpoint and one language.
4. Explicitly set both talkers' sampling controls. A useful canary starting point is `top_k=10`, `top_p=0.70`, `temperature=0.35` for both main and sub-talker, with a fixed seed reset per independently generated part. These are canary values, not universal quality constants; listen for repeated cadence or degraded diction before scaling up.
5. Build a short concatenated canary from opening, middle, and closing copy with different phonetic content. Do not spend an hour generating the full narration until this boundary canary passes.
6. Measure equal-duration speech windows with an independent speaker-verification model such as `microsoft/wavlm-base-plus-sv`. Compare pairwise cosine mean and minimum against the rejected baseline. In one observed repair, mean/min improved from `0.9489/0.9339` to `0.9704/0.9641`; treat the relative improvement—not those exact numbers—as the durable signal.
7. Human listening remains authoritative. Speaker embeddings can miss perceived age, emotion, pitch, or cadence changes. Deliver the actual canary and then the full regenerated video for explicit approval.

If a licensing correction changes the TTS provider, checkpoint, prompt, reference voice, or sampling parameters, invalidate the earlier video approval. Keep the platform artifact frozen until the regenerated full cut—not merely the audio files or metrics—has been heard and approved.

## Full narration pattern

1. If perceptual speaker identity must be seamless, prefer one continuous narration master and cut it into chapters afterward at deterministic pause markers. A shared preset name, reference embedding, seed, and low-temperature sampling can reduce drift but does not guarantee that independently generated chapters sound like one person.
2. If the model cannot generate the whole master safely, precompute one voice-clone/reference prompt and reuse it for every segment with one documented low-variance parameter set and seed policy. Build an opening/middle/closing canary first, listen across the boundaries, and compare independent speaker embeddings before full generation.
3. Treat codec-token exhaustion as failure: split risky passages at sentence boundaries, cap `max_new_tokens`, and reject implausibly long segments instead of accepting a valid container with repeated speech.
4. Replace markup such as `[pause]` with an actual 0.5–0.8 second zero-valued PCM segment; never let TTS speak the marker.
5. Write chapters to a temporary directory and validate all files before atomically replacing active audio.
6. Make the generator resumable: skip already validated chapter files after interruption.
7. Derive timeline durations from final WAV frame counts; re-run the platform runtime limit test.
8. Keep the previous active audio only until the new full render passes; then delete it after user approval.

A practical final format is 24 kHz mono PCM16 WAV. Before render, verify per chapter:

- expected file count and IDs;
- mono / 24 kHz / 16-bit;
- non-empty RMS and plausible duration;
- hard-clipping ratio below 0.01%;
- absolute DC offset below 0.01;
- total voice duration plus timeline overhead remains within the submission limit.

## Caption stability paired with narration

Do not fade the caption container on every sentence. Keep one fixed-height container mounted and opaque through the narration window; switch only the text at cue boundaries, then fade the whole container once at chapter entrance/exit. Regression-test opacity at `boundary-1`, `boundary`, and `boundary+1` and render those frames for visual comparison.

## Verification and handoff

- Run timeline tests, typecheck, real composition metadata, and full render.
- Independently decode/transcode the complete MP4 with a second media stack when the render-bundled FFmpeg is minimal.
- If embedding video in PPTX, verify the embedded media entry's SHA-256 equals the final MP4.
- Document the rejected hosted/free-plan audio and why it was excluded.
