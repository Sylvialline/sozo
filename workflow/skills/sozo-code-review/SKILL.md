---
name: sozo-code-review
description: Perform a structured review of an already-written Python solution for an algorithm contest or timed exam when the current request explicitly asks to review or audit the solution as a whole. When explicitly invoked alongside another task, contribute exam-oriented principles without imposing review-only restrictions. Do not treat narrow follow-up questions, design discussions, debugging, implementation or refactoring requests, or code edits as a new review unless the user asks to resume one.
---

# Sozo Code Review

Help the user build Python solutions that are quick to write, quick to verify,
and hard to mistype under exam pressure. Apply the full review workflow only
when the current request is actually a review.

## Route the current request first

Review mode is **request-scoped, not conversation-scoped**. Re-evaluate the
user's intent on every message; an earlier invocation or review does not keep
later turns in review mode.

Use **structured review mode** when the current request asks for a review or
audit of an existing solution as a whole, or explicitly asks to continue the
review. Examples include asking what is worth improving across a solution,
requesting an exam-oriented code review, or invoking this skill for that
purpose.

Use **normal task mode** when the current request instead asks a narrow or
different question, even when it follows a review. Examples include:

- explaining one earlier finding or one checker error;
- discussing a design, type annotation, API, or alternative approach;
- asking how to implement one change;
- debugging or checking a specific correctness concern;
- editing, refactoring, running, testing, or profiling code;
- asking for a code snippet rather than another whole-solution review.

In normal task mode, answer or act in the format appropriate to the current
request. Do not reuse the review headings, review disclaimer, static-only rule,
or correctness restrictions merely because this skill appeared earlier. Reuse
only the general exam-oriented principles below when they help.

If one request combines review with implementation or dynamic validation,
scope the review rules to the review portion and handle the other authorized
work normally. Explicit user instructions about the current deliverable take
priority over this skill's review defaults. System, repository, permission, and
safety constraints remain binding.

## General exam-oriented principles

Apply these principles in both modes when relevant:

- Prefer changes that reduce exam-time writing, reading, lookup, or mechanical
  error risk. Avoid production-style layers and defensive scaffolding whose
  memory cost exceeds their benefit.
- Preserve the user's chosen algorithm or design unless the current request
  asks to debug, replace, compare, or change it.
- Treat unused imports, optional third-party imports, temporary logging, debug
  prints, and commented probes as normal working residue. Do not raise cleanup
  as an unsolicited priority, but honor an explicit cleanup request.
- Prefer small, stable, copy-friendly interfaces and visible failures over
  silent fallback behavior.
- Notice reusable patterns, but do not turn a contextual solution into a
  framework.

The repository philosophy is:

> 在平时的练习中积累高效 Python 编码工作流，并为未来将到来的正式考试积累足够的代码工具（比如可直接 import）和参考（比如某个写法/API 忘记了可以查先前的实现）。

## Honor repository and source protections

Read repository instructions such as `AGENTS.md` before acting. In this
repository, every `solve.py` is protected exam source: never create, edit,
reformat, move, rename, delete, stage, or commit it. Reading, reviewing,
running, testing, and profiling are allowed when the current request calls for
them. Put proposed changes in the conversation or a separate authorized notes
file so the owner applies them personally.

When creating or extending reusable APIs under `utils`, write concise Chinese
docstrings for new public modules, classes, and functions. Document the
contract or important convention rather than repeating the symbol name. Keep
runtime `print` and logging messages in English. Do not rewrite existing
utilities solely to impose this convention retroactively.

## Structured review mode

### Evidence and correctness boundary

Read the complete target before commenting. Read only the relevant repository
instructions, imported local utilities, documentation, or earlier solutions
needed to understand the code or evaluate reuse.

A review is static by default. Do not execute code merely to manufacture
confidence. If the current request explicitly asks for execution, tests,
profiling, or dynamic validation, honor that request when permitted and clearly
distinguish runtime evidence from static findings.

Do not inspect or reveal problem-specific algorithm correctness unless the
current request asks for correctness checking or debugging. Without that
request, limit correctness comments to mechanical Python issues such as syntax,
undefined names, incorrect API use, scope, iterator consumption, mutability,
aliasing, and other language-semantic bugs independent of the algorithm.

Clearly identify proposals that may change behavior. When correctness or
debugging was requested, analyze the behavioral consequences normally rather
than stopping at a generic warning.

### Review priorities

Rank findings by expected exam-room benefit and prefer a few high-value
observations over an exhaustive style audit.

1. **Problem-local architecture.** Identify the concrete subsystem being
   built, such as a parser/interpreter, reversible search, simulation, or graph
   pipeline. Assess responsibility boundaries, state ownership, data flow,
   mutation and rollback invariants, helper APIs, and whether the model makes
   the problem easier to reason about. Do not mistake ordinary `task1`,
   `task2`, ... ordering or answer orchestration for meaningful architecture.
2. **Natural Python.** Look for readable uses of built-ins, comprehensions,
   generators, unpacking, slicing, container APIs, and relevant standard
   library tools. Prefer recognizable idioms over code golf.
3. **Redundancy and local readability.** Find repeated checks or calculations,
   needless copies or conversions, unnecessary temporaries, and names that are
   misleading or change roles. Accept conventional contest names when their
   meaning is obvious.
4. **Reusable exam assets.** Inspect relevant existing `utils`, nearby
   documentation, and prior solutions before proposing a new utility. Extract
   only patterns likely to recur, with a small stable interface and lower
   memory cost than rewriting.
5. **Low-cost performance.** Mention cheap improvements that preserve the core
   algorithm, such as avoiding needless copies, using a set for repeated
   membership, using `deque` instead of `list.pop(0)`, or joining strings.

Do not recommend mandatory type hints, docstrings, exhaustive exception
handling, design patterns, long names, or functional tricks without a clear
exam-time payoff. Say when the existing form is already good.

### Reuse classification

Distinguish:

- **Import-worthy tool:** stable and generic enough for `utils`.
- **Reference-worthy pattern:** useful to find in an earlier solution but too
  contextual for a shared API.

For a reference-worthy pattern, look for a repository-level reference index.
If the current request authorizes documentation edits, add or update a compact
row with the situation, source and exact line, and what to borrow. Otherwise,
propose the row only when it adds value. Use a repository-relative Markdown
link with an exact line anchor, such as
`[2022-8/solve.py:315](2022-8/solve.py#L315)`.

### Review output

Choose a structure that makes the findings easy to scan. For a comprehensive
review, useful sections may include:

- most valuable changes;
- Python simplifications;
- architecture and organization;
- reusable assets;
- focused reference rewrites.

These headings are optional, not a required template. Omit empty or irrelevant
sections. Provide a reorganized version only when it materially helps, and
prefer focused fragments over rewriting a whole protected source for display.
Do not append a stock disclaimer or repeat the review format in later narrow
follow-ups.

## Normal task mode

Handle design discussion, explanation, debugging, implementation, editing,
testing, and other follow-up work according to the current request. The skill's
general exam-oriented principles may influence choices, but they do not impose
a review deliverable.

- Answer narrow questions directly.
- When changes are requested and allowed, implement and verify them rather
  than returning a review.
- When execution or testing is requested and allowed, perform it rather than
  citing the review's static default.
- When correctness or debugging is requested, investigate it directly.
- Do not apply review-only headings, warnings, or closing sentences.
