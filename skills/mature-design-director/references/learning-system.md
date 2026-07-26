# Compounding Design Learning System

The design system must improve from both success and failure without turning into an ever-growing pile of anecdotes.

## Four memory layers

| Layer | Stores | Location | Promotion rule |
|---|---|---|---|
| Constitution | Cross-medium principles that almost never change | `SKILL.md` | Repeated class-level lesson or explicit user doctrine |
| Capability contract | Output-specific creative procedure and recurring evidence lessons | `references/capabilities/` inside this skill | Lesson applies to one recurring output class |
| Approved case | Sanitized successful pattern, stack, versions, commands, asset classes, approval scope | linked case under the relevant capability or this umbrella | User approved quality, reusable publication is authorized, and workflow is reproducible |
| Task checkpoint | Current direction, candidates, unresolved issues, exact approval state | project-local `.hermes/design/` or session | Never promote raw task state directly |

## Project-local design record

For substantial work, keep internal records under `.hermes/design/` unless project governance names another private path:

```text
.hermes/design/
  brief.md
  adoption-ledger.md
  iteration-ledger.md
  approval-scope.md
```

These files are production notes, not final-user content. **They are project-local and private by default.** Do not render them into the product, deck, video, report, or README unless a concise user-facing disclosure is genuinely needed. Do not commit `.hermes/design/` unless repository governance permits it and the user or project owner has authorized that exact record. Prefer an ignored/private path for client work.

## Consent, confidentiality, and redaction gate

Design approval is not permission to publish the process, feedback, assets, or case. Before promoting any task record into a shared skill, case reference, repository, or cross-project memory:

1. confirm that reusable publication or sharing is explicitly authorized for that scope;
2. remove credentials, tokens, account identifiers, personal data, private URLs, internal hostnames, customer names, unpublished product details, prices, analytics, and contractual information;
3. replace exact local paths, repository names, artifact IDs, hashes, and reproduction commands with sanitized forms unless they are public and necessary;
4. paraphrase user/client feedback by default; preserve verbatim text only when it is non-sensitive and explicitly approved for reuse;
5. never copy customer-owned images, fonts, videos, audio, decks, source files, brand kits, datasets, screenshots, or generated derivatives into a shared skill or case reference;
6. record reusable asset **classes, provenance rules, transformations, and quality gates**, not the private asset itself;
7. re-run secret and privacy scans before committing any promoted case.

If authorization is absent or ambiguous, keep only an abstract behavioral lesson with no identifying details. If sanitization would destroy the lesson's meaning, keep it project-local and do not promote it.

## Start-of-task retrieval

Before external research or fresh prototyping:

1. search session history for the last explicit approval/rejection;
2. search project and archive directories for approved artifacts and reproducible source;
3. load the relevant capability contract and its authorized positive-case references;
4. inspect the current ecosystem registry and live upstream status;
5. identify reusable foundations and invalidated assumptions.

A new task begins from the strongest approved prior state, not from generic defaults.

## Iteration ledger

After every meaningful review, record:

- artifact/version/hash or exact path;
- sanitized feedback or an approved verbatim excerpt;
- approval scope: medium, page/route/scene, visual/content/audio/interaction, and whether publication is included;
- observations that succeeded;
- defects and root causes;
- wasted path or unnecessary custom work;
- fix and verification evidence;
- candidate lesson and target layer.

## Promotion test

Promote a lesson only if it changes future behavior and meets one of these:

- the user stated a durable class-level preference;
- the same failure occurred or would plausibly recur across projects;
- a complex successful workflow was explicitly approved and reproducible;
- a mature tool/version/asset pipeline proved materially better than the prior path;
- a new regression gate catches a real defect.

Promotion also requires passing the consent, confidentiality, and redaction gate above. User approval of an artifact's visual quality does not imply approval to publish its case record.

Do not promote:

- temporary deadlines, file hashes, IDs, private paths, one-off copy, current task status;
- “liked it” without identifying what worked;
- a tool name that was researched but not adopted;
- a failure caused only by a transient outage;
- verbose process history with no behavioral rule.

## Where to write the lesson

- Cross-medium user-facing doctrine → patch `mature-design-director`.
- Interface/product behavior → `references/capabilities/interface.md`.
- Deck/submission workflow → `references/capabilities/presentation.md`; raw PPTX mechanics remain delegated.
- Long-form editorial documents → `references/capabilities/document.md`.
- Film/editorial/capture → `references/capabilities/motion.md`.
- Product imagery and identity preservation → `references/capabilities/image.md`.
- Engine-native game UI/assets → `references/capabilities/game-ui.md`.
- Sprites/frame animation → `references/capabilities/sprite.md`.
- Diagrams, infographics, comics, and explanatory animation → `references/capabilities/visual-explanation.md`.
- 3D, realtime, installation, and creative coding → `references/capabilities/spatial.md`.
- Music, voice, effects, and sonic identity → `references/capabilities/sound.md`.
- One approved multi-medium campaign → case reference under this umbrella.

Patch the narrowest correct capability. Do not create a new top-level creative authority or duplicate the same rule across capabilities.

## Positive-case contract

A reusable approved case should contain:

1. problem, audience, medium, and constraints;
2. final art direction and why it fit;
3. actual adopted projects, versions, licenses, and layer ownership;
4. sanitized source/artifact roles and what is generated; never private customer paths or assets;
5. reproducible build/capture/render/export commands with credentials, hosts, IDs, and private paths removed;
6. design tokens, asset sources, timing/data model, and truth boundaries;
7. quality gates and real execution results;
8. what the user approved and what remains unapproved;
9. adaptation rules for a different product;
10. known non-transferable details.

Every promoted case must begin with a short provenance block stating authorization scope, redaction date, asset inclusion policy, and whether any client/customer material was excluded. A shared case must remain useful when all private artifacts are absent.

## Regression-gate contract

A lesson is incomplete until it has a checkable gate. Examples:

- “No emoji UI” → search visible copy/assets and inspect rendered controls.
- “No card soup” → whole-screen contact sheet review with information-budget audit.
- “Do not hide real defects in video” → real-input product smoke before capture.
- “Adopt mature tools, do not cite them” → adoption ledger requires executed spike and exact used capability.
- “Cross-route style drift” → same-size route contact sheet gate.
- “Voice changes across chapters” → continuous master or speaker-verification canary plus listening gate.

## Pruning and evolution

Review this skill and related references periodically or after several major projects:

- merge duplicate rules;
- remove stale tool/version claims from always-loaded text;
- move changing ecosystem facts to the governed ecosystem sources;
- archive rejected cases that no longer affect behavior;
- keep positive baselines and regression gates concise;
- prefer one stronger rule over several layered warnings.

The target is not maximal size. The target is increasing predictive quality: fewer repeated failures, faster reuse of proven foundations, and stronger first-pass user-facing artifacts.
