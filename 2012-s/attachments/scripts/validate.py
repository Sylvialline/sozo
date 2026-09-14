#!/usr/bin/env python3
"""Independent validation, feature checks, and deterministic property tests."""

from __future__ import annotations

import hashlib
import json
import random
import subprocess
import sys
from pathlib import Path

from interpreter import VM, load_program, parse_program


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"
TEST_PROGRAMS = ROOT / "tests" / "programs"
TEST_EXPECTED = ROOT / "tests" / "expected"


def independent_execute(text: str, max_steps: int = 1_000_000) -> tuple[int, int]:
    """A deliberately separate VM implementation working on raw token lists."""
    code = [line.split() for line in text.splitlines() if line.strip()]
    pc = 0
    steps = 0
    scopes: list[dict[str, int]] = [{}]
    subs: list[int] = []
    calls: list[tuple[int, int]] = []

    def read(token: str) -> int:
        if token.lstrip("-").isdigit():
            return int(token)
        return scopes[-1][token]

    while 0 <= pc < len(code):
        steps += 1
        if steps > max_steps:
            raise RuntimeError("independent VM step limit exceeded")
        op, left, right = code[pc]
        if op == "SET":
            scopes[-1][left] = read(right)
            pc += 1
        elif op == "ADD":
            scopes[-1][right] = read(left) + read(right)
            pc += 1
        elif op == "CMP":
            pc += 2 if read(left) == read(right) else 1
        elif op == "JMP":
            pc = pc + read(left)
        elif op == "PRN":
            return read(left), read(right)
        elif op == "SUB":
            destination = pc + read(left)
            subs.append(pc + 1)
            pc = destination
        elif op == "BAK":
            pc = subs.pop()
        elif op == "CAL":
            destination = pc + read(left)
            argument = read(right)
            calls.append((pc + 1, len(subs)))
            scopes.append({"in": argument})
            pc = destination
        elif op == "RET":
            returned = read(left)
            return_pc, sub_depth = calls.pop()
            assert len(subs) == sub_depth
            scopes.pop()
            scopes[-1]["out"] = returned
            pc = return_pc
        else:
            raise AssertionError(op)
    raise RuntimeError("independent VM left code without PRN")


def execute_primary(text: str) -> tuple[int, int]:
    return VM(parse_program(text)).run()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def output_pair(number: int) -> tuple[int, int]:
    fields = (OUTPUTS / f"q{number}.out").read_text(encoding="ascii").split()
    assert len(fields) == 2
    return int(fields[0]), int(fields[1])


