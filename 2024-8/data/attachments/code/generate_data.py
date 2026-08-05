from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import DefaultDict, Dict, Iterable, List, Sequence, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference_solver import solve_all  # noqa: E402


NONZERO_VALUES = tuple(v for v in range(-9, 10) if v != 0)
MILD_VALUES = (-9, -8, -7, -6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5)


@dataclass
class SparseMatrix:
    rows: int
    cols: int
    cells: Dict[Tuple[int, int], int] = field(default_factory=dict)
    row_count: DefaultDict[int, int] = field(default_factory=lambda: defaultdict(int))
    col_count: DefaultDict[int, int] = field(default_factory=lambda: defaultdict(int))

    def can_add(self, i: int, j: int) -> bool:
        return (
            1 <= i <= self.rows
            and 1 <= j <= self.cols
            and (i, j) not in self.cells
            and self.row_count[i] < 10
            and self.col_count[j] < 10
        )

    def add(self, i: int, j: int, value: int) -> None:
        if value == 0 or not (-9 <= value <= 9):
            raise ValueError("matrix values must be nonzero integers in [-9, 9]")
        if not self.can_add(i, j):
            raise ValueError(f"cannot add entry {(i, j)}")
        self.cells[(i, j)] = value
        self.row_count[i] += 1
        self.col_count[j] += 1

    def set_existing(self, i: int, j: int, value: int) -> None:
        if (i, j) not in self.cells:
            self.add(i, j, value)
        else:
            if value == 0 or not (-9 <= value <= 9):
                raise ValueError("invalid value")
            self.cells[(i, j)] = value

    @property
    def nnz(self) -> int:
        return len(self.cells)


def random_fill(
    matrix: SparseMatrix,
    target_nnz: int,
    rng: random.Random,
    values: Sequence[int] = MILD_VALUES,
    excluded_rows: Iterable[int] = (),
    excluded_cols: Iterable[int] = (),
) -> None:
    excluded_rows = set(excluded_rows)
    excluded_cols = set(excluded_cols)
    attempts = 0
    max_attempts = max(100_000, target_nnz * 200)
    while matrix.nnz < target_nnz:
        attempts += 1
        if attempts > max_attempts:
            raise RuntimeError(f"failed to fill matrix to {target_nnz} nonzeros")
        i = rng.randint(1, matrix.rows)
        j = rng.randint(1, matrix.cols)
        if i in excluded_rows or j in excluded_cols or not matrix.can_add(i, j):
            continue
        matrix.add(i, j, rng.choice(values))


def add_target_row(matrix: SparseMatrix, row: int, rng: random.Random, value: int = 9) -> None:
    candidates = list(range(1, matrix.cols + 1))
    rng.shuffle(candidates)
    added = 0
    for j in candidates:
        if matrix.can_add(row, j):
            matrix.add(row, j, value)
            added += 1
            if added == min(10, matrix.cols):
                return
    raise RuntimeError("could not add target row")


def add_target_col(matrix: SparseMatrix, col: int, rng: random.Random, value: int = 9) -> None:
    candidates = list(range(1, matrix.rows + 1))
    rng.shuffle(candidates)
    added = 0
    for i in candidates:
        if matrix.can_add(i, col):
            matrix.add(i, col, value)
            added += 1
            if added == min(10, matrix.rows):
                return
    raise RuntimeError("could not add target column")


def write_format1(path: Path, matrix: SparseMatrix) -> None:
    values = []
    for i in range(1, matrix.rows + 1):
        for j in range(1, matrix.cols + 1):
            values.append(str(matrix.cells.get((i, j), 0)))
    path.write_text(",".join(values) + "\n", encoding="utf-8")


def write_format2(path: Path, matrix: SparseMatrix) -> None:
    values: List[str] = []
    for (i, j), x in sorted(matrix.cells.items()):
        values.extend((str(i), str(j), str(x)))
    path.write_text(",".join(values) + "\n", encoding="utf-8")


