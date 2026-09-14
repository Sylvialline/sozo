#!/usr/bin/env python3
"""Reference parser and interpreter for the language L."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


VARIABLE_RE = re.compile(r"[a-z]+\Z")
INTEGER_RE = re.compile(r"-?[0-9]+\Z")
BASE_OPS = {"ADD", "CMP", "JMP", "PRN", "SET"}
ALL_OPS = BASE_OPS | {"SUB", "BAK", "CAL", "RET"}


@dataclass(frozen=True)
class Instruction:
    opcode: str
    alpha: str
    beta: str


def parse_program(text: str) -> list[Instruction]:
    instructions: list[Instruction] = []
    for line_no, raw in enumerate(text.splitlines(), 1):
        fields = raw.split()
        if len(fields) != 3:
            raise ValueError(f"line {line_no}: expected exactly 3 fields")
        opcode, alpha, beta = fields
        if opcode not in ALL_OPS:
            raise ValueError(f"line {line_no}: unknown opcode {opcode!r}")
        for operand in (alpha, beta):
            if not (INTEGER_RE.fullmatch(operand) or VARIABLE_RE.fullmatch(operand)):
                raise ValueError(f"line {line_no}: invalid operand {operand!r}")
        if opcode == "ADD" and not VARIABLE_RE.fullmatch(beta):
            raise ValueError(f"line {line_no}: ADD destination must be a variable")
        if opcode == "SET" and not VARIABLE_RE.fullmatch(alpha):
            raise ValueError(f"line {line_no}: SET destination must be a variable")
        instructions.append(Instruction(opcode, alpha, beta))
    if not instructions:
        raise ValueError("empty program")
    return instructions


def load_program(path: Path) -> list[Instruction]:
    return parse_program(path.read_text(encoding="ascii"))


def first_operands(program: list[Instruction]) -> list[str]:
    return [instruction.alpha for instruction in program]


class VM:
    """Execute valid L code using current-instruction-relative jumps."""

    def __init__(self, program: list[Instruction], *, max_steps: int = 1_000_000):
        self.program = program
        self.max_steps = max_steps
        self.pc = 0
        self.steps = 0
        self.env: dict[str, int] = {}
        self.sub_returns: list[int] = []
        self.function_returns: list[tuple[int, dict[str, int], int]] = []

    def value(self, token: str) -> int:
        if INTEGER_RE.fullmatch(token):
            return int(token)
        if token not in self.env:
            raise ValueError(f"variable {token!r} read before assignment at line {self.pc}")
        return self.env[token]

    def run(self) -> tuple[int, int]:
        while 0 <= self.pc < len(self.program):
            self.steps += 1
            if self.steps > self.max_steps:
                raise RuntimeError("step limit exceeded")

            ins = self.program[self.pc]
            op, a, b = ins.opcode, ins.alpha, ins.beta

            if op == "SET":
                self.env[a] = self.value(b)
                self.pc += 1
            elif op == "ADD":
                self.env[b] = self.value(a) + self.value(b)
                self.pc += 1
            elif op == "CMP":
                self.pc += 2 if self.value(a) == self.value(b) else 1
            elif op == "JMP":
                self.pc += self.value(a)
            elif op == "PRN":
                return self.value(a), self.value(b)
            elif op == "SUB":
                offset = self.value(a)
                self.sub_returns.append(self.pc + 1)
                self.pc += offset
            elif op == "BAK":
                if not self.sub_returns:
                    raise ValueError(f"BAK without SUB at line {self.pc}")
                self.pc = self.sub_returns.pop()
            elif op == "CAL":
                offset = self.value(a)
                argument = self.value(b)
                self.function_returns.append((self.pc + 1, self.env, len(self.sub_returns)))
                self.env = {"in": argument}
                self.pc += offset
            elif op == "RET":
                result = self.value(a)
                if not self.function_returns:
                    raise ValueError(f"RET without CAL at line {self.pc}")
                return_pc, caller_env, saved_sub_depth = self.function_returns.pop()
                if len(self.sub_returns) != saved_sub_depth:
                    raise ValueError("function returned with an unfinished SUB call")
                self.env = caller_env
                self.env["out"] = result
                self.pc = return_pc
            else:  # pragma: no cover - parse_program prevents this
                raise AssertionError(op)

        raise ValueError(f"program counter left the program at {self.pc} without PRN")


def execute_text(text: str, *, max_steps: int = 1_000_000) -> tuple[int, int]:
    return VM(parse_program(text), max_steps=max_steps).run()
