from __future__ import annotations

import argparse
import json
from decimal import Decimal, ROUND_HALF_UP, localcontext
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Iterable, Mapping, Sequence


ATTACHMENTS_DIR = Path(__file__).resolve().parent
DATA_DIR = ATTACHMENTS_DIR.parent

EXPECTED_DATA_FILES = (
    "baseline.txt",
    "echo_long_a.txt",
    "echo_long_b.txt",
    "echo_short.txt",
    "infections.txt",
    "infections2.txt",
    "plateau.txt",
    "sawtooth.txt",
)


def parse_series(text: str) -> list[int]:
    """Parse one colon-separated sequence of non-negative integers."""
    stripped = text.strip()
    if not stripped:
        raise ValueError("the infection sequence must not be empty")

    fields = stripped.split(":")
    if any(not field or not field.isascii() or not field.isdecimal() for field in fields):
        raise ValueError("expected colon-separated non-negative decimal integers")

    values = [int(field) for field in fields]
    if any(value < 0 for value in values):
        raise ValueError("infection counts must be non-negative")
    return values


def read_series(path: Path) -> list[int]:
    return parse_series(path.read_text(encoding="utf-8"))


def load_data(data_dir: Path = DATA_DIR) -> dict[str, list[int]]:
    paths = sorted(data_dir.glob("*.txt"), key=lambda path: path.name)
    if not paths:
        raise ValueError(f"no input text files found in {data_dir}")
    return {path.name: read_series(path) for path in paths}


def tenth_largest_distinct(values: Iterable[int]) -> int:
    distinct = sorted(set(values), reverse=True)
    if len(distinct) < 10:
        raise ValueError("at least 10 distinct infection counts are required")
    return distinct[9]


def new_infection_differences(values: Sequence[int]) -> list[int]:
    previous = 0
    differences: list[int] = []
    for value in values:
        differences.append(value - previous)
        previous = value
    return differences


def difference_sequence(values: Sequence[int]) -> str:
    return "".join(f"{difference:+d}" for difference in new_infection_differences(values))


def maximum_increment_periods(values: Sequence[int]) -> dict[str, object]:
    """Find every shortest non-empty period attaining the maximum increment sum."""
    if not values:
        raise ValueError("the infection sequence must not be empty")

    prefix = 0
    minimum_prefix = 0
    latest_minimum_index = 0
    best_sum: int | None = None
    best_length: int | None = None
    periods: list[dict[str, int]] = []

    for end_day, difference in enumerate(new_infection_differences(values), start=1):
        prefix += difference
        candidate_sum = prefix - minimum_prefix
        candidate_length = end_day - latest_minimum_index
        candidate = {
            "start_day": latest_minimum_index + 1,
            "end_day": end_day,
        }

        if best_sum is None or candidate_sum > best_sum:
            best_sum = candidate_sum
            best_length = candidate_length
            periods = [candidate]
        elif candidate_sum == best_sum:
            if best_length is None or candidate_length < best_length:
                best_length = candidate_length
                periods = [candidate]
            elif candidate_length == best_length:
                periods.append(candidate)

        # Equal minima use the latest index because only shortest maximum-sum
        # periods are required.
        if prefix <= minimum_prefix:
            minimum_prefix = prefix
            latest_minimum_index = end_day

    assert best_sum is not None and best_length is not None
    return {
        "maximum_sum": best_sum,
        "shortest_length": best_length,
        "periods": periods,
    }


def _format_fraction(value: Fraction, places: int = 4) -> str:
    scale = 10**places
    numerator = value.numerator
    denominator = value.denominator
    quotient, remainder = divmod(abs(numerator) * scale, denominator)
    if remainder * 2 >= denominator:
        quotient += 1

    if quotient == 0:
        sign = ""
    else:
        sign = "-" if numerator < 0 else ""
    integer, fractional = divmod(quotient, scale)
    return f"{sign}{integer}.{fractional:0{places}d}"


def _format_decimal(value: Decimal, places: int = 4) -> str:
    quantum = Decimal(1).scaleb(-places)
    with localcontext() as context:
        context.prec = max(80, len(value.as_tuple().digits) + places + 8)
        rounded = value.quantize(quantum, rounding=ROUND_HALF_UP)
    if rounded == 0:
        rounded = abs(rounded)
    return format(rounded, f".{places}f")


