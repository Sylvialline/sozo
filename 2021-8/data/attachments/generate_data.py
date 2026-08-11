from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Mapping, Sequence

sys.dont_write_bytecode = True

from reference_solver import (
    ATTACHMENTS_DIR,
    DATA_DIR,
    EXPECTED_DATA_FILES,
    difference_sequence,
    render_answers,
    solve_all,
    tenth_largest_distinct,
)


ATTACHMENT_FILES = (
    "README.md",
    "answers.json",
    "answers.txt",
    "dataset_summary.json",
    "diff.txt",
    "generate_data.py",
    "reference_solver.py",
    "test_reference_solver.py",
)


def build_infections() -> list[int]:
    # Two equally short (three-day) periods attain the global increment sum
    # 5000.  The repeated 5000 and repeated tail values also exercise the
    # distinct-value and zero-increment requirements.
    values = [
        120,
        150,
        150,
        130,
        90,
        40,
        0,
        1200,
        3300,
        5000,
        5000,
        4200,
        2600,
        800,
        300,
        120,
        75,
        40,
        20,
        0,
        1000,
        3600,
        5000,
        4700,
        4300,
        3900,
        3600,
        3200,
        2800,
        2400,
    ]
    tail: list[int] = []
    for index in range(66):
        value = 250 + ((811 * index + 37 * index * index) % 4550)
        if index in {12, 29, 47}:
            value = tail[-1]
        tail.append(value)
    return values + tail


