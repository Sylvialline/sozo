from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

Interval = Tuple[int, int]
Assignment = Tuple[int, int]  # xM = xN -> (M, N)


def read_ints(path: str | Path) -> List[int]:
    text = Path(path).read_text(encoding="utf-8").strip()
    if not text:
        return []
    return [int(x.strip()) for x in text.split(",") if x.strip()]


def parse_inequalities(path: str | Path) -> Dict[int, Interval]:
    """Read triples N,S,T. If N occurs repeatedly, the rightmost triple is effective."""
    a = read_ints(path)
    if len(a) % 3:
        raise ValueError(f"invalid inequality file: {path}")
    res: Dict[int, Interval] = {}
    for i in range(0, len(a), 3):
        n, s, t = a[i:i+3]
        if not (0 <= n <= 999 and 0 <= s <= t <= 999):
            raise ValueError(f"out-of-range inequality triple {(n, s, t)} in {path}")
        res[n] = (s, t)
    return res


def parse_program(path: str | Path) -> List[Assignment]:
    """Read pairs M,N representing xM=xN, in execution order."""
    a = read_ints(path)
    if len(a) % 2:
        raise ValueError(f"invalid program file: {path}")
    res: List[Assignment] = []
    for i in range(0, len(a), 2):
        m, n = a[i:i+2]
        if not (0 <= m <= 999 and 0 <= n <= 999):
            raise ValueError(f"out-of-range assignment {(m, n)} in {path}")
        res.append((m, n))
    return res


def fmt_var(n: int) -> str:
    return f"x{n}"


def fmt_interval(iv: Interval) -> str:
    return f"[{iv[0]}, {iv[1]}]"


def q1(ineq_path: str | Path) -> List[Tuple[int, int, int]]:
    ineq = parse_inequalities(ineq_path)
    if not ineq:
        return []
    best = max(t - s for s, t in ineq.values())
    return [(n, s, t) for n, (s, t) in sorted(ineq.items()) if t - s == best]


def q2(program_path: str | Path) -> List[int]:
    program = parse_program(program_path)
    if not program:
        return []
    cnt = Counter(m for m, _ in program)
    best = max(cnt.values())
    return [n for n in sorted(cnt) if cnt[n] == best]


def execute_ranges(program: List[Assignment], ineq: Dict[int, Interval]):
    """
    Symbolically execute P using intervals.

    A variable is initialized only when it first has to be read on the RHS before
    having received a value. Its initial interval is its effective inequality, or
    [0,100] if no inequality exists. A LHS variable gets exactly the current value
    interval of the RHS variable.

    Returns:
      current: interval at program end for every variable that acquired a value
      runtime: min/max interval over all values held during execution (initialization
               included; pre-initialization values excluded)
      appeared: all variables that occur in at least one assignment statement
    """
    current: Dict[int, Interval] = {}
    runtime: Dict[int, Interval] = {}
    appeared = set()

    def record(v: int, iv: Interval) -> None:
        if v in runtime:
            a, b = runtime[v]
            runtime[v] = (min(a, iv[0]), max(b, iv[1]))
        else:
            runtime[v] = iv

    for m, n in program:
        appeared.add(m)
        appeared.add(n)
        if n not in current:
            current[n] = ineq.get(n, (0, 100))
            record(n, current[n])
        current[m] = current[n]
        record(m, current[m])

    return current, runtime, appeared


def q3(program_path: str | Path, ineq_path: str | Path, targets=(31, 41, 51)):
    program = parse_program(program_path)
    ineq = parse_inequalities(ineq_path)
    current, _, appeared = execute_ranges(program, ineq)
    ans: Dict[int, Optional[Interval]] = {}
    for v in targets:
        ans[v] = current.get(v) if v in appeared else None
    return ans


def q4(program_path: str | Path, ineq_path: str | Path, targets=(31, 41, 51)):
    program = parse_program(program_path)
    ineq = parse_inequalities(ineq_path)
    _, runtime, appeared = execute_ranges(program, ineq)
    ans: Dict[int, Optional[Interval]] = {}
    for v in targets:
        ans[v] = runtime.get(v) if v in appeared else None
    return ans


