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
