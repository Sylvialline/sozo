#!/usr/bin/env python3
"""Produce the standard answers for all six questions and regression cases."""

from __future__ import annotations

import json
from pathlib import Path

from interpreter import VM, first_operands, load_program, parse_program


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"
TEST_PROGRAMS = ROOT / "tests" / "programs"
TEST_EXPECTED = ROOT / "tests" / "expected"


Q2_PROGRAM = """\
SET x 1
SET y 0
ADD x y
ADD 1 x
CMP x 10
JMP -3 0
PRN x y
"""


def execute(path: Path) -> tuple[int, int]:
    return VM(load_program(path)).run()


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    TEST_EXPECTED.mkdir(parents=True, exist_ok=True)

    q1_operands = first_operands(load_program(DATA / "prog1.txt"))
    q2 = VM(parse_program(Q2_PROGRAM)).run()
    q3 = execute(DATA / "prog2.txt")
    q4 = execute(DATA / "prog3.txt")
    q5 = execute(DATA / "prog4.txt")
    q6 = execute(DATA / "prog5.txt")

    (OUTPUTS / "q1.out").write_text("\n".join(q1_operands) + "\n", encoding="ascii")
    for number, values in enumerate((q2, q3, q4, q5, q6), start=2):
        (OUTPUTS / f"q{number}.out").write_text(
            f"{values[0]} {values[1]}\n", encoding="ascii"
        )

    regression: dict[str, list[int]] = {}
    for path in sorted(TEST_PROGRAMS.glob("*.txt")):
        result = execute(path)
        regression[path.stem] = list(result)
        (TEST_EXPECTED / f"{path.stem}.out").write_text(
            f"{result[0]} {result[1]}\n", encoding="ascii"
        )

    answers = {
        "question_1": {"input": "data/prog1.txt", "output": q1_operands},
        "question_2": {
            "output": list(q2),
            "summary": "x increases from 1 to 10; y accumulates 1+...+9 = 45",
        },
        "question_3": {"input": "data/prog2.txt", "output": list(q3)},
        "question_4": {"input": "data/prog3.txt", "output": list(q4)},
        "question_5": {"input": "data/prog4.txt", "output": list(q5)},
        "question_6": {"input": "data/prog5.txt", "output": list(q6)},
        "regression_cases": regression,
    }
    (ROOT / "answers" / "answers.json").parent.mkdir(parents=True, exist_ok=True)
    (ROOT / "answers" / "answers.json").write_text(
        json.dumps(answers, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
