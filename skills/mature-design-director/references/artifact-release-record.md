# Artifact Release Record

`templates/artifact-release-record.json` is a project instance of the lifecycle declared in `references/capability-registry.json`. The registry remains the authority; this document only explains how to bind one artifact to it.

## Create the record

Copy the template to `.hermes/design/artifact-release.json` at the start of substantial work. Keep it private and project-local unless publication is explicitly authorized.

Set `registry_sha256` to the SHA-256 of the installed `references/capability-registry.json`. Validation loads that exact installed registry and rejects a same-version substitute.

Identify:

- `producer`: the person or agent that authored the candidate;
- `creative_authority`: the director that accepts delegated bytes and owns the final state transition;
- `final_audience`: the named user of the natural artifact, not the requester, scorer, or portfolio viewer;
- `requester_reviewer`: the people or roles evaluating or operating the work;
- `native_medium.requested`: what the task actually asked for;
- `native_medium.actual`: what was actually built;
- `native_medium.classification`: a truthful class such as `native-product`, `editable-source`, `rendered-output`, or `concept-proof`.
- `native_medium.output_class`: one output contract declared by the selected capability. Its foundation and mechanics roles become mandatory only when the current or historical lifecycle state declares them required.

Bind `primary_artifact.ref` to the actual native artifact or a deterministic bundle of a multi-file project, and bind `primary_artifact.sha256` to those exact bytes. The selected output contract declares allowed delivered classifications and file suffixes. Once the lifecycle reaches a state that requires assembly mechanics, the validator also checks recognizable natural-format/container identity; plain text renamed to an allowed suffix fails. A `concept-proof`, README, source generator, component board, or review wrapper cannot claim a stronger output class.

### Package a multi-file artifact

Every `.zip` primary artifact must contain `artifact-manifest.json` at archive root. Start from `templates/artifact-bundle-manifest.json` and list every non-directory payload exactly once with its lowercase SHA-256. Do not list the manifest itself. `primary` must name one listed payload whose actual bytes pass the same natural-format probe as a direct artifact. The archive must contain no undeclared files, duplicate names, encrypted entries, symlinks, absolute paths, traversal paths, or nested ZIP primary.

The manifest establishes bundle identity, not artistic maturity. Source code and generators may be declared secondary payloads when legitimately needed, but a README, generator, source listing, or component board cannot be the natural primary entrypoint. Unsupported opaque authoring formats need a tested format adapter before they can support a stronger lifecycle state; do not bypass the probe by renaming them.

## Separate foundation from mechanics

Each `creative_foundations` row has:

- `role`: a role declared by the selected capability;
- `source_class`: one admissible source class declared under that capability role;
- `source`: the exact approved system, artboard, asset family, media source, or selected custom source;
- `evidence`: `creative-source`.

Each `assembly_mechanics` row has:

- `role`: the implementation role;
- `candidate`: one mechanics candidate declared under that capability role;
- `tool`: the actual runtime, authoring, rendering, export, or packaging tool;
- `evidence`: a bound non-creative evidence ID, commonly `technical-integrity` or `working-artifact`.

A source and a tool cannot occupy both layers. A generator, codebase, browser, office API, engine, or successful command is not a creative foundation by itself.

## Bind evidence bytes

Each key in `evidence` is an evidence ID declared by the registry. Its value is a non-empty list of objects:

```json
{
  "ref": "evidence/whole-artifact-contact-sheet.png",
  "sha256": "lowercase 64-character digest",
  "subject_sha256": "digest of the exact primary artifact being reviewed",
  "description": "what these exact bytes establish",
  "reviewer": "independent reviewer identity or empty string",
  "benchmarks": ["named mature benchmark when required"]
}
```

`ref` must be a regular project-local file, not an external path or symlink. The validator recomputes its hash. A README claim without bound evidence bytes does not count.

`proof-selection` and `independent-critique` require a reviewer different from `producer`. `proof-selection` and `comparative-quality` require named mature benchmarks. Automated checks can create technical evidence but cannot supply these judgments.

Evidence IDs listed together under the registry's `authority.distinct_evidence_sets` must bind different bytes. Do not reuse one screenshot, README, contact sheet, or review note as foundation, selection, final render, critique, and delivery evidence. Duplicate paths or hashes within one evidence list also fail.

## Record lifecycle history

Start `state_history` at the registry's `initial_state`. For each transition, add one row for the target state and attach every evidence ID required by that transition. Attach each evidence ID to exactly one lifecycle row; do not reuse a claim to satisfy multiple stages. State-level `requires_output_foundations` and `requires_output_mechanics` flags make those output roles mandatory from the first stage that needs them; a later rejection does not erase an earlier obligation.

Entering `production-candidate` means the complete working and rendered artifact already exists in its native context. It is not a synonym for “production has started.” Comparative whole-artifact critique moves that exact candidate to `release-candidate`.

A `delivered` record must contain:

- all authority `release_evidence`;
- all evidence required by the selected capability;
- at least one creative foundation and assembly mechanic;
- a legal, unskipped state history;
- no rejection reason.

A user rejection may move any nonterminal state directly to `rejected`. Record the reason. A rejected artifact does not transition back or become a positive reference; start a new candidate.

## Accept delegated output

List only delegations whose bytes are actually adopted into the artifact. Each row has:

```json
{
  "task_id": "delegated-task-id",
  "status": "completed",
  "artifact_ref": "project-local/path/to/the/adopted/artifact",
  "artifact_sha256": "digest already bound by evidence",
  "accepted_by": "the creative_authority value",
  "acceptance_evidence": "bound evidence ID used for the acceptance decision"
}
```

A timeout, no-summary task, duplicate task ID, missing hash, unbound artifact, or acceptance by anyone other than `creative_authority` fails closed. `acceptance_evidence` must bind the exact accepted artifact hash, not merely name some other evidence type. Child completion never supplies final acceptance.

## Validate before a delivered claim

```bash
python3 <skill-root>/maintenance/validate_skill.py \
  --artifact-record .hermes/design/artifact-release.json \
  --project-root .
```

The validator proves state/evidence integrity. It deliberately does not compute an aesthetic score; selection and whole-artifact maturity still require the recorded human or independent comparative judgment.