def build_infections2() -> list[int]:
    # The logarithms form a two-day staircase: x_i + 1 == 2**floor(i/2).
    # Copying the same 31-point block creates an exact mathematical tie, while
    # zero padding makes the two full blocks, and only those blocks, maximal.
    # The largest value stays at 32767, a conservative size despite the lack
    # of an explicit numeric bound in the statement.
    exponential_block = [2 ** (index // 2) - 1 for index in range(31)]
    return (
        [0] * 8
        + exponential_block
        + [0] * 20
        + exponential_block
        + [0] * 8
    )


def build_echo_files() -> tuple[list[int], list[int], list[int]]:
    core = [5000 + 137 * index + 19 * (index % 7) for index in range(45)]
    long_a = (
        [900 + 31 * index for index in range(7)]
        + core
        + [13000 + 43 * index for index in range(5)]
    )
    long_b = (
        [16000 + 47 * index for index in range(3)]
        + core
        + [18000 + 53 * index for index in range(13)]
    )
    return core, long_a, long_b


def build_dataset() -> dict[str, list[int]]:
    echo_short, echo_long_a, echo_long_b = build_echo_files()
    dataset = {
        "baseline.txt": [1000 + 23 * index + 7 * (index % 4) for index in range(37)],
        "echo_long_a.txt": echo_long_a,
        "echo_long_b.txt": echo_long_b,
        "echo_short.txt": echo_short,
        "infections.txt": build_infections(),
        "infections2.txt": build_infections2(),
        "plateau.txt": [700 + 101 * (index // 3) for index in range(48)],
        "sawtooth.txt": [
            200 + 173 * (index % 11) + 29 * (index // 11)
            for index in range(66)
        ],
    }
    if tuple(sorted(dataset)) != EXPECTED_DATA_FILES:
        raise AssertionError("generated file set does not match EXPECTED_DATA_FILES")
    return dataset


def validate_generated_dataset(dataset: Mapping[str, Sequence[int]]) -> None:
    if tuple(sorted(dataset)) != EXPECTED_DATA_FILES:
        raise ValueError("unexpected generated input file set")

    for name, values in dataset.items():
        if len(values) < 31:
            raise ValueError(f"{name}: every generated series must contain at least 31 days")
        if any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in values):
            raise ValueError(f"{name}: infection counts must be non-negative integers")
        if len(set(values)) < 10:
            raise ValueError(f"{name}: fewer than 10 distinct values")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as output:
        output.write(text)


def write_json(path: Path, value: object) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def write_input_files(dataset: Mapping[str, Sequence[int]]) -> None:
    for name, values in sorted(dataset.items()):
        write_text(DATA_DIR / name, ":".join(map(str, values)) + "\n")


def build_summary(
    dataset: Mapping[str, Sequence[int]],
    answers: Mapping[str, object],
) -> dict[str, object]:
    file_statistics = {
        name: {
            "days": len(values),
            "minimum": min(values),
            "maximum": max(values),
            "distinct_values": len(set(values)),
            "tenth_largest_distinct": tenth_largest_distinct(values),
        }
        for name, values in sorted(dataset.items())
    }
    one_four = answers["1.4"]
    two_two = answers["2.2"]
    two_four = answers["2.4"]
    assert isinstance(one_four, Mapping)
    assert isinstance(two_two, Mapping)
    assert isinstance(two_four, Mapping)
    return {
        "provenance": "Deterministic synthetic practice data; not the original exam USB data.",
        "statement_limits": (
            "The statement gives no explicit length or numeric upper bound. "
            "All generated values are non-negative integers, every file has at least "
            "10 distinct values, infections.txt has at least 7 days, and "
            "infections2.txt has at least 31 days."
        ),
        "input_files": list(EXPECTED_DATA_FILES),
        "file_statistics": file_statistics,
        "coverage": {
            "problem_1_1": "duplicates, zero, more than 10 distinct values",
            "problem_1_2": "different file lengths and per-file distinct-value counts",
            "problem_1_3": "positive, negative, and zero increments with changing digit widths",
            "problem_1_4": {
                "maximum_sum": one_four["maximum_sum"],
                "tied_shortest_periods": len(one_four["periods"]),
            },
            "problem_2_1": "first/middle/last seven-day windows and exact rational rounding",
            "problem_2_2": {
                "different_lengths": True,
                "interior_exact_matches": True,
                "tied_best_pairs": len(two_two["pairs"]),
            },
            "problem_2_3": "exact integer sufficient statistics and a nontrivial rational linear fit",
            "problem_2_4": {
                "window_length": two_four["window_length"],
                "tied_fastest_windows": len(two_four["solutions"]),
                "contains_zero": True,
            },
        },
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def manifest_paths() -> list[Path]:
    paths = [DATA_DIR / name for name in EXPECTED_DATA_FILES]
    paths.extend(ATTACHMENTS_DIR / name for name in ATTACHMENT_FILES)
    return paths


def write_manifest() -> None:
    lines = ["sha256\tbytes\tpath"]
    for path in sorted(manifest_paths(), key=lambda item: item.relative_to(DATA_DIR).as_posix()):
        if not path.is_file():
            raise FileNotFoundError(f"cannot build manifest; missing {path}")
        relative = path.relative_to(DATA_DIR).as_posix()
        lines.append(f"{sha256(path)}\t{path.stat().st_size}\t{relative}")
    write_text(ATTACHMENTS_DIR / "manifest.sha256.tsv", "\n".join(lines) + "\n")


def generate() -> None:
    dataset = build_dataset()
    validate_generated_dataset(dataset)
    write_input_files(dataset)

    answers = solve_all(DATA_DIR)
    write_json(ATTACHMENTS_DIR / "answers.json", answers)
    write_text(ATTACHMENTS_DIR / "answers.txt", render_answers(answers))

    one_three = answers["1.3"]
    assert isinstance(one_three, Mapping)
    expected_diff = difference_sequence(dataset["infections.txt"])
    if one_three["sequence"] != expected_diff:
        raise AssertionError("reference difference output is inconsistent")
    write_text(ATTACHMENTS_DIR / "diff.txt", expected_diff + "\n")

    write_json(ATTACHMENTS_DIR / "dataset_summary.json", build_summary(dataset, answers))
    write_manifest()
    print(f"generated {len(dataset)} data files and all reference artifacts")


if __name__ == "__main__":
    generate()
