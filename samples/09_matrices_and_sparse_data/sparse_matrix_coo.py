"""COO（坐标列表）稀疏矩阵：三条并行数组存 row/col/value。

示例输入：(0,1,2)、(2,0,5)、重复项 (0,1,3)。
示例输出：合并重复项后 (0,1)=5，乘向量 [10,20] 得 [100,0,50]。
复杂度：追加 O(1)，规范化排序 O(nnz log nnz)，乘向量 O(nnz+rows)。
常见陷阱：COO 可含重复坐标且通常未排序；查询频繁时应转换成 CSR 或 dict。
"""

from dataclasses import dataclass, field


@dataclass
class COO:
    rows: int
    cols: int
    row_indices: list[int] = field(default_factory=list)
    col_indices: list[int] = field(default_factory=list)
    values: list[float] = field(default_factory=list)

    def add(self, row: int, col: int, value: float) -> None:
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            raise IndexError((row, col))
        if value != 0:
            self.row_indices.append(row)
            self.col_indices.append(col)
            self.values.append(value)

    def entries(self) -> list[tuple[int, int, float]]:
        return list(zip(self.row_indices, self.col_indices, self.values))

    def coalesced_entries(self) -> list[tuple[int, int, float]]:
        merged: dict[tuple[int, int], float] = {}
        for row, col, value in self.entries():
            merged[row, col] = merged.get((row, col), 0.0) + value
        return [
            (row, col, value)
            for (row, col), value in sorted(merged.items())
            if value != 0
        ]

    def matvec(self, vector: list[float]) -> list[float]:
        if len(vector) != self.cols:
            raise ValueError("vector length differs from column count")
        result = [0.0] * self.rows
        for row, col, value in self.coalesced_entries():
            result[row] += value * vector[col]
        return result


def main() -> None:
    matrix = COO(3, 2)
    matrix.add(0, 1, 2)
    matrix.add(2, 0, 5)
    matrix.add(0, 1, 3)
    print("raw:", matrix.entries())
    print("coalesced:", matrix.coalesced_entries())
    print("matvec:", matrix.matvec([10, 20]))


if __name__ == "__main__":
    main()
