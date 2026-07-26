# Contributing

Contributions are welcome when they improve creative decisions, evidence, portability, or maintainability without creating a parallel authority.

## Before changing the skill

1. Identify the final-user problem and the exact behavior that changes.
2. Check `references/capability-registry.json` for the narrowest owner.
3. Check `references/creative-skill-sources.json` and the production catalog before inventing new workflow.
4. Confirm source/license boundaries before adapting public material.
5. Keep project-specific assets, private paths, credentials, client information, and raw feedback out of the repository.

## Where a change belongs

- Cross-capability durable principle → `SKILL.md`.
- Output-specific creative decision/evidence → one capability contract.
- Tool/provider command → external adapter or production ecosystem entry.
- Public skill behavior/provenance → creative-skill source registry.
- One approved example → sanitized case or showcase after exact publication approval.
- One-off task state → nowhere in the shared skill.

## Add a capability

Add a contract under `references/capabilities/`, then add one registry row with:

- unique `id`;
- `accepts`;
- `outputs`, each with an `id`, required foundation/mechanics roles, allowed delivered classifications, and primary-artifact suffixes;
- creative `foundations` roles and admissible source classes;
- assembly-mechanics `delegates` roles and candidates;
- required `evidence` IDs.

Do not edit the validator to add the capability name. The extension regression test proves that a new declared capability validates without code changes. If the capability introduces an opaque file/container format, add a format-level probe and regression fixture rather than trusting a suffix or hard-coding the capability. Package multi-file `.zip` artifacts with the exact hash-bound `artifact-manifest.json` contract documented by the skill.

## Required checks

```bash
python3 skills/mature-design-director/maintenance/validate_skill.py
python3 -m unittest discover -s skills/mature-design-director/tests -p 'test_*.py'
```

For production-catalog changes, run the relevant live audit and include the JSON evidence. Manual-review statuses are acceptable; fabricated green statuses are not.
