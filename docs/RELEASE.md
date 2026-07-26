# Release process

The private `agent-skills-vault` remains the canonical editable source. This public repository is a manually reviewed publication mirror.

## Manual mirror only

1. Verify the canonical skill and its tests.
2. Export only `skills/mature-design-director/` plus the public repository files.
3. Exclude caches, local agent state, generated previews, credentials, private cases, and unrelated vault skills.
4. Compare the exported tree with the canonical skill.
5. Run secret scanning against the public worktree and staged content.
6. Run tests from the public repository.
7. Review the complete staged diff.
8. Commit and push deliberately.
9. Fresh-clone the advertised remote commit and rerun validation.

Never add an automatic private-vault-to-public synchronization job. A public update is a publication decision, not a backup side effect.

## Versioning

Use semantic versions from the skill frontmatter:

- patch: clarification, test, evidence, or non-breaking capability improvement;
- minor: new capability or backward-compatible contract field;
- major: authority, flow, registry schema, or routing change.

A release tag must match the frontmatter version.
