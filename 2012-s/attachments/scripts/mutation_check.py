#!/usr/bin/env python3
"""Confirm that the supplied data kills representative incorrect interpreters."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_mutant(text: str, mutant: str, max_steps: int = 200_000) -> tuple[int, int]:
    code = [line.split() for line in text.splitlines() if line.strip()]
    pc = 0
    steps = 0
    scopes: list[dict[str, int]] = [{}]
    sub_returns: list[int] = []
    calls: list[tuple[int, int, bool]] = []

    def value(token: str) -> int:
        if token.lstrip("-").isdigit():
            return int(token)
        return scopes[-1][token]

    def offset(token: str) -> int:
        if mutant == "variable_offsets_rejected":
            return int(token)
        return value(token)

    while 0 <= pc < len(code):
        steps += 1
        if steps > max_steps:
            raise RuntimeError("step limit")
        op, a, b = code[pc]

        if mutant == "unused_operands_evaluated" and op in {"JMP", "SUB", "BAK", "RET"}:
            value(b)

        if op == "SET":
            scopes[-1][a] = value(b)
            pc += 1
        elif op == "ADD":
            if mutant == "add_overwrites_destination":
                scopes[-1][b] = value(a)
            else:
                scopes[-1][b] = value(a) + value(b)
            pc += 1
        elif op == "CMP":
            equal = value(a) == value(b)
            if mutant == "cmp_condition_inverted":
                equal = not equal
            pc += 2 if equal else 1
        elif op == "JMP":
            base = pc + 1 if mutant == "jmp_based_on_next_line" else pc
            pc = base + offset(a)
        elif op == "PRN":
            return value(a), value(b)
        elif op == "SUB":
            base = pc + 1 if mutant == "sub_target_based_on_next_line" else pc
            destination = base + offset(a)
            return_pc = pc if mutant == "sub_returns_to_call_line" else pc + 1
            sub_returns.append(return_pc)
            pc = destination
        elif op == "BAK":
            if mutant == "sub_returns_fifo":
                pc = sub_returns.pop(0)
            else:
                pc = sub_returns.pop()
        elif op == "CAL":
            base = pc + 1 if mutant == "cal_target_based_on_next_line" else pc
            destination = base + offset(a)
            argument = value(b)
            return_pc = pc if mutant == "cal_returns_to_call_line" else pc + 1
            new_scope = mutant != "function_variables_are_global"
            calls.append((return_pc, len(sub_returns), new_scope))
            if new_scope:
                scopes.append({} if mutant == "function_argument_in_missing" else {"in": argument})
            else:
                scopes[-1]["in"] = argument
            pc = destination
        elif op == "RET":
            returned = value(b) if mutant == "ret_uses_second_operand" else value(a)
            return_pc, sub_depth, new_scope = calls.pop()
            if len(sub_returns) != sub_depth:
                raise RuntimeError("unfinished SUB")
            if new_scope:
                scopes.pop()
            if mutant != "returned_value_not_written_to_out":
                scopes[-1]["out"] = returned
            pc = return_pc
        else:
            raise AssertionError(op)
    raise RuntimeError("left program")


def load_cases() -> list[tuple[str, str, tuple[int, int]]]:
    cases: list[tuple[str, str, tuple[int, int]]] = []
    for question, filename in [(3, "prog2.txt"), (4, "prog3.txt"), (5, "prog4.txt"), (6, "prog5.txt")]:
        text = (ROOT / "data" / filename).read_text(encoding="ascii")
        expected = tuple(map(int, (ROOT / "outputs" / f"q{question}.out").read_text().split()))
        cases.append((filename.removesuffix(".txt"), text, expected))
    for path in sorted((ROOT / "tests" / "programs").glob("*.txt")):
        text = path.read_text(encoding="ascii")
        expected = tuple(map(int, (ROOT / "tests" / "expected" / f"{path.stem}.out").read_text().split()))
        cases.append((path.stem, text, expected))
    return cases


def main() -> None:
    mutants = [
        "add_overwrites_destination",
        "cmp_condition_inverted",
        "jmp_based_on_next_line",
        "sub_target_based_on_next_line",
        "sub_returns_to_call_line",
        "sub_returns_fifo",
        "cal_target_based_on_next_line",
        "cal_returns_to_call_line",
        "function_variables_are_global",
        "function_argument_in_missing",
        "returned_value_not_written_to_out",
        "ret_uses_second_operand",
        "unused_operands_evaluated",
        "variable_offsets_rejected",
    ]
    cases = load_cases()
    caught: dict[str, str] = {}
    for mutant in mutants:
        for name, text, expected in cases:
            try:
                actual = run_mutant(text, mutant)
            except Exception as error:  # An error also means the valid test rejected the mutant.
                caught[mutant] = f"{name} (error: {type(error).__name__})"
                break
            if actual != expected:
                caught[mutant] = f"{name} (got {actual}, expected {expected})"
                break
        if mutant not in caught:
            raise AssertionError(f"mutant survived: {mutant}")

    report = {
        "status": "passed",
        "mutants_tested": len(mutants),
        "mutants_caught": len(caught),
        "first_killing_case": caught,
    }
    (ROOT / "mutation_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"mutation check passed: {len(caught)}/{len(mutants)} representative bugs caught")


if __name__ == "__main__":
    main()