def write_format3(path: Path, matrix: SparseMatrix) -> None:
    values: List[str] = []
    previous = -1
    for (i, j), x in sorted(matrix.cells.items(), key=lambda item: (item[0][0], item[0][1])):
        flat = (i - 1) * matrix.cols + (j - 1)
        zeros = flat - previous - 1
        values.extend((str(zeros), str(x)))
        previous = flat
    path.write_text(",".join(values) + "\n", encoding="utf-8")


def build_1a() -> SparseMatrix:
    rows = [
        [3, -2, 0, 1],
        [-4, 5, 2, -1],
        [9, 8, -3, 4],
        [0, -1, 2, 3],
        [6, -7, 1, 0],
        [-2, 4, 0, 5],
    ]
    m = SparseMatrix(6, 4)
    for i, row in enumerate(rows, 1):
        for j, x in enumerate(row, 1):
            if x:
                m.add(i, j, x)
    return m


def build_1b() -> SparseMatrix:
    rng = random.Random(1101)
    m = SparseMatrix(100, 150)
    random_fill(m, 650, rng, excluded_rows={73})
    add_target_row(m, 73, rng)
    return m


def build_2a() -> SparseMatrix:
    # Row 3 is the only all-zero row; every represented row has a negative sum.
    rows = [
        [-2, -1, 0, 0],
        [0, -3, -2, 0],
        [0, 0, 0, 0],
        [-1, 0, -4, -1],
        [0, -2, 0, -2],
        [-5, 1, -1, 0],
    ]
    m = SparseMatrix(6, 4)
    for i, row in enumerate(rows, 1):
        for j, x in enumerate(row, 1):
            if x:
                m.add(i, j, x)
    return m


def build_2b() -> SparseMatrix:
    rng = random.Random(2202)
    m = SparseMatrix(100, 150)
    random_fill(m, 700, rng, excluded_rows={42})
    add_target_row(m, 42, rng)
    return m


def build_2c() -> SparseMatrix:
    rng = random.Random(2203)
    m = SparseMatrix(10**6, 10**6)
    random_fill(m, 30_000, rng, excluded_rows={999_983})
    add_target_row(m, 999_983, rng)
    # Explicit boundary and very large-coordinate entries.
    for i, j, x in ((1, 1, -9), (1, 10**6, 4), (10**6, 1, -3), (10**6, 10**6, 5)):
        if m.can_add(i, j):
            m.add(i, j, x)
    return m


def build_3a() -> SparseMatrix:
    rows = [
        [1, -2, 0, 3, 9, 0],
        [0, 4, -1, 0, 9, -2],
        [-3, 0, 2, 1, 9, 0],
        [2, -1, 0, -2, 9, 4],
    ]
    m = SparseMatrix(4, 6)
    for i, row in enumerate(rows, 1):
        for j, x in enumerate(row, 1):
            if x:
                m.add(i, j, x)
    return m


def build_3b() -> SparseMatrix:
    rng = random.Random(3302)
    m = SparseMatrix(100, 150)
    random_fill(m, 650, rng, excluded_cols={137})
    add_target_col(m, 137, rng)
    return m


def build_3c() -> SparseMatrix:
    rng = random.Random(3303)
    m = SparseMatrix(10**6, 10**6)
    random_fill(m, 35_000, rng, excluded_cols={987_654})
    add_target_col(m, 987_654, rng)
    for i, j, x in ((1, 1, 2), (10**6, 10**6, -7), (500_000, 1, 6)):
        if m.can_add(i, j):
            m.add(i, j, x)
    return m


def build_4a() -> Tuple[SparseMatrix, SparseMatrix]:
    a_vals = [[2, -3, 4, 1], [-5, 2, -1, 3]]
    b_vals = [[4, -2, 1], [-3, 5, 2], [2, -4, -2], [1, 3, -5]]
    a = SparseMatrix(2, 4)
    b = SparseMatrix(4, 3)
    for i, row in enumerate(a_vals, 1):
        for j, x in enumerate(row, 1):
            a.add(i, j, x)
    for i, row in enumerate(b_vals, 1):
        for j, x in enumerate(row, 1):
            b.add(i, j, x)
    return a, b


def _pick_available_index(
    rng: random.Random,
    upper: int,
    forbidden: set[int],
    count_map: DefaultDict[int, int],
) -> int:
    while True:
        x = rng.randint(1, upper)
        if x not in forbidden and count_map[x] < 10:
            return x