def seven_day_statistics(values: Sequence[int]) -> dict[str, str]:
    if len(values) < 7:
        raise ValueError("at least 7 days are required for seven-day averages")

    window_sum = sum(values[:7])
    averages = [Fraction(window_sum, 7)]
    for right in range(7, len(values)):
        window_sum += values[right] - values[right - 7]
        averages.append(Fraction(window_sum, 7))

    return {
        "maximum": _format_fraction(max(averages)),
        "minimum": _format_fraction(min(averages)),
        "sum": _format_fraction(sum(averages, Fraction(0))),
    }


def similarity_score(first: Sequence[int], second: Sequence[int]) -> int:
    """Return the score from Problem 2(2) for two sequences."""
    longer, shorter = (first, second) if len(first) >= len(second) else (second, first)
    if not shorter:
        raise ValueError("similarity is undefined for an empty sequence")

    shortest_error: int | None = None
    for offset in range(len(longer) - len(shorter) + 1):
        error = sum(
            (longer[offset + index] - value) ** 2
            for index, value in enumerate(shorter)
        )
        if shortest_error is None or error < shortest_error:
            shortest_error = error

    assert shortest_error is not None
    return -shortest_error


def most_similar_file_pairs(series: Mapping[str, Sequence[int]]) -> dict[str, object]:
    if len(series) < 2:
        raise ValueError("at least two files are required")

    best_score: int | None = None
    best_pairs: list[list[str]] = []
    for first_name, second_name in combinations(sorted(series), 2):
        score = similarity_score(series[first_name], series[second_name])
        pair = [first_name, second_name]
        if best_score is None or score > best_score:
            best_score = score
            best_pairs = [pair]
        elif score == best_score:
            best_pairs.append(pair)

    assert best_score is not None
    return {
        "maximum_score": best_score,
        "pairs": best_pairs,
    }


def linear_fit(values: Sequence[int]) -> dict[str, str]:
    """Fit a*i + k by ordinary least squares, using exact rational arithmetic."""
    count = len(values)
    if count < 2:
        raise ValueError("at least two values are required for a linear fit")

    sum_i = count * (count - 1) // 2
    sum_i_squared = count * (count - 1) * (2 * count - 1) // 6
    sum_x = sum(values)
    sum_ix = sum(index * value for index, value in enumerate(values))
    denominator = count * sum_i_squared - sum_i * sum_i
    if denominator == 0:
        raise ValueError("the linear-fit denominator is zero")

    a = Fraction(count * sum_ix - sum_i * sum_x, denominator)
    k = Fraction(sum_i_squared * sum_x - sum_ix * sum_i, denominator)
    return {
        "a": _format_fraction(a),
        "k": _format_fraction(k),
    }