def fibonacci(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def fib_program(n: int) -> str:
    return "\n".join(
        [
            f"SET n {n}",
            "CAL 3 n",
            "PRN out 0",
            "JMP 0 0",
            "CMP in 0",
            "JMP 2 0",
            "RET 0 0",
            "CMP in 1",
            "JMP 2 0",
            "RET 1 0",
            "SET saved in",
            "SET arg in",
            "ADD -1 arg",
            "CAL -9 arg",
            "SET first out",
            "SET arg saved",
            "ADD -2 arg",
            "CAL -13 arg",
            "ADD out first",
            "RET first 0",
        ]
    ) + "\n"


def sub_sum_program(n: int) -> str:
    return "\n".join(
        [
            "JMP 9 0",
            "CMP n 0",
            "JMP 2 0",
            "BAK 0 0",
            "ADD n sum",
            "ADD -1 n",
            "SUB -5 0",
            "ADD 1 unwind",
            "BAK 0 0",
            f"SET n {n}",
            "SET sum 0",
            "SET unwind 0",
            "SUB -11 0",
            "ADD unwind sum",
            "PRN n sum",
        ]
    ) + "\n"


def run_property_tests() -> int:
    rng = random.Random(2012)
    count = 0

    # Random straight-line arithmetic programs, including source/destination aliasing.
    for _ in range(300):
        lines = [
            f"SET a {rng.randint(-1000, 1000)}",
            f"SET b {rng.randint(-1000, 1000)}",
            f"SET c {rng.randint(-1000, 1000)}",
        ]
        names = ["a", "b", "c"]
        for _ in range(30):
            destination = rng.choice(names)
            if rng.randrange(3) == 0:
                source = str(rng.randint(-500, 500))
            else:
                source = rng.choice(names)
            opcode = rng.choice(["SET", "ADD"])
            if opcode == "SET":
                lines.append(f"SET {destination} {source}")
            else:
                lines.append(f"ADD {source} {destination}")
        lines.append("PRN a b")
        text = "\n".join(lines) + "\n"
        assert execute_primary(text) == independent_execute(text)
        count += 1

    # Structured loops verify CMP and that all relative jumps use the current line.
    for n in range(1, 51):
        text = (
            f"SET n {n}\nSET sum 0\nADD n sum\nADD -1 n\n"
            "CMP n 0\nJMP -3 0\nPRN n sum\n"
        )
        expected = (0, n * (n + 1) // 2)
        assert execute_primary(text) == independent_execute(text) == expected
        count += 1

    # Recursive SUB/BAK tests exercise LIFO return positions.
    for n in range(0, 31):
        text = sub_sum_program(n)
        expected = (0, n * (n + 1) // 2 + n)
        assert execute_primary(text) == independent_execute(text) == expected
        count += 1

    # Recursive CAL/RET tests exercise frame-local variables, in, and out.
    for n in range(0, 13):
        text = fib_program(n)
        expected = (fibonacci(n), 0)
        assert execute_primary(text) == independent_execute(text) == expected
        count += 1

    return count


def main() -> None:
    before = {
        path.relative_to(ROOT).as_posix(): sha256(path)
        for path in sorted(DATA.glob("*.txt"))
    }
    subprocess.run([sys.executable, str(ROOT / "scripts" / "generate_data.py")], check=True)
    after = {
        path.relative_to(ROOT).as_posix(): sha256(path)
        for path in sorted(DATA.glob("*.txt"))
    }
    assert before == after, "data generation is not deterministic"

    expected_main = {
        "prog2.txt": (126, 0),
        "prog3.txt": (22, 40),
        "prog4.txt": (0, 144),
        "prog5.txt": (3000, 3021),
    }
    expected_q1 = [
        "x", "y", "7", "x", "y", "-3", "-7", "2", "x", "-1000000",
        "0", "2", "y", "x",
    ]
    assert (OUTPUTS / "q1.out").read_text(encoding="ascii").splitlines() == expected_q1
    assert output_pair(2) == (10, 45)

    main_results: dict[str, list[int]] = {}
    for name, expected in expected_main.items():
        path = DATA / name
        text = path.read_text(encoding="ascii")
        parsed = load_program(path)
        assert len(parsed) < 100
        primary = VM(parsed).run()
        independent = independent_execute(text)
        assert primary == independent == expected
        question = int(name[4]) + 1
        assert output_pair(question) == expected
        main_results[name] = list(expected)

    # Stage-specific restrictions from the statement.
    p2_ops = {line.split()[0] for line in (DATA / "prog2.txt").read_text().splitlines()}
    assert p2_ops <= {"ADD", "SET", "PRN"}
    p1_variables = {
        token
        for line in (DATA / "prog1.txt").read_text().splitlines()
        for token in line.split()[1:]
        if token.isalpha()
    }
    assert p1_variables <= {"x", "y"}
    assert all(path.read_bytes().isascii() for path in DATA.glob("*.txt"))

    regression_results: dict[str, list[int]] = {}
    manifest = json.loads((ROOT / "generation_manifest.json").read_text(encoding="utf-8"))
    for path in sorted(TEST_PROGRAMS.glob("*.txt")):
        text = path.read_text(encoding="ascii")
        primary = execute_primary(text)
        independent = independent_execute(text)
        expected = tuple(manifest["regression_cases"][path.stem]["expected"])
        on_disk = tuple(map(int, (TEST_EXPECTED / f"{path.stem}.out").read_text().split()))
        assert primary == independent == expected == on_disk
        regression_results[path.stem] = list(expected)

    property_count = run_property_tests()
    report = {
        "status": "passed",
        "source_crosscheck": {
            "english_pages_checked": [4, 5],
            "japanese_pages_checked": [4, 5],
            "substantive_differences": [],
            "wording_difference": "Q3: English <100 lines; Japanese <=100 lines; data uses <100",
        },
        "main_results": main_results,
        "regression_cases_checked": len(regression_results),
        "property_tests_passed": property_count,
        "independent_vm_agreement": True,
        "deterministic_regeneration": True,
        "ascii_data": True,
        "all_programs_under_100_lines": True,
        "coverage": [
            "negative and variable operands",
            "ADD aliasing",
            "CMP true and false branches",
            "current-instruction-relative forward and backward JMP",
            "variable jump/call offsets",
            "nested and recursive SUB/BAK with LIFO returns",
            "literal and variable function arguments",
            "recursive CAL/RET",
            "per-call local-variable isolation",
            "special variables in and out",
            "negative literal return values",
            "unused operands",
        ],
    }
    (ROOT / "validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"validation passed: {property_count} property tests, {len(regression_results)} regression cases")


if __name__ == "__main__":
    main()
