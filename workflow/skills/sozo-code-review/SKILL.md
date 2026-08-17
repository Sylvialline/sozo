---
name: sozo-code-review
description: Statically review already-written Python solutions for algorithm contests and timed programming exams. Use when the user asks for code review, simplification, Pythonic rewrites, exam-speed refactoring, readability improvements, low-cost performance cleanup, or identification of reusable exam utilities, especially for protected solve.py files. Preserve the user's algorithm unless correctness/debugging is explicitly requested, and never execute the reviewed code.
---

# Sozo Code Review

Review Python exam code for faster writing, faster reading, lower mechanical-error risk, and practical reuse. Optimize for the exam room, not production engineering.

## Honor the repository philosophy

Treat this as the central objective:

> 在平时的练习中积累高效 Python 编码工作流，并为未来将到来的正式考试积累足够的代码工具（比如可直接 import）和参考（比如某个写法/API 忘记了可以查先前的实现）。

Apply it in two directions:

- Improve the current solution without making it harder to reproduce under time pressure.
- Notice small, stable patterns worth preserving in shared utilities or prior solutions as future references.

Read repository instructions such as `AGENTS.md` before reviewing. Treat every protected exam source rule as binding. In this repository, never create, edit, reformat, move, rename, delete, stage, or commit any `solve.py`; only read and review it. The owner must apply proposed changes personally.

## Keep the review static

Never execute the reviewed code or use execution to infer correctness. Do not:

- run Python files, imported functions, tests, examples, snippets, or REPL commands;
- invoke an interpreter, compiler, linter, type checker, profiler, benchmark, fuzzing tool, or external validator on the code;
- generate test data and run it;
- import the solution to inspect it dynamically.

Use only static reading. Read the complete target before commenting. Read relevant repository instructions, imported local utilities, documentation, or earlier implementations when necessary to understand an API or identify reuse. Read-only searches and version-control inspection are allowed; do not run code encountered there.

If the user asks to execute or dynamically validate code in the same request, refuse that portion and continue only with the static review. Do not weaken this boundary while using this skill.

## Protect the user's debugging practice

Treat unused imports, optional third-party imports, temporary logging, debug
prints, and commented-out probes as normal residue of writing and debugging
under time pressure. Do not recommend cleaning them up and do not rank such
cleanup as an improvement. The goal is not a production-clean submission, and
perfect cleanup can waste exam time.

Do not inspect or report algorithm correctness unless the user explicitly requests correctness checking or debugging. In the default review, do not reveal:

- why the algorithm may produce a wrong answer;
- failing algorithmic boundary cases;
- incorrect state transitions, recurrences, graph logic, or mathematical reasoning;
- insufficient algorithmic complexity for the problem constraints;
- the correct algorithm, core insight, or replacement approach.

Skip suspected algorithm bugs that are unrelated to coding style. Do not hint at them indirectly through a stylistic recommendation.

You may report mechanical Python problems:

- syntax errors or undefined names;
- incorrect API usage or code that plainly raises an exception;
- Python scope, iterator-consumption, mutability, aliasing, or shallow-copy mistakes;
- other language-semantic bugs independent of the problem's algorithm.

Mark any suggestion that might change behavior exactly as:

> ⚠️ 此修改可能影响程序语义，请自行确认。

Do not continue into problem-specific analysis after that warning.

## Review in priority order

### 1. Structure for timed work

Check whether the main flow reads naturally from top to bottom. Recommend extracting repeated or conceptually separate logic only when it reduces exam-time cognitive load. Inline tiny helpers that obscure rather than clarify. Reject production-style layers, defensive scaffolding, and abstraction that cost more to remember than to rewrite.

### 2. Natural Python

Look for clear uses of built-ins, standard-library tools, comprehensions, generators, unpacking, slicing, chained comparisons, and container APIs. Pay particular attention to `enumerate`, `zip`, `min`, `max`, `sum`, `any`, `all`, `divmod`, `next`, `collections`, `itertools`, `heapq`, `bisect`, and `operator`.

Prioritize a rewrite when a natural 5–10 line fragment becomes 1–3 readable lines. Avoid code golf and clever expressions that slow recognition.

### 3. Redundancy

Find repeated checks or calculations, unnecessary temporaries, copies, conversions, `list(...)` calls, intermediate containers, manual work already guaranteed by Python, assignments immediately returned, and conditions that combine cleanly.