def add_channel_groups(
    x: SparseMatrix,
    y: SparseMatrix,
    groups: int,
    rng: random.Random,
    forbidden_rows: set[int],
    forbidden_k: set[int],
    forbidden_cols: set[int],
) -> None:
    used_k = set(forbidden_k)
    for _ in range(groups):
        while True:
            k = rng.randint(1, x.cols)
            if k not in used_k and x.col_count[k] == 0 and y.row_count[k] == 0:
                used_k.add(k)
                break

        left_rows: List[int] = []
        while len(left_rows) < 3:
            i = _pick_available_index(rng, x.rows, forbidden_rows, x.row_count)
            if i not in left_rows and x.can_add(i, k):
                left_rows.append(i)

        right_cols: List[int] = []
        while len(right_cols) < 3:
            j = _pick_available_index(rng, y.cols, forbidden_cols, y.col_count)
            if j not in right_cols and y.can_add(k, j):
                right_cols.append(j)

        for i in left_rows:
            x.add(i, k, rng.choice(MILD_VALUES))
        for j in right_cols:
            y.add(k, j, rng.choice(MILD_VALUES))


def add_star_target(
    x: SparseMatrix,
    y: SparseMatrix,
    target_row: int,
    k_start: int,
    j_start: int,
) -> Tuple[set[int], set[int]]:
    ks: set[int] = set()
    js: set[int] = set()
    for a in range(10):
        k = k_start + a
        x.add(target_row, k, 9)
        ks.add(k)
        for b in range(10):
            j = j_start + a * 10 + b
            y.add(k, j, 9)
            js.add(j)
    return ks, js


def add_repeated_star_path(
    x: SparseMatrix,
    y: SparseMatrix,
    i: int,
    j: int,
    ks: Sequence[int],
    x_values: Sequence[int],
    y_values: Sequence[int],
) -> None:
    for k, xv, yv in zip(ks, x_values, y_values):
        x.add(i, k, xv)
        y.add(k, j, yv)


def build_4b() -> Tuple[SparseMatrix, SparseMatrix]:
    rng = random.Random(4402)
    x = SparseMatrix(10**6, 10**6)
    y = SparseMatrix(10**6, 10**6)
    target_row = 777_777
    target_ks, target_js = add_star_target(x, y, target_row, 900_000, 800_000)
    add_repeated_star_path(x, y, 12_345, 54_321, [700_001, 700_002, 700_003], [3, -4, 2], [4, 5, 3])
    add_channel_groups(x, y, 180, rng, {target_row}, target_ks, target_js)
    assert x.nnz <= 1000 and y.nnz <= 1000
    return x, y


def build_4c() -> Tuple[SparseMatrix, SparseMatrix]:
    rng = random.Random(4403)
    x = SparseMatrix(10**6, 10**6)
    y = SparseMatrix(10**6, 10**6)
    target_row = 654_321
    target_ks, target_js = add_star_target(x, y, target_row, 950_000, 850_000)
    add_repeated_star_path(x, y, 22_222, 33_333, [740_001, 740_002, 740_003, 740_004], [3, -4, 2, -1], [4, 5, 3, -9])
    add_repeated_star_path(x, y, 22_223, 33_334, [740_011, 740_012, 740_013], [2, 4, 3], [3, 2, 1])
    add_channel_groups(x, y, 4_000, rng, {target_row}, target_ks, target_js)
    return x, y


def build_5a() -> SparseMatrix:
    rows = [
        [1, -1, 0, 2, -2, 0],
        [0, 0, 0, 1, -1, 0],
        [3, -3, 0, 0, 0, 0],
        [0, 2, -2, 0, 4, -4],
        [1, 1, -2, 0, 0, 0],
        [-1, 0, 1, 2, 0, -2],
        [0, 0, 0, -3, 3, 0],
        [2, -2, 0, 0, 1, -1],
    ]
    m = SparseMatrix(8, 6)
    for i, row in enumerate(rows, 1):
        for j, x in enumerate(row, 1):
            if x:
                m.add(i, j, x)
    return m