def _exponential_fit_decimal(values: Sequence[int]) -> tuple[Decimal, Decimal]:
    """Return (a, k) for k*a**i fitted to x_i+1 in log space."""
    count = len(values)
    if count < 2:
        raise ValueError("at least two values are required for an exponential fit")
    if any(value < 0 for value in values):
        raise ValueError("log(x + 1) requires non-negative infection counts")

    sum_i = Decimal(count * (count - 1) // 2)
    sum_i_squared = Decimal(count * (count - 1) * (2 * count - 1) // 6)
    count_decimal = Decimal(count)
    denominator = count_decimal * sum_i_squared - sum_i * sum_i

    with localcontext() as context:
        context.prec = 80
        logs = [Decimal(value + 1).ln() for value in values]
        sum_y = sum(logs, Decimal(0))
        sum_iy = sum(
            (Decimal(index) * value for index, value in enumerate(logs)),
            Decimal(0),
        )
        slope = (count_decimal * sum_iy - sum_i * sum_y) / denominator
        intercept = (sum_y - slope * sum_i) / count_decimal
        return +slope.exp(), +intercept.exp()


def _exponential_growth_metric(values: Sequence[int]) -> Fraction:
    """Compare fitted growth factors exactly, without logarithmic roundoff.

    For 31 points, the fitted log-slope is proportional to
    sum((i - 15) * log(x_i + 1)).  Exponentiating that numerator gives the
    rational product below, so Fraction ordering is exactly the ordering of a.
    """
    if len(values) != 31:
        raise ValueError("the exact growth metric expects 31 values")

    numerator = 1
    denominator = 1
    for index, value in enumerate(values):
        weight = index - 15
        if weight > 0:
            numerator *= (value + 1) ** weight
        elif weight < 0:
            denominator *= (value + 1) ** (-weight)
    return Fraction(numerator, denominator)


def fastest_exponential_windows(
    values: Sequence[int],
    window_length: int = 31,
) -> dict[str, object]:
    if len(values) < window_length:
        raise ValueError(f"at least {window_length} values are required")

    candidates: list[tuple[int, Fraction, Decimal, Decimal]] = []
    for start in range(len(values) - window_length + 1):
        window = values[start : start + window_length]
        a, k = _exponential_fit_decimal(window)
        metric = _exponential_growth_metric(window)
        candidates.append((start, metric, a, k))

    maximum_metric = max(metric for _, metric, _, _ in candidates)
    solutions = [
        {
            "s": start,
            "a": _format_decimal(a),
            "k": _format_decimal(k),
        }
        for start, metric, a, k in candidates
        if metric == maximum_metric
    ]
    return {
        "window_length": window_length,
        "solutions": solutions,
    }


def solve_all(data_dir: Path = DATA_DIR) -> dict[str, object]:
    series = load_data(data_dir)
    try:
        infections = series["infections.txt"]
        infections2 = series["infections2.txt"]
    except KeyError as error:
        raise ValueError(f"missing required input file: {error.args[0]}") from error

    per_file_tenth = {
        name: tenth_largest_distinct(values)
        for name, values in sorted(series.items())
    }
    encoded_differences = difference_sequence(infections)

    return {
        "1.1": {
            "tenth_largest_distinct": tenth_largest_distinct(infections),
        },
        "1.2": {
            "sum": sum(per_file_tenth.values()),
            "per_file": per_file_tenth,
        },
        "1.3": {
            "sequence": encoded_differences,
            "character_count": len(encoded_differences),
        },
        "1.4": maximum_increment_periods(infections),
        "2.1": seven_day_statistics(infections),
        "2.2": most_similar_file_pairs(series),
        "2.3": linear_fit(infections2),
        "2.4": fastest_exponential_windows(infections2),
    }


def render_answers(answers: Mapping[str, object]) -> str:
    one_one = answers["1.1"]
    one_two = answers["1.2"]
    one_three = answers["1.3"]
    one_four = answers["1.4"]
    two_one = answers["2.1"]
    two_two = answers["2.2"]
    two_three = answers["2.3"]
    two_four = answers["2.4"]
    assert isinstance(one_one, Mapping)
    assert isinstance(one_two, Mapping)
    assert isinstance(one_three, Mapping)
    assert isinstance(one_four, Mapping)
    assert isinstance(two_one, Mapping)
    assert isinstance(two_two, Mapping)
    assert isinstance(two_three, Mapping)
    assert isinstance(two_four, Mapping)

    lines = [
        "Programming 1",
        "=============",
        f"(1) 第 10 大的不重复值: {one_one['tenth_largest_distinct']}",
        f"(2) 所有文件的 N_f 之和: {one_two['sum']}",
        "    各文件 N_f:",
    ]
    per_file = one_two["per_file"]
    assert isinstance(per_file, Mapping)
    lines.extend(f"    - {name}: {value}" for name, value in per_file.items())
    lines.extend(
        [
            f"(3) diff.txt 内容: {one_three['sequence']}",
            f"    字符数: {one_three['character_count']}",
            f"(4) 最大增量和: {one_four['maximum_sum']}",
            f"    最短长度: {one_four['shortest_length']} 天",
            "    区间:",
        ]
    )
    periods = one_four["periods"]
    assert isinstance(periods, list)
    lines.extend(
        f"    - From Day {period['start_day']} to {period['end_day']}"
        for period in periods
    )

    lines.extend(
        [
            "",
            "Programming 2",
            "=============",
            f"(1) maximum ave(i): {two_one['maximum']}",
            f"    minimum ave(i): {two_one['minimum']}",
            f"    sum of ave(i): {two_one['sum']}",
            f"(2) 最高相似度: {two_two['maximum_score']}",
            "    文件对:",
        ]
    )
    pairs = two_two["pairs"]
    assert isinstance(pairs, list)
    lines.extend(f"    - {pair[0]}, {pair[1]}" for pair in pairs)
    lines.extend(
        [
            f"(3) a: {two_three['a']}",
            f"    k: {two_three['k']}",
            "(4) 使 a 最大的解:",
        ]
    )
    solutions = two_four["solutions"]
    assert isinstance(solutions, list)
    lines.extend(
        f"    - s={solution['s']}, a={solution['a']}, k={solution['k']}"
        for solution in solutions
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="2021-8 Programming 1/2 reference solver")
    parser.add_argument("--data", type=Path, default=DATA_DIR, help="input data directory")
    parser.add_argument(
        "--format",
        choices=("json", "text"),
        default="text",
        help="output representation",
    )
    args = parser.parse_args()
    answers = solve_all(args.data.resolve())
    if args.format == "json":
        print(json.dumps(answers, ensure_ascii=False, indent=2))
    else:
        print(render_answers(answers), end="")


if __name__ == "__main__":
    main()
