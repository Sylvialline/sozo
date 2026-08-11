from __future__ import annotations

import json
import random
import sys
import unittest
from decimal import Decimal, ROUND_HALF_UP, localcontext
from fractions import Fraction
from itertools import combinations
from pathlib import Path

sys.dont_write_bytecode = True

from reference_solver import (
    _format_fraction,
    difference_sequence,
    fastest_exponential_windows,
    linear_fit,
    maximum_increment_periods,
    most_similar_file_pairs,
    parse_series,
    seven_day_statistics,
    similarity_score,
    tenth_largest_distinct,
)


def brute_maximum_increment_periods(values: list[int]) -> dict[str, object]:
    previous = 0
    differences = []
    for value in values:
        differences.append(value - previous)
        previous = value

    candidates = []
    for start in range(len(differences)):
        running = 0
        for end in range(start, len(differences)):
            running += differences[end]
            candidates.append((running, end - start + 1, start + 1, end + 1))
    maximum_sum = max(item[0] for item in candidates)
    shortest_length = min(item[1] for item in candidates if item[0] == maximum_sum)
    periods = [
        {"start_day": start, "end_day": end}
        for total, length, start, end in candidates
        if total == maximum_sum and length == shortest_length
    ]
    periods.sort(key=lambda period: (period["end_day"], period["start_day"]))
    return {
        "maximum_sum": maximum_sum,
        "shortest_length": shortest_length,
        "periods": periods,
    }


def independent_format_fraction(value: Fraction) -> str:
    quotient, remainder = divmod(abs(value.numerator) * 10_000, value.denominator)
    if remainder * 2 >= value.denominator:
        quotient += 1
    sign = "-" if value < 0 and quotient else ""
    integer, fractional = divmod(quotient, 10_000)
    return f"{sign}{integer}.{fractional:04d}"


def independent_format_decimal(value: Decimal) -> str:
    with localcontext() as context:
        context.prec = 80
        rounded = value.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    if rounded == 0:
        rounded = abs(rounded)
    return format(rounded, ".4f")


def independent_similarity(first: list[int], second: list[int]) -> int:
    if len(first) < len(second):
        first, second = second, first
    errors = []
    for offset in range(len(first) - len(second) + 1):
        errors.append(
            sum((first[offset + index] - value) ** 2 for index, value in enumerate(second))
        )
    return -min(errors)


def independently_solve_delivery() -> dict[str, object]:
    attachments = Path(__file__).resolve().parent
    data_dir = attachments.parent
    series = {
        path.name: [int(field) for field in path.read_text(encoding="utf-8").strip().split(":")]
        for path in sorted(data_dir.glob("*.txt"), key=lambda item: item.name)
    }
    infections = series["infections.txt"]
    infections2 = series["infections2.txt"]

    per_file = {
        name: sorted(set(values), reverse=True)[9]
        for name, values in series.items()
    }

    differences = []
    previous = 0
    for value in infections:
        differences.append(value - previous)
        previous = value
    encoded = "".join(("+" if value >= 0 else "") + str(value) for value in differences)

    window_sums = [sum(infections[start : start + 7]) for start in range(len(infections) - 6)]
    seven_day = {
        "maximum": independent_format_fraction(Fraction(max(window_sums), 7)),
        "minimum": independent_format_fraction(Fraction(min(window_sums), 7)),
        "sum": independent_format_fraction(Fraction(sum(window_sums), 7)),
    }

    best_similarity = None
    best_pairs = []
    for first_name, second_name in combinations(sorted(series), 2):
        score = independent_similarity(series[first_name], series[second_name])
        if best_similarity is None or score > best_similarity:
            best_similarity = score
            best_pairs = [[first_name, second_name]]
        elif score == best_similarity:
            best_pairs.append([first_name, second_name])
    assert best_similarity is not None

    count = len(infections2)
    sum_i = sum(range(count))
    sum_i_squared = sum(index * index for index in range(count))
    sum_x = sum(infections2)
    sum_ix = sum(index * value for index, value in enumerate(infections2))
    denominator = count * sum_i_squared - sum_i * sum_i
    linear_a = Fraction(count * sum_ix - sum_i * sum_x, denominator)
    linear_k = Fraction(sum_i_squared * sum_x - sum_ix * sum_i, denominator)

    exponential_candidates = []
    for start in range(len(infections2) - 30):
        window = infections2[start : start + 31]
        numerator = 1
        denominator_product = 1
        for index, value in enumerate(window):
            centered = index - 15
            if centered > 0:
                numerator *= (value + 1) ** centered
            elif centered < 0:
                denominator_product *= (value + 1) ** (-centered)
        exponential_candidates.append((start, Fraction(numerator, denominator_product), window))
    maximum_metric = max(metric for _, metric, _ in exponential_candidates)
    exponential_solutions = []
    for start, metric, window in exponential_candidates:
        if metric != maximum_metric:
            continue
        with localcontext() as context:
            context.prec = 80
            logs = [Decimal(value + 1).ln() for value in window]
            slope = sum(
                (Decimal(index - 15) * value for index, value in enumerate(logs)),
                Decimal(0),
            ) / Decimal(2480)
            intercept = sum(logs, Decimal(0)) / Decimal(31) - Decimal(15) * slope
            exponential_solutions.append(
                {
                    "s": start,
                    "a": independent_format_decimal(slope.exp()),
                    "k": independent_format_decimal(intercept.exp()),
                }
            )

    return {
        "1.1": {"tenth_largest_distinct": sorted(set(infections), reverse=True)[9]},
        "1.2": {"sum": sum(per_file.values()), "per_file": per_file},
        "1.3": {"sequence": encoded, "character_count": len(encoded)},
        "1.4": brute_maximum_increment_periods(infections),
        "2.1": seven_day,
        "2.2": {"maximum_score": best_similarity, "pairs": best_pairs},
        "2.3": {
            "a": independent_format_fraction(linear_a),
            "k": independent_format_fraction(linear_k),
        },
        "2.4": {"window_length": 31, "solutions": exponential_solutions},
    }