def q5(program_path: str | Path, ineq_path: str | Path) -> List[int]:
    program = parse_program(program_path)
    ineq = parse_inequalities(ineq_path)
    _, runtime, _ = execute_ranges(program, ineq)
    bad = []
    for v, (a, b) in runtime.items():
        if v not in ineq:
            continue
        s, t = ineq[v]
        if a < s or t < b:
            bad.append(v)
    return sorted(bad)


def q6(program_path: str | Path, ineq_path: str | Path) -> List[Assignment]:
    program = parse_program(program_path)
    ineq = parse_inequalities(ineq_path)
    bad: List[Assignment] = []
    seen = set()
    for m, n in program:
        if (m, n) in seen:
            continue
        seen.add((m, n))
        if m not in ineq or n not in ineq:
            continue
        sm, tm = ineq[m]
        sn, tn = ineq[n]
        if not (sm <= sn <= tn <= tm):
            bad.append((m, n))
    return bad


def q7(program_path: str | Path, ineq_path: str | Path) -> Optional[Dict[int, Interval]]:
    """
    Define intervals for program variables missing from the inequality file so
    every assignment xM=xN is statically consistent (interval(N) subset interval(M)).

    Construction: direct the graph M -> N. For every missing variable v, collect
    all fixed-interval ancestors that can reach v; v must be contained in all of
    them, so choose the full intersection of those ancestor intervals. With no
    fixed ancestor choose [0,999]. Finally validate every assignment. If validation
    fails, no possible definitions exist.
    """
    program = parse_program(program_path)
    fixed = parse_inequalities(ineq_path)
    vars_in_program = sorted({v for e in program for v in e})
    missing = [v for v in vars_in_program if v not in fixed]

    # fixed ancestors propagated along assignment graph M -> N
    anc: Dict[int, set[int]] = {v: set() for v in vars_in_program}
    for v in vars_in_program:
        if v in fixed:
            anc[v].add(v)

    changed = True
    while changed:
        changed = False
        for m, n in program:
            before = len(anc[n])
            anc[n] |= anc[m]
            if len(anc[n]) != before:
                changed = True

    chosen: Dict[int, Interval] = dict(fixed)
    definitions: Dict[int, Interval] = {}
    for v in missing:
        if anc[v]:
            s = max(fixed[u][0] for u in anc[v])
            t = min(fixed[u][1] for u in anc[v])
        else:
            s, t = 0, 999
        if s > t:
            return None
        definitions[v] = (s, t)
        chosen[v] = (s, t)

    for m, n in program:
        sm, tm = chosen[m]
        sn, tn = chosen[n]
        if not (sm <= sn <= tn <= tm):
            return None

    return dict(sorted(definitions.items()))


def format_q3_q4(ans: Dict[int, Optional[Interval]]) -> str:
    parts = []
    for v in (31, 41, 51):
        iv = ans[v]
        parts.append(f"x{v}: Undefined" if iv is None else f"x{v}: {iv[0]} {iv[1]}")
    return "; ".join(parts)


def assignment_text(a: Assignment) -> str:
    return f"x{a[0]}=x{a[1]}"


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("question", type=int, choices=range(1, 8))
    p.add_argument("files", nargs="+")
    args = p.parse_args()

    q = args.question
    if q == 1:
        print(q1(args.files[0]))
    elif q == 2:
        print(q2(args.files[0]))
    elif q == 3:
        print(format_q3_q4(q3(args.files[0], args.files[1])))
    elif q == 4:
        print(format_q3_q4(q4(args.files[0], args.files[1])))
    elif q == 5:
        print(q5(args.files[0], args.files[1]) or "None")
    elif q == 6:
        ans = q6(args.files[0], args.files[1])
        print([assignment_text(x) for x in ans] if ans else "None")
    elif q == 7:
        ans = q7(args.files[0], args.files[1])
        print(ans if ans is not None else "None")
