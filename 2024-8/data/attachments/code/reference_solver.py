from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import DefaultDict, Dict, Iterable, Iterator, List, Tuple


# (file name, rows, columns)
SPECS = {
    "1a": ("data1a.txt", 6, 4),
    "1b": ("data1b.txt", 100, 150),
    "2a": ("data2a.txt", 6, 4),
    "2b": ("data2b.txt", 100, 150),
    "2c": ("data2c.txt", 10**6, 10**6),
    "3a": ("data3a.txt", 4, 6),
    "3b": ("data3b.txt", 100, 150),
    "3c": ("data3c.txt", 10**6, 10**6),
    "4a_A": ("data4a.txt", 2, 4),
    "4a_B": ("data4b.txt", 4, 3),
    "4b_C": ("data4c.txt", 10**6, 10**6),
    "4b_D": ("data4d.txt", 10**6, 10**6),
    "4c_E": ("data4e.txt", 10**6, 10**6),
    "4c_F": ("data4f.txt", 10**6, 10**6),
    "5a": ("data5a.txt", 8, 6),
    "5b": ("data5b.txt", 10**6, 10**6),
    "5c": ("data5c.txt", 10**6, 10**6),
}


def iter_csv_ints(path: Path, chunk_size: int = 1 << 20) -> Iterator[int]:
    """Read comma-separated integers without materializing all tokens at once."""
    carry = ""
    with path.open("r", encoding="utf-8") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            text = carry + chunk
            parts = text.split(",")
            carry = parts.pop()
            for token in parts:
                token = token.strip()
                if token:
                    yield int(token)
        carry = carry.strip()
        if carry:
            yield int(carry)


def _take_exact(it: Iterator[int], n: int, label: str) -> List[int]:
    values: List[int] = []
    for _ in range(n):
        try:
            values.append(next(it))
        except StopIteration as exc:
            raise ValueError(f"{label}: truncated input") from exc
    return values


def _ensure_exhausted(it: Iterator[int], label: str) -> None:
    try:
        extra = next(it)
    except StopIteration:
        return
    raise ValueError(f"{label}: unexpected extra integer {extra}")


def _lowest_missing(indices: Iterable[int], upper: int) -> int | None:
    candidate = 1
    for x in sorted(indices):
        if x < candidate:
            continue
        if x == candidate:
            candidate += 1
            if candidate > upper:
                return None
        else:
            break
    return candidate if candidate <= upper else None


def _choose_lowest_max(sums: Dict[int, int], total_indices: int) -> Tuple[int, int]:
    """Choose the lowest index among maximum sums, including implicit all-zero indices."""
    best_index: int | None = None
    best_sum: int | None = None

    missing = _lowest_missing(sums.keys(), total_indices)
    if missing is not None:
        best_index, best_sum = missing, 0

    for index, value in sums.items():
        if best_sum is None or value > best_sum or (value == best_sum and index < best_index):
            best_index, best_sum = index, value

    if best_index is None or best_sum is None:
        # total_indices is positive in this problem.
        raise ValueError("no valid index")
    return best_index, best_sum


def solve_format1_max_row(path: Path, rows: int, cols: int) -> Tuple[int, int]:
    it = iter_csv_ints(path)
    best_row = 1
    best_sum: int | None = None
    for i in range(1, rows + 1):
        row_sum = sum(_take_exact(it, cols, str(path)))
        if best_sum is None or row_sum > best_sum:
            best_row, best_sum = i, row_sum
    _ensure_exhausted(it, str(path))
    assert best_sum is not None
    return best_row, best_sum


def iter_format2(path: Path) -> Iterator[Tuple[int, int, int]]:
    it = iter_csv_ints(path)
    while True:
        try:
            i = next(it)
        except StopIteration:
            return
        try:
            j = next(it)
            x = next(it)
        except StopIteration as exc:
            raise ValueError(f"{path}: Format 2 needs triples") from exc
        yield i, j, x


def iter_format3(path: Path, cols: int) -> Iterator[Tuple[int, int, int]]:
    """Yield 1-based (row, col, value) entries from Format 3."""
    it = iter_csv_ints(path)
    flat = -1
    while True:
        try:
            zeros = next(it)
        except StopIteration:
            return
        try:
            value = next(it)
        except StopIteration as exc:
            raise ValueError(f"{path}: Format 3 needs pairs") from exc
        if zeros < 0:
            raise ValueError(f"{path}: negative zero run")
        flat += zeros + 1
        row, col0 = divmod(flat, cols)
        yield row + 1, col0 + 1, value


def solve_format2_max_row(path: Path, rows: int, cols: int) -> Tuple[int, int]:
    sums: DefaultDict[int, int] = defaultdict(int)
    for i, j, x in iter_format2(path):
        if not (1 <= i <= rows and 1 <= j <= cols):
            raise ValueError(f"{path}: coordinate out of range: {(i, j)}")
        sums[i] += x
    return _choose_lowest_max(dict(sums), rows)


def solve_transposed_format3_max_row(path: Path, rows: int, cols: int) -> Tuple[int, int]:
    # A row of the transposed matrix is a column of the original matrix.
    column_sums: DefaultDict[int, int] = defaultdict(int)
    for i, j, x in iter_format3(path, cols):
        if i > rows:
            raise ValueError(f"{path}: entry beyond matrix bounds")
        column_sums[j] += x
    return _choose_lowest_max(dict(column_sums), cols)


def read_format3_rows(path: Path, rows: int, cols: int) -> Dict[int, List[Tuple[int, int]]]:
    result: DefaultDict[int, List[Tuple[int, int]]] = defaultdict(list)
    for i, j, x in iter_format3(path, cols):
        if i > rows:
            raise ValueError(f"{path}: entry beyond matrix bounds")
        result[i].append((j, x))
    return dict(result)


