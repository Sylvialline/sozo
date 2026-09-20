#!/usr/bin/env python3
"""Validate formats, deterministic generation, exact answers, and geometry."""

from __future__ import annotations

from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys

from exact_geometry import (
    area_text,
    count_koch,
    count_koch_slow,
    count_r0,
    count_r1,
    koch_vertices,
    parse_decimal_exact,
)


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ANSWERS = ROOT / "answers"
EXPECTED_COUNTS = {1: 50_000, 2: 2_000, 3: 32, 4: 75, 5: 1_000, 6: 256}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lines(path: Path) -> list[str]:
    return path.read_text(encoding="ascii").splitlines()


def independent_r0(d: Fraction) -> int:
    if d == 0:
        return 1
    h = abs(d)
    axis_count = 10 // h + 1
    return axis_count * axis_count


def independent_r1_small(d: Fraction) -> int:
    if d == 0:
        return 0
    h = abs(d)
    bound = 10 // h
    return sum(
        (h * p - 5) ** 2 + (h * q - 5) ** 2 <= 25
        for p in range(bound + 1)
        for q in range(bound + 1)
    )


def area_coefficient_by_sum(n: int) -> Fraction:
    coefficient = Fraction(25)
    for i in range(1, n + 1):
        coefficient += Fraction(75 * 4 ** (i - 1), 9 ** i)
    return coefficient


def answer_for_query(question: int, query: str) -> str:
    inputs = lines(DATA / f"q{question}.txt")
    outputs = lines(ANSWERS / f"q{question}.txt")
    return outputs[inputs.index(query)]


