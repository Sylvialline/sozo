# Repository instructions

## Protected exam source

Every file named `solve.py` represents code that the repository owner must be
able to write personally during the examination.

- Never create, edit, reformat, move, rename, delete, or automatically fix a
  `solve.py` file.
- Reading, running, profiling, testing, and reviewing `solve.py` is allowed.
- Put proposed changes in the conversation or in a separate review/notes file.
  The repository owner applies every change to `solve.py` personally.
- A broad request to refactor or clean the repository does not override this
  rule.

## Auxiliary files

Files outside `solve.py` are pre-examination infrastructure and may be improved
when requested. Prefer:

- Python standard-library-only implementations that work offline;
- small, stable, copy-friendly interfaces;
- visible failures over silent fallback behavior;
- optimizations that reduce total exam workflow time, including answer lookup
  and transcription, not only algorithm runtime.

## Skill synchronization

Treat `workflow/skills/` as the canonical, version-controlled source for every
Codex skill used by this repository's training workflow.

- Mirror every skill addition, edit, rename, or deletion to
  `workflow/skills/` in the same task, including `SKILL.md`, `agents/`,
  `references/`, `scripts/`, and `assets/`.
- Never leave a skill change only in a machine-local Codex skills directory.
- When the repository copy and an installed copy differ, preserve both long
  enough to inspect the diff, then make the repository copy canonical and
  synchronize the installed copy from it.
- After cloning or pulling on another computer, synchronize the repository
  copies into that computer's Codex skills directory before using or editing
  them.
