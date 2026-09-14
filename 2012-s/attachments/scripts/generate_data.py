#!/usr/bin/env python3
"""Deterministically generate the five exam data files and regression cases."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TEST_PROGRAMS = ROOT / "tests" / "programs"


MAIN_PROGRAMS: dict[str, list[str]] = {
    "prog1.txt": [
        "SET x -12",
        "SET y 5",
        "ADD 7 x",
        "ADD x y",
        "CMP y 12",
        "JMP -3 0",
        "CMP -7 x",
        "JMP 2 y",
        "SET x x",
        "ADD -1000000 y",
        "CMP 0 0",
        "JMP 2 -999",
        "SET y 777",
        "PRN x y",
    ],
    "prog2.txt": [
        "SET x -17",
        "SET y 5",
        "ADD x y",
        "ADD y y",
        "SET x y",
        "ADD 100 x",
        "ADD x x",
        "ADD -2 y",
        "ADD y x",
        "SET y x",
        "ADD -126 y",
        "PRN x y",
    ],
    "prog3.txt": [
        "SET count 7",
        "SET total 0",
        "ADD count total",
        "ADD -1 count",
        "CMP count 0",
        "JMP -3 ignored",
        "CMP 5 5",
        "PRN -999 -999",
        "SET jump 2",
        "JMP jump unused",
        "PRN -888 -888",
        "CMP total 28",
        "PRN -777 -777",
        "SET delta -8",
        "ADD delta total",
        "SET copy total",
        "ADD copy copy",
        "CMP copy total",
        "ADD 2 total",
        "CMP copy 40",
        "ADD 1000 total",
        "PRN total copy",
    ],
    "prog4.txt": [
        "JMP 9 0",
        "CMP n 0",
        "JMP 2 0",
        "BAK 123 x",
        "ADD n total",
        "ADD -1 n",
        "SUB -5 ignored",
        "ADD 1 unwind",
        "BAK y -999",
        "SET n 8",
        "SET total 0",
        "SET unwind 0",
        "SET entry -12",
        "SUB entry 314",
        "ADD unwind total",
        "ADD 100 total",
        "PRN n total",
    ],
    "prog5.txt": [
        "SET saved 1000",
        "SET arg 2000",
        "SET first 3000",
        "SET n 8",
        "CAL 5 n",
        "SET result out",
        "ADD saved result",
        "ADD arg result",
        "PRN first result",
        "CMP in 0",
        "JMP 2 unused",
        "RET 0 -999",
        "CMP in 1",
        "JMP 2 unused",
        "RET 1 -999",
        "SET saved in",
        "SET arg in",
        "ADD -1 arg",
        "CAL -9 arg",
        "SET first out",
        "SET arg saved",
        "ADD -2 arg",
        "CAL -13 arg",
        "ADD out first",
        "RET first -999",
    ],
}


REGRESSION_CASES: dict[str, dict[str, object]] = {
    "01_add_alias": {
        "stage": 3,
        "expected": [12, -2],
        "lines": ["SET x 7", "SET y -2", "ADD x x", "ADD y x", "PRN x y"],
    },
    "02_cmp_true_skip": {
        "stage": 4,
        "expected": [5, 0],
        "lines": ["SET a 5", "CMP a 5", "PRN 999 999", "PRN a 0"],
    },
    "03_cmp_false": {
        "stage": 4,
        "expected": [7, 0],
        "lines": ["SET a 4", "CMP a 5", "ADD 3 a", "PRN a 0"],
    },
    "04_jump_from_current": {
        "stage": 4,
        "expected": [4, 0],
        "lines": [
            "SET a 0", "ADD 1 a", "CMP a 4", "JMP -2 0", "PRN a 0"
        ],
    },
    "05_jump_variable_offset": {
        "stage": 4,
        "expected": [7, 8],
        "lines": ["SET off 2", "JMP off 0", "PRN 999 999", "PRN 7 8"],
    },
    "06_sub_nested": {
        "stage": 5,
        "expected": [111, 0],
        "lines": [
            "JMP 8 0", "ADD 1 x", "SUB 3 0", "ADD 100 x", "BAK 0 0",
            "ADD 10 x", "BAK 0 0", "JMP 0 0", "SET x 0", "SUB -8 0",
            "PRN x 0",
        ],
    },
    "07_sub_recursive": {
        "stage": 5,
        "expected": [0, 20],
        "lines": [
            "JMP 9 0", "CMP n 0", "JMP 2 0", "BAK 0 0", "ADD n sum",
            "ADD -1 n", "SUB -5 0", "ADD 1 unwind", "BAK 0 0", "SET n 5",
            "SET sum 0", "SET unwind 0", "SUB -11 0", "ADD unwind sum",
            "PRN n sum",
        ],
    },
    "08_cal_literal_argument": {
        "stage": 6,
        "expected": [3, 0],
        "lines": [
            "CAL 3 -7", "PRN out 0", "JMP 0 0", "SET value in",
            "ADD 10 value", "RET value 0",
        ],
    },
    "09_cal_local_shadow": {
        "stage": 6,
        "expected": [99, 7],
        "lines": [
            "SET a 99", "CAL 3 1", "PRN a out", "JMP 0 0", "SET a 7", "RET a 0",
        ],
    },
    "10_cal_variable_offset": {
        "stage": 6,
        "expected": [7, 5],
        "lines": [
            "SET target 4", "SET arg 5", "CAL target arg", "PRN out arg",
            "JMP 0 0", "JMP 0 0", "SET value in", "ADD 2 value", "RET value 0",
        ],
    },
    "11_ret_literal_negative": {
        "stage": 6,
        "expected": [-123, 0],
        "lines": ["CAL 3 0", "PRN out 0", "JMP 0 0", "RET -123 ignored"],
    },
    "12_recursive_fibonacci": {
        "stage": 6,
        "expected": [3000, 3021],
        "lines": MAIN_PROGRAMS["prog5.txt"],
    },
}


def write_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="ascii", newline="\n")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    TEST_PROGRAMS.mkdir(parents=True, exist_ok=True)
    for name, lines in MAIN_PROGRAMS.items():
        write_lines(DATA / name, lines)
    for name, case in REGRESSION_CASES.items():
        write_lines(TEST_PROGRAMS / f"{name}.txt", case["lines"])

    manifest = {
        "generator": "scripts/generate_data.py",
        "deterministic": True,
        "bilingual_constraint_resolution": {
            "english": "less than 100 lines",
            "japanese": "at most 100 lines",
            "applied": "all programs have fewer than 100 lines",
        },
        "main_files": {
            name: {"lines": len(lines), "sha256": sha256(DATA / name)}
            for name, lines in MAIN_PROGRAMS.items()
        },
        "regression_cases": {
            name: {
                "stage": case["stage"],
                "expected": case["expected"],
                "lines": len(case["lines"]),
                "sha256": sha256(TEST_PROGRAMS / f"{name}.txt"),
            }
            for name, case in REGRESSION_CASES.items()
        },
    }
    (ROOT / "generation_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