class ReferenceSolverTests(unittest.TestCase):
    def test_delivery_answers_with_independent_oracles(self) -> None:
        attachments = Path(__file__).resolve().parent
        stored = json.loads((attachments / "answers.json").read_text(encoding="utf-8"))
        self.assertEqual(independently_solve_delivery(), stored)

    def test_parser_and_tenth_distinct(self) -> None:
        values = parse_series("9:0:10:9:100:8:7:6:5:4:3:2:1\n")
        self.assertEqual(tenth_largest_distinct(values), 2)
        for invalid in ("", "1::2", "1:-2", "1: 2", "1:two"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                parse_series(invalid)

    def test_difference_encoding_includes_plus_for_zero(self) -> None:
        self.assertEqual(difference_sequence([621, 591, 591, 275, 489, 400]), "+621-30+0-316+214-89")

    def test_maximum_period_fixed_ties(self) -> None:
        self.assertEqual(
            maximum_increment_periods([0, 5, 10, 0, 5, 10]),
            {
                "maximum_sum": 10,
                "shortest_length": 2,
                "periods": [
                    {"start_day": 2, "end_day": 3},
                    {"start_day": 5, "end_day": 6},
                ],
            },
        )
        self.assertEqual(len(maximum_increment_periods([0, 0, 0])["periods"]), 3)

    def test_maximum_period_random_against_quadratic_brute_force(self) -> None:
        rng = random.Random(202108)
        for length in range(1, 13):
            for _ in range(80):
                values = [rng.randrange(21) for _ in range(length)]
                with self.subTest(values=values):
                    self.assertEqual(
                        maximum_increment_periods(values),
                        brute_maximum_increment_periods(values),
                    )

    def test_exact_rounding_and_seven_day_statistics(self) -> None:
        self.assertEqual(_format_fraction(Fraction(-1, 6)), "-0.1667")
        self.assertEqual(
            seven_day_statistics(list(range(1, 9))),
            {"maximum": "5.0000", "minimum": "4.0000", "sum": "9.0000"},
        )

    def test_similarity_alignment_and_all_tied_pairs(self) -> None:
        self.assertEqual(similarity_score([9, 1, 2, 3, 8], [1, 2, 4]), -1)
        series = {
            "long_a.txt": [8, 1, 2, 3, 9],
            "long_b.txt": [7, 7, 1, 2, 3, 6],
            "short.txt": [1, 2, 3],
        }
        self.assertEqual(
            most_similar_file_pairs(series),
            {
                "maximum_score": 0,
                "pairs": [
                    ["long_a.txt", "short.txt"],
                    ["long_b.txt", "short.txt"],
                ],
            },
        )

    def test_exact_linear_fit(self) -> None:
        self.assertEqual(linear_fit([5, 8, 11, 14, 17]), {"a": "3.0000", "k": "5.0000"})

    def test_exponential_fit_and_all_window_starts(self) -> None:
        geometric = [3 * 2**index - 1 for index in range(31)]
        self.assertEqual(
            fastest_exponential_windows(geometric),
            {
                "window_length": 31,
                "solutions": [{"s": 0, "a": "2.0000", "k": "3.0000"}],
            },
        )
        constant = fastest_exponential_windows([0] * 33)
        self.assertEqual(
            constant["solutions"],
            [
                {"s": 0, "a": "1.0000", "k": "1.0000"},
                {"s": 1, "a": "1.0000", "k": "1.0000"},
                {"s": 2, "a": "1.0000", "k": "1.0000"},
            ],
        )


if __name__ == "__main__":
    unittest.main()