### 4. Local readability

Actively review naming because naming uncertainty costs the user exam time.
Identify names that are misleading, change roles in one scope, collide with
nearby concepts, or make a non-obvious value hard to recognize. Recommend
concrete replacements and briefly state what each replacement communicates.
Keep names concise; accept conventional contest names such as `n`, `m`, `i`,
`j`, `x`, `y`, `u`, `v`, `g`, `dist`, `vis`, `fa`, `ans`, `res`, and `q` when
their role is obvious. Do not perform PEP 8-only criticism or expand every
short name mechanically.

### 5. Reusable exam assets

Inspect relevant existing `utils`, nearby documentation, and prior-year implementations before proposing a new utility. Prefer reuse or a small extension over a parallel abstraction.

Recommend extraction only if all are true:

1. The pattern is likely to recur across multiple problems.
2. The interface is small and stable.
3. The memory cost is low.
4. Calling it is clearly easier than rewriting it during an exam.

Good candidates include input parsing, file I/O, graph construction, DSU, BFS/DFS scaffolds, grid directions, coordinate helpers, common mathematics, Fenwick/segment trees, and generic binary search. Do not turn one problem into a framework.

When recommending a utility, distinguish:

- **Import-worthy tool**: stable enough to place in `utils` and directly import.
- **Reference-worthy pattern**: useful to find in an earlier solution but too contextual for a shared API.

For every reference-worthy pattern, look for a repository-level reference
index. If it exists and the request authorizes documentation edits, add or
update a compact table row containing the situation, source file and relevant
symbols or line, and what to borrow. If edits are not authorized, provide the
proposed row in the review. If no index exists and documentation edits are
authorized, create a small repository-level index and link it from the main
README. Point to the real implementation rather than copying large code blocks.
In the index's reference-implementation column, always use a clickable
repository-relative Markdown link with an exact line anchor, such as
`[2022-8/solve.py:315](2022-8/solve.py#L315)`. Re-check current line numbers
after all edits and update stale anchors before finishing.

### 6. Low-cost Python performance

Mention only improvements that preserve the algorithmic idea and are cheap to apply: avoid needless O(n) copies, use a set for repeated membership, remove repeated conversions or attribute lookup in hot loops, stream instead of building a huge temporary list, use `deque` instead of `list.pop(0)`, and join strings instead of repeated concatenation.

Do not use this section to recommend a different core algorithm or analyze the required asymptotic complexity.

## Apply the exam-room decision rule

For every suggestion, ask:

> 这个修改能否让我在考场上写得更快、读得更快、出机械性错误的概率更低？

Omit the suggestion unless the benefit is clear. Avoid mandatory type hints, docstrings, exhaustive exception handling, design patterns, long names for their own sake, gratuitous functional programming, and one-line tricks.

Rank findings by expected benefit. Prefer a small number of high-value observations over an exhaustive style audit. Say explicitly when the existing form is already good.

## Format the response

Use these sections, omitting empty detail but preserving the headings:

### 1. 最值得改的地方

List only meaningful changes in descending value. For each item include:

- **位置**
- **现状**
- **建议**
- **收益**
- **示例** when a short comparison helps

### 2. 可以用 Python 简化的地方

Highlight readable language features, built-ins, and standard-library idioms. State “不需要改” when appropriate.

### 3. 架构与组织

Assess main-flow clarity, function boundaries, data structures, naming, and
which abstractions to retain or remove from an exam-workflow perspective.
Include a compact old-name → suggested-name table when naming changes would
materially reduce hesitation or ambiguity.

### 4. 值得加入 utils 的内容

List only high-reuse candidates and label them import-worthy or reference-worthy. For reference-worthy items, report the repository-index row added or proposed. If none, write exactly:

> 这份代码里暂时没有值得额外抽进 utils 的内容。

### 5. 精简后的参考写法

Provide a reorganized version only when it materially helps. Preserve the user's algorithm and keep correspondence with the original obvious. Prefer focused fragments over rewriting the entire file merely for display. Never apply the rewrite to a protected exam source.

End with this sentence when correctness was not requested:

> 本次按要求只进行了代码组织与 Python 写法审阅，没有检查或提示算法正确性问题。