def solve_star_max_row(
    x_path: Path,
    y_path: Path,
    l: int,
    m: int,
    n: int,
) -> Tuple[int, int]:
    """Find the maximum row sum of Z = X star Y.

    For every output pair (i, j), only shared nonzero k values can produce a
    nonzero product. If fewer than m such products exist, zero is also among
    the m products and must be included when taking min and max.
    """
    x_rows = read_format3_rows(x_path, l, m)
    y_rows = read_format3_rows(y_path, m, n)

    row_sums: Dict[int, int] = {}
    for i, x_entries in x_rows.items():
        # j -> [minimum nonzero product, maximum nonzero product, count]
        extrema: Dict[int, List[int]] = {}
        for k, x in x_entries:
            for j, y in y_rows.get(k, ()):
                product = x * y
                old = extrema.get(j)
                if old is None:
                    extrema[j] = [product, product, 1]
                else:
                    if product < old[0]:
                        old[0] = product
                    if product > old[1]:
                        old[1] = product
                    old[2] += 1

        total = 0
        for minimum, maximum, count in extrema.values():
            if count < m:
                if minimum > 0:
                    minimum = 0
                if maximum < 0:
                    maximum = 0
            total += minimum + maximum
        row_sums[i] = total

    return _choose_lowest_max(row_sums, l)


def count_zero_sum_submatrices_format3(
    path: Path,
    rows: int,
    cols: int,
    height: int,
    width: int,
) -> int:
    """Count fixed-size zero-sum submatrices by sweeping top-row positions.

    A nonzero cell contributes to a rectangle of possible top-left positions.
    The row dimension is handled with add/remove events. Since width <= 100 in
    this problem, each event updates at most 100 top-left columns explicitly.
    """
    if not (1 <= height <= rows and 1 <= width <= cols):
        raise ValueError("invalid submatrix size")

    top_rows = rows - height + 1
    left_cols = cols - width + 1
    events: DefaultDict[int, List[Tuple[int, int, int]]] = defaultdict(list)

    for i, j, x in iter_format3(path, cols):
        if i > rows:
            raise ValueError(f"{path}: entry beyond matrix bounds")

        start_row = max(1, i - height + 1)
        end_row = min(i, top_rows)
        start_col = max(1, j - width + 1)
        end_col = min(j, left_cols)
        if start_row > end_row or start_col > end_col:
            continue

        events[start_row].append((start_col, end_col, x))
        if end_row + 1 <= top_rows:
            events[end_row + 1].append((start_col, end_col, -x))

    # Only nonzero window sums are stored. All other left positions have sum 0.
    column_sums: Dict[int, int] = {}
    zero_columns = left_cols
    answer = 0
    previous_row = 1

    for event_row in sorted(events):
        if event_row > top_rows:
            break

        if event_row > previous_row:
            answer += (event_row - previous_row) * zero_columns

        for left, right, delta in events[event_row]:
            for b in range(left, right + 1):
                old = column_sums.get(b, 0)
                new = old + delta
                if old == 0:
                    zero_columns -= 1
                if new == 0:
                    zero_columns += 1
                    column_sums.pop(b, None)
                else:
                    column_sums[b] = new

        previous_row = event_row

    if previous_row <= top_rows:
        answer += (top_rows - previous_row + 1) * zero_columns

    return answer


def solve_all(data_dir: Path) -> Dict[str, Dict[str, int]]:
    ans: Dict[str, Dict[str, int]] = {}

    for key in ("1a", "1b"):
        file_name, r, c = SPECS[key]
        row, value = solve_format1_max_row(data_dir / file_name, r, c)
        ans[key] = {"row": row, "sum": value}

    for key in ("2a", "2b", "2c"):
        file_name, r, c = SPECS[key]
        row, value = solve_format2_max_row(data_dir / file_name, r, c)
        ans[key] = {"row": row, "sum": value}

    for key in ("3a", "3b", "3c"):
        file_name, r, c = SPECS[key]
        row, value = solve_transposed_format3_max_row(data_dir / file_name, r, c)
        ans[key] = {"row": row, "sum": value}

    row, value = solve_star_max_row(
        data_dir / SPECS["4a_A"][0], data_dir / SPECS["4a_B"][0], 2, 4, 3
    )
    ans["4a"] = {"row": row, "sum": value}

    row, value = solve_star_max_row(
        data_dir / SPECS["4b_C"][0], data_dir / SPECS["4b_D"][0], 10**6, 10**6, 10**6
    )
    ans["4b"] = {"row": row, "sum": value}

    row, value = solve_star_max_row(
        data_dir / SPECS["4c_E"][0], data_dir / SPECS["4c_F"][0], 10**6, 10**6, 10**6
    )
    ans["4c"] = {"row": row, "sum": value}

    for key, h, w in (("5a", 2, 3), ("5b", 10, 10), ("5c", 100, 100)):
        file_name, r, c = SPECS[key]
        count = count_zero_sum_submatrices_format3(data_dir / file_name, r, c, h, w)
        ans[key] = {"count": count}

    return ans


def main() -> None:
    parser = argparse.ArgumentParser(description="Reference solver for 2024-8 programming data")
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parents[1] / "data")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args()

    answers = solve_all(args.data_dir)
    if args.json:
        print(json.dumps(answers, ensure_ascii=False, indent=2, sort_keys=True))
        return

    for q in ("1a", "1b", "2a", "2b", "2c", "3a", "3b", "3c", "4a", "4b", "4c"):
        item = answers[q]
        print(f"{q}: row={item['row']}, sum={item['sum']}")
    for q in ("5a", "5b", "5c"):
        print(f"{q}: count={answers[q]['count']}")


if __name__ == "__main__":
    main()