def add_cancellation_pairs(
    matrix: SparseMatrix,
    count: int,
    rng: random.Random,
    max_delta_row: int,
    max_delta_col: int,
) -> None:
    added = 0
    while added < count:
        i = rng.randint(1, matrix.rows - max_delta_row)
        j = rng.randint(1, matrix.cols - max_delta_col)
        di = rng.randint(0, max_delta_row)
        dj = rng.randint(1 if di == 0 else 0, max_delta_col)
        i2, j2 = i + di, j + dj
        v = rng.choice((1, 2, 3, 4, 5, 7, 9))
        if matrix.can_add(i, j) and matrix.can_add(i2, j2):
            matrix.add(i, j, v)
            matrix.add(i2, j2, -v)
            added += 1


def build_5b() -> SparseMatrix:
    rng = random.Random(5502)
    m = SparseMatrix(10**6, 10**6)
    random_fill(m, 6_000, rng)
    add_cancellation_pairs(m, 300, rng, 9, 9)
    for i, j, x in (
        (1, 1, 9),
        (1, 10**6, -9),
        (10**6, 1, 7),
        (10**6, 10**6, -7),
        (5, 5, 4),
        (999_996, 999_996, -4),
    ):
        if m.can_add(i, j):
            m.add(i, j, x)
    return m


def build_5c() -> SparseMatrix:
    rng = random.Random(5503)
    m = SparseMatrix(10**6, 10**6)
    random_fill(m, 15_000, rng)
    add_cancellation_pairs(m, 600, rng, 99, 99)
    # A small cancellation cluster near the top-left and boundary entries.
    planted = (
        (1, 1, 5),
        (1, 100, -5),
        (100, 1, -3),
        (100, 100, 3),
        (10**6, 10**6, 9),
        (999_901, 999_901, -9),
    )
    for i, j, x in planted:
        if m.can_add(i, j):
            m.add(i, j, x)
    return m


def write_answers(root: Path, answers: Dict[str, Dict[str, int]]) -> None:
    (root / "answers.json").write_text(
        json.dumps(answers, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = ["2024-8 Programming generated data - reference answers", ""]
    for q in ("1a", "1b", "2a", "2b", "2c", "3a", "3b", "3c", "4a", "4b", "4c"):
        item = answers[q]
        lines.append(f"{q}: row = {item['row']}, sum = {item['sum']}")
    for q in ("5a", "5b", "5c"):
        lines.append(f"{q}: count = {answers[q]['count']}")
    (root / "answers.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_manifest(root: Path) -> None:
    rows = []
    for path in sorted((root / "data").glob("*.txt")):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append(f"{path.name}\t{path.stat().st_size}\t{digest}")
    (root / "manifest.sha256.tsv").write_text(
        "file\tbytes\tsha256\n" + "\n".join(rows) + "\n", encoding="utf-8"
    )


def generate(root: Path) -> None:
    data = root / "data"
    data.mkdir(parents=True, exist_ok=True)

    write_format1(data / "data1a.txt", build_1a())
    write_format1(data / "data1b.txt", build_1b())

    write_format2(data / "data2a.txt", build_2a())
    write_format2(data / "data2b.txt", build_2b())
    write_format2(data / "data2c.txt", build_2c())

    write_format3(data / "data3a.txt", build_3a())
    write_format3(data / "data3b.txt", build_3b())
    write_format3(data / "data3c.txt", build_3c())

    a, b = build_4a()
    write_format3(data / "data4a.txt", a)
    write_format3(data / "data4b.txt", b)

    c, d = build_4b()
    write_format3(data / "data4c.txt", c)
    write_format3(data / "data4d.txt", d)

    e, f = build_4c()
    write_format3(data / "data4e.txt", e)
    write_format3(data / "data4f.txt", f)

    write_format3(data / "data5a.txt", build_5a())
    write_format3(data / "data5b.txt", build_5b())
    write_format3(data / "data5c.txt", build_5c())

    answers = solve_all(data)
    write_answers(root, answers)
    write_manifest(root)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic data for 2024-8 programming problem")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="package root containing data/ and answers files",
    )
    args = parser.parse_args()
    generate(args.output.resolve())
    print(f"generated data in {args.output.resolve()}")


if __name__ == "__main__":
    main()
