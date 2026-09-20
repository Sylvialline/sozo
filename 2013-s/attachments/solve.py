
"""Generate deterministic standard answers using exact decimal/algebraic arithmetic."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path

from exact_geometry import area_text, count_koch, count_r0, count_r1, parse_decimal_exact


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ANSWERS = ROOT / "answers"


def reduced_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def solve_q1(lines: list[str]) -> list[str]:
    return [str(count_r0(parse_decimal_exact(line))) for line in lines]


def solve_q2(lines: list[str]) -> list[str]:
    answers = []
    for line in lines:
        d = parse_decimal_exact(line)
        answers.append(reduced_text(Fraction(count_r1(d), 4 * count_r0(d))))
    return answers


def solve_q3(lines: list[str]) -> list[str]:
    if any(line != "K2" for line in lines):
        raise ValueError("q3 queries must be K2")
    return [area_text(2) for _ in lines]


def solve_q4(lines: list[str]) -> list[str]:
    return [area_text(int(line)) for line in lines]


def solve_q5(lines: list[str]) -> list[str]:
    return [str(count_koch(parse_decimal_exact(line), 2)) for line in lines]


def solve_q6(lines: list[str]) -> list[str]:
    answers = []
    for line in lines:
        d_text, n_text = line.split()
        answers.append(str(count_koch(parse_decimal_exact(d_text), int(n_text))))
    return answers


SOLVERS = [solve_q1, solve_q2, solve_q3, solve_q4, solve_q5, solve_q6]


def main() -> None:
    ANSWERS.mkdir(parents=True, exist_ok=True)
    for index, solver in enumerate(SOLVERS, 1):
        lines = (DATA / f"q{index}.txt").read_text(encoding="ascii").splitlines()
        output = solver(lines)
        if len(output) != len(lines):
            raise AssertionError("answer count mismatch")
        (ANSWERS / f"q{index}.txt").write_text(
            "\n".join(output) + "\n", encoding="ascii", newline="\n"
        )


if __name__ == "__main__":
    main()
