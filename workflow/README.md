# Workflow

This directory stores version-controlled assets shared by the training
workflow across computers.

## Python runtimes

[`run_python.py`](run_python.py) provides one command for selecting CPython or
PyPy without changing any `solve.py` or the machine's PowerShell execution
policy. Child processes and the Windows console use UTF-8 while the target is
running. See [`PYPY.md`](PYPY.md) for the portable Windows setup, comparison
workflow, and exam-time decision rules. The workspace task in
[`../.vscode/tasks.json`](../.vscode/tasks.json) runs the current editor file
through this launcher with PyPy.

Machine-local interpreters live under `runtimes/` and are intentionally not
version-controlled.

## VS Code workspace helpers

[`../.vscode/default.code-snippets`](../.vscode/default.code-snippets) provides
the `exam-default` Python snippet for inserting the standard `Path`, `DATA`,
`Batch`, `Case`, `Rows`, and `Exam` file header. [`../.vscode/tasks.json`](../.vscode/tasks.json)
registers `Python: Run Current File with PyPy` as the default Build Task, so
<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>B</kbd> runs the active file with PyPy while
the Python extension's **Run Python File** remains the CPython entry point.

## Performance profiling

[`profile_python.py`](profile_python.py) provides a no-source-edit workflow for
function-level `cProfile` and line-level `line_profiler` diagnosis. See
[`PROFILING.md`](PROFILING.md) for installation, exam-time commands, result
interpretation, multiprocessing limits, and the final CPython/PyPy comparison.

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
