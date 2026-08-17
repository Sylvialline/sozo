# Workflow

This directory stores version-controlled assets shared by the training
workflow across computers.

## Skills

`skills/` is the canonical source for repository-specific Codex skills. Keep
the complete skill directory here, including optional `agents/`, `references/`,
`scripts/`, and `assets/` directories.

On each computer:

1. Pull the latest repository changes.
2. Synchronize each directory under `workflow/skills/` to the local Codex
   skills directory.
3. When changing a skill, update the repository copy in the same task and
   commit it so the other computer can receive it.

Currently mirrored:

- `sozo-code-review`
