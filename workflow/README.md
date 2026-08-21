# Workflow

This directory stores version-controlled assets shared by the training
workflow across computers.

## Python runtimes

[`run_python.py`](run_python.py) provides one command for selecting CPython or
PyPy without changing any `solve.py` or the machine's PowerShell execution
policy. Child processes and the Windows console use UTF-8 while the target is
running. See [`PYPY.md`](PYPY.md) for the portable Windows setup, comparison
workflow, and exam-time decision rules.

Machine-local interpreters live under `runtimes/` and are intentionally not
version-controlled.

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
