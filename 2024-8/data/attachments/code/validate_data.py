from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference_solver import (  # noqa: E402
    SPECS,
    iter_csv_ints,
    iter_format2,
    iter_format3,
    solve_all,
)


FORMAT_BY_FILE = {
    "data1a.txt": 1,
    "data1b.txt": 1,
    "data2a.txt": 2,
    "data2b.txt": 2,
    "data2c.txt": 2,
    "data3a.txt": 3,
    "data3b.txt": 3,
    "data3c.txt": 3,
    "data4a.txt": 3,
    "data4b.txt": 3,
    "data4c.txt": 3,
    "data4d.txt": 3,
    "data4e.txt": 3,
    "data4f.txt": 3,
    "data5a.txt": 3,
    "data5b.txt": 3,
    "data5c.txt": 3,
}

DIMS_BY_FILE = {file_name: (r, c) for file_name, r, c in SPECS.values()}


def load_entries(path: Path, rows: int, cols: int, fmt: int) -> Dict[Tuple[int, int], int]:
    entries: Dict[Tuple[int, int], int] = {}
    if fmt == 1:
        values = list(iter_csv_ints(path))
        assert len(values) == rows * cols, f"{path.name}: wrong Format 1 length"
        for flat, x in enumerate(values):
            assert -9 <= x <= 9
            if x:
                i, j0 = divmod(flat, cols)
                entries[(i + 1, j0 + 1)] = x
    elif fmt == 2:
        previous = (0, 0)
        for i, j, x in iter_format2(path):
            assert 1 <= i <= rows and 1 <= j <= cols
            assert x != 0 and -9 <= x <= 9
            assert (i, j) > previous, f"{path.name}: entries are not strictly row-major"
            assert (i, j) not in entries
            entries[(i, j)] = x
            previous = (i, j)
    else:
        previous = (0, 0)
        for i, j, x in iter_format3(path, cols):
            assert 1 <= i <= rows and 1 <= j <= cols
            assert x != 0 and -9 <= x <= 9
            assert (i, j) > previous, f"{path.name}: entries are not strictly row-major"
            assert (i, j) not in entries
            entries[(i, j)] = x
            previous = (i, j)
    return entries


def validate_constraints(data_dir: Path) -> Dict[str, Dict[Tuple[int, int], int]]:
    all_entries: Dict[str, Dict[Tuple[int, int], int]] = {}
    for file_name, fmt in FORMAT_BY_FILE.items():
        rows, cols = DIMS_BY_FILE[file_name]
        entries = load_entries(data_dir / file_name, rows, cols, fmt)
        row_counts = defaultdict(int)
        col_counts = defaultdict(int)
        for i, j in entries:
            row_counts[i] += 1
            col_counts[j] += 1
        assert len(entries) <= 10**6, f"{file_name}: too many nonzeros"
        assert max(row_counts.values(), default=0) <= 10, f"{file_name}: row cap exceeded"
        assert max(col_counts.values(), default=0) <= 10, f"{file_name}: column cap exceeded"
        all_entries[file_name] = entries

    assert len(all_entries["data4c.txt"]) <= 1000
    assert len(all_entries["data4d.txt"]) <= 1000
    return all_entries


def brute_max_row(entries: Dict[Tuple[int, int], int], rows: int) -> Tuple[int, int]:
    sums = [0] * rows
    for (i, _), x in entries.items():
        sums[i - 1] += x
    best = max(sums)
    return sums.index(best) + 1, best


def brute_max_col(entries: Dict[Tuple[int, int], int], cols: int) -> Tuple[int, int]:
    sums = [0] * cols
    for (_, j), x in entries.items():
        sums[j - 1] += x
    best = max(sums)
    return sums.index(best) + 1, best


def brute_star(
    x_entries: Dict[Tuple[int, int], int],
    y_entries: Dict[Tuple[int, int], int],
    l: int,
    m: int,
    n: int,
) -> Tuple[int, int]:
    row_sums = []
    for i in range(1, l + 1):
        total = 0
        for j in range(1, n + 1):
            products = [x_entries.get((i, k), 0) * y_entries.get((k, j), 0) for k in range(1, m + 1)]
            total += min(products) + max(products)
        row_sums.append(total)
    best = max(row_sums)
    return row_sums.index(best) + 1, best


def brute_zero_windows(
    entries: Dict[Tuple[int, int], int], rows: int, cols: int, h: int, w: int
) -> int:
    matrix = [[0] * cols for _ in range(rows)]
    for (i, j), x in entries.items():
        matrix[i - 1][j - 1] = x
    prefix = [[0] * (cols + 1) for _ in range(rows + 1)]
    for i in range(rows):
        running = 0
        for j in range(cols):
            running += matrix[i][j]
            prefix[i + 1][j + 1] = prefix[i][j + 1] + running
    answer = 0
    for top in range(rows - h + 1):
        for left in range(cols - w + 1):
            bottom, right = top + h, left + w
            total = prefix[bottom][right] - prefix[top][right] - prefix[bottom][left] + prefix[top][left]
            answer += total == 0
    return answer


def validate_answers(root: Path, entries: Dict[str, Dict[Tuple[int, int], int]]) -> None:
    actual = solve_all(root / "data")
    stored = json.loads((root / "answers.json").read_text(encoding="utf-8"))
    assert actual == stored, "stored answers do not match reference solver"

    # Independent brute-force checks for every small subproblem.
    assert actual["1a"] == dict(zip(("row", "sum"), brute_max_row(entries["data1a.txt"], 6)))
    assert actual["2a"] == dict(zip(("row", "sum"), brute_max_row(entries["data2a.txt"], 6)))
    assert actual["3a"] == dict(zip(("row", "sum"), brute_max_col(entries["data3a.txt"], 6)))
    assert actual["4a"] == dict(
        zip(
            ("row", "sum"),
            brute_star(entries["data4a.txt"], entries["data4b.txt"], 2, 4, 3),
        )
    )
    assert actual["5a"]["count"] == brute_zero_windows(entries["data5a.txt"], 8, 6, 2, 3)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate generated data and answers")
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1], help="package root"
    )
    args = parser.parse_args()
    root = args.root.resolve()
    entries = validate_constraints(root / "data")
    validate_answers(root, entries)
    print("all data constraints and reference answers validated")


if __name__ == "__main__":
    main()
