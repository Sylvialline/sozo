"""用途：把 COO 稀疏矩阵转换为 CSR，并执行查询和矩阵乘向量。
示例输入：3×4 矩阵的 5 个非零项以及长度 4 的向量。
示例输出：row_ptr=[0, 2, 3, 5]；A*x=[6, 6, 11]。
复杂度：转换 O(nnz log nnz)，查询 O(行非零数)，乘法 O(nnz)。
陷阱：重复 COO 坐标需要预先定义相加或覆盖语义；本例禁止重复坐标。
"""

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent


@dataclass
class CSR:
    rows: int
    cols: int
    row_ptr: list[int]
    col_idx: list[int]
    values: list[int]

    @classmethod
    def from_coo(
        cls,
        rows: int,
        cols: int,
        entries: list[tuple[int, int, int]],
    ) -> "CSR":
        entries = sorted(entries)
        if len({(r, c) for r, c, _ in entries}) != len(entries):
            raise ValueError("duplicate COO coordinate")
        row_ptr = [0] * (rows + 1)
        col_idx = []
        values = []
        for row, col, value in entries:
            row_ptr[row + 1] += 1
            col_idx.append(col)
            values.append(value)
        for row in range(rows):
            row_ptr[row + 1] += row_ptr[row]
        return cls(rows, cols, row_ptr, col_idx, values)

    def get(self, row: int, col: int) -> int:
        for index in range(self.row_ptr[row], self.row_ptr[row + 1]):
            if self.col_idx[index] == col:
                return self.values[index]
        return 0

    def matvec(self, vector: list[int]) -> list[int]:
        if len(vector) != self.cols:
            raise ValueError("vector length mismatch")
        result = [0] * self.rows
        for row in range(self.rows):
            for index in range(self.row_ptr[row], self.row_ptr[row + 1]):
                result[row] += self.values[index] * vector[self.col_idx[index]]
        return result


def read_coo(path: Path) -> CSR:
    lines = path.read_text(encoding="utf-8").splitlines()
    rows, cols, count = map(int, lines[0].split())
    entries = [tuple(map(int, line.split())) for line in lines[1:]]
    if len(entries) != count:
        raise ValueError("nnz does not match header")
    return CSR.from_coo(rows, cols, entries)


def main() -> None:
    matrix = read_coo(ROOT / "input" / "matrix.coo")
    vector = list(
        map(
            int,
            (ROOT / "input" / "vector.txt").read_text(encoding="utf-8").split(),
        )
    )
    print("row_ptr:", matrix.row_ptr)
    print("col_idx:", matrix.col_idx)
    print("values:", matrix.values)
    print("A[2,2]:", matrix.get(2, 2))
    print("A*x:", matrix.matvec(vector))


if __name__ == "__main__":
    main()
