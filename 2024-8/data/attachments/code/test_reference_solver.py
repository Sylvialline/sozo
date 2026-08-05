from __future__ import annotations

import random
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_data import SparseMatrix, write_format1, write_format2, write_format3  # noqa: E402
from reference_solver import (  # noqa: E402
    count_zero_sum_submatrices_format3,
    solve_format1_max_row,
    solve_format2_max_row,
    solve_star_max_row,
    solve_transposed_format3_max_row,
)


def dense(matrix: SparseMatrix) -> list[list[int]]:
    return [
        [matrix.cells.get((i, j), 0) for j in range(1, matrix.cols + 1)]
        for i in range(1, matrix.rows + 1)
    ]


def lowest_max(values: list[int]) -> tuple[int, int]:
    best = max(values)
    return values.index(best) + 1, best


def random_matrix(rows: int, cols: int, rng: random.Random, p: float = 0.35) -> SparseMatrix:
    m = SparseMatrix(rows, cols)
    for i in range(1, rows + 1):
        for j in range(1, cols + 1):
            if rng.random() < p:
                m.add(i, j, rng.choice([v for v in range(-3, 4) if v]))
    return m


def run_tests() -> None:
    rng = random.Random(202408)
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for case in range(200):
            r = rng.randint(1, 7)
            c = rng.randint(1, 7)
            m = random_matrix(r, c, rng)
            a = dense(m)

            p1 = root / "f1.txt"
            p2 = root / "f2.txt"
            p3 = root / "f3.txt"
            write_format1(p1, m)
            write_format2(p2, m)
            write_format3(p3, m)

            expected_rows = lowest_max([sum(row) for row in a])
            assert solve_format1_max_row(p1, r, c) == expected_rows
            assert solve_format2_max_row(p2, r, c) == expected_rows
            expected_cols = lowest_max([sum(a[i][j] for i in range(r)) for j in range(c)])
            assert solve_transposed_format3_max_row(p3, r, c) == expected_cols

            h = rng.randint(1, r)
            w = rng.randint(1, c)
            brute = 0
            for top in range(r - h + 1):
                for left in range(c - w + 1):
                    total = sum(a[i][j] for i in range(top, top + h) for j in range(left, left + w))
                    brute += total == 0
            assert count_zero_sum_submatrices_format3(p3, r, c, h, w) == brute

        for case in range(200):
            l = rng.randint(1, 5)
            m_dim = rng.randint(1, 5)
            n = rng.randint(1, 5)
            x = random_matrix(l, m_dim, rng, 0.6)
            y = random_matrix(m_dim, n, rng, 0.6)
            px = root / "x.txt"
            py = root / "y.txt"
            write_format3(px, x)
            write_format3(py, y)
            xd, yd = dense(x), dense(y)
            row_sums = []
            for i in range(l):
                total = 0
                for j in range(n):
                    products = [xd[i][k] * yd[k][j] for k in range(m_dim)]
                    total += min(products) + max(products)
                row_sums.append(total)
            assert solve_star_max_row(px, py, l, m_dim, n) == lowest_max(row_sums)

    print("randomized reference-solver tests passed")


if __name__ == "__main__":
    run_tests()