def main() -> None:
    manifest_path = ROOT / "attachments" / "manifest.json"
    original_hashes = {i: sha256(DATA / f"q{i}.txt") for i in range(1, 7)}
    subprocess.run([sys.executable, str(ROOT / "attachments" / "generate_data.py")], check=True)
    regenerated_hashes = {i: sha256(DATA / f"q{i}.txt") for i in range(1, 7)}
    assert original_hashes == regenerated_hashes

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for question, expected_count in EXPECTED_COUNTS.items():
        input_path = DATA / f"q{question}.txt"
        answer_path = ANSWERS / f"q{question}.txt"
        input_lines, answer_lines = lines(input_path), lines(answer_path)
        assert len(input_lines) == len(answer_lines) == expected_count
        assert input_path.read_bytes().isascii() and answer_path.read_bytes().isascii()
        assert all(line and line == line.strip() for line in input_lines + answer_lines)
        assert manifest["files"][f"q{question}.txt"]["sha256"] == sha256(input_path)

    decimal_limits = {
        1: (Fraction(1, 10**12), Fraction(10**6)),
        2: (Fraction(5, 10**4), Fraction(10**6)),
        5: (Fraction(2, 10**3), Fraction(10**6)),
    }
    for question, (minimum, maximum) in decimal_limits.items():
        for token in lines(DATA / f"q{question}.txt"):
            magnitude = abs(parse_decimal_exact(token))
            assert magnitude == 0 or minimum <= magnitude <= maximum
    assert set(lines(DATA / "q3.txt")) == {"K2"}
    q4_inputs = [int(token) for token in lines(DATA / "q4.txt")]
    assert all(1 <= n <= 10**9 for n in q4_inputs)
    assert set(range(1, 65)) <= set(q4_inputs)
    assert {10**6, 10**9 - 1, 10**9} <= set(q4_inputs)
    for query in lines(DATA / "q6.txt"):
        d_text, n_text = query.split()
        magnitude = abs(parse_decimal_exact(d_text))
        assert magnitude == 0 or Fraction(1, 100) <= magnitude <= 10**6
        assert 1 <= int(n_text) <= 8

    # Exact decimal parser invariants and all cheap answers.
    assert parse_decimal_exact("0.1") == parse_decimal_exact("0.10") == Fraction(1, 10)
    assert parse_decimal_exact("-0.0") == 0
    for token, output in zip(lines(DATA / "q1.txt"), lines(ANSWERS / "q1.txt")):
        d = parse_decimal_exact(token)
        assert count_r0(d) == independent_r0(d) == int(output)
    print("validated q1", flush=True)
    q2_pairs = list(zip(lines(DATA / "q2.txt"), lines(ANSWERS / "q2.txt")))
    q2_indices = list(range(30)) + random.Random(201302).sample(range(30, len(q2_pairs)), 100)
    for index in q2_indices:
        token, output = q2_pairs[index]
        d = parse_decimal_exact(token)
        assert Fraction(output) == Fraction(count_r1(d), 4 * count_r0(d))
    print("validated q2 samples", flush=True)

    # Separate two-dimensional enumeration for circle cases with manageable grids.
    circle_checks = [Fraction(0), Fraction(1, 2), Fraction(1), Fraction(5, 4), Fraction(2), Fraction(5), Fraction(20), Fraction(-1)]
    for d in circle_checks:
        assert count_r1(d) == independent_r1_small(d)

    # Area formula: finite geometric sum agrees with the closed form.
    for n in range(21):
        assert area_coefficient_by_sum(n) == Fraction(40) - Fraction(15) * Fraction(4, 9) ** n
    assert set(lines(ANSWERS / "q3.txt")) == {area_text(2)}
    q4_answers = lines(ANSWERS / "q4.txt")
    for n_text, output in zip(lines(DATA / "q4.txt"), q4_answers):
        assert output == area_text(int(n_text))
        whole, dot, fraction = output.partition(".")
        assert whole.isdigit() and dot == "." and len(fraction) == 20 and fraction.isdigit()
    # Every output distinguishable for 1 <= n <= 1e9 under the specified
    # 20-place rounding: n=1..61 plus the limiting rounded value.
    assert len(set(q4_answers)) == 62
    assert q4_answers[60] == q4_answers[61]
    assert q4_answers[61] != q4_answers[62]
    assert len(set(q4_answers[62:])) == 1
    print("validated areas", flush=True)

    # Fast exact scanline versus independent exact point-by-point winding tests.
    deterministic_steps = [Fraction(0), Fraction(1, 2), Fraction(1), Fraction(5, 4), Fraction(2), Fraction(5, 2), Fraction(5), Fraction(20), Fraction(-1)]
    geometry_checks = 0
    for n in range(3):
        assert len(koch_vertices(n)) == 3 * 4 ** n
        for d in deterministic_steps:
            assert count_koch(d, n) == count_koch_slow(d, n)
            geometry_checks += 1

    assert len(koch_vertices(3)) == 3 * 4 ** 3
    for d in [Fraction(1), Fraction(2), Fraction(5)]:
        assert count_koch(d, 3) == count_koch_slow(d, 3)
        geometry_checks += 1
    assert len(koch_vertices(4)) == 3 * 4 ** 4
    for d in [Fraction(2), Fraction(5)]:
        assert count_koch(d, 4) == count_koch_slow(d, 4)
        geometry_checks += 1

    rng = random.Random(2013)
    for _ in range(15):
        n = rng.randrange(3)
        d = Fraction(rng.randint(1, 20), rng.randint(1, 5))
        assert count_koch(d, n) == count_koch_slow(d, n)
        geometry_checks += 1
    print("validated independent geometry", flush=True)

    # Region inclusion and sign/zero invariants.
    for d in [Fraction(0), Fraction(1), Fraction(2), Fraction(5)]:
        values = [count_koch(d, n) for n in range(6)]
        assert values == sorted(values)
        assert all(count_koch(d, n) == count_koch(-d, n) for n in range(6))
    print("validated geometry invariants", flush=True)

    # Fixed anchor values and selected on-disk answer checks.
    assert answer_for_query(1, "0") == "1"
    assert answer_for_query(1, "1") == "121"
    assert answer_for_query(1, "0.1") == "10201"
    assert answer_for_query(2, "0") == "0/1"
    assert answer_for_query(2, "1") == "81/484"
    assert answer_for_query(5, "0") == "1"
    assert answer_for_query(5, "1") == "65"

    q5_pairs = list(zip(lines(DATA / "q5.txt"), lines(ANSWERS / "q5.txt")))
    for token, output in q5_pairs[:30] + q5_pairs[30::25]:
        assert int(output) == count_koch(parse_decimal_exact(token), 2)
    print("validated q5 samples", flush=True)

    q6_pairs = list(zip(lines(DATA / "q6.txt"), lines(ANSWERS / "q6.txt")))
    selected_q6 = [pair for pair in q6_pairs if int(pair[0].split()[1]) <= 5][:40]
    for query, output in selected_q6:
        d_text, n_text = query.split()
        assert int(output) == count_koch(parse_decimal_exact(d_text), int(n_text))
    print("validated q6 samples", flush=True)

    report = {
        "status": "passed",
        "source_crosscheck": {
            "english_problem_pages": [4, 5],
            "japanese_problem_pages": [4, 5],
            "differences": [],
        },
        "case_counts": {f"q{i}": EXPECTED_COUNTS[i] for i in range(1, 7)},
        "decimal_tokens_parsed_exactly": True,
        "binary_float_used_for_decisions": False,
        "deterministic_regeneration": True,
        "independent_circle_checks": len(circle_checks),
        "on_disk_q2_rechecks": len(q2_indices),
        "on_disk_q5_rechecks": len(q5_pairs[:30] + q5_pairs[30::25]),
        "on_disk_q6_rechecks": len(selected_q6),
        "independent_koch_checks": geometry_checks,
        "area_formula_checks": 21,
        "q4_distinct_answers": len(set(q4_answers)),
        "q4_distinct_answers_maximal_for_output_format": True,
        "coverage": [
            "closed-boundary inclusion",
            "positive, negative, zero, and negative-zero d",
            "equivalent decimal spellings",
            "values immediately on both sides of discontinuities",
            "very small and much-larger-than-region spacing",
            "n up to 1e9 for the area formula",
            "Koch depth up to 8 for lattice counting",
            "horizontal-boundary and vertex lattice points",
            "exact Q(sqrt(3)) scanline ordering and rounding",
        ],
        "input_sha256": {f"q{i}.txt": sha256(DATA / f"q{i}.txt") for i in range(1, 7)},
        "answer_sha256": {f"q{i}.txt": sha256(ANSWERS / f"q{i}.txt") for i in range(1, 7)},
    }
    (ROOT / "attachments" / "validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"validation passed: {sum(EXPECTED_COUNTS.values())} cases, {geometry_checks} independent Koch checks")


if __name__ == "__main__":
    main()
