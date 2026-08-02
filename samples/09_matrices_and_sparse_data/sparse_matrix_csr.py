"""CSR（压缩行）稀疏矩阵的查询和矩阵乘向量。

示例输入：indptr=[0,2,2,3]、indices=[0,2,1]、data=[1,4,5]。
示例输出：(0,2)=4、(1,1)=0，乘 [10,20,30] 得 [130,0,100]。
复杂度：按行遍历总计 O(nnz)；行内二分查询 O(log(row_nnz))。
常见陷阱：``indptr`` 长度必须为 rows+1，且每行列下标应升序、无重复。
"""

from bisect import bisect_left
from dataclasses import dataclass


@dataclass
class CSR:
    rows: int
    cols: int
    indptr: list[int]
    indices: list[int]
    data: list[float]

    def __post_init__(self) -> None:
        if len(self.indptr) != self.rows + 1:
            raise ValueError("indptr length must be rows + 1")
        if self.indptr[0] != 0 or self.indptr[-1] != len(self.data):
            raise ValueError("invalid indptr endpoints")
        if len(self.indices) != len(self.data):
            raise ValueError("indices/data lengths differ")
        for row in range(self.rows):
            start, end = self.indptr[row], self.indptr[row + 1]
            row_indices = self.indices[start:end]
            if row_indices != sorted(set(row_indices)):
                raise ValueError("each row must have sorted unique column indices")

    def get(self, row: int, col: int) -> float:
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            raise IndexError((row, col))
        start, end = self.indptr[row], self.indptr[row + 1]
        position = bisect_left(self.indices, col, start, end)
        return self.data[position] if position < end and self.indices[position] == col else 0.0

    def matvec(self, vector: list[float]) -> list[float]:
        if len(vector) != self.cols:
            raise ValueError("vector length differs from column count")
        result = [0.0] * self.rows
        for row in range(self.rows):
            for k in range(self.indptr[row], self.indptr[row + 1]):
                result[row] += self.data[k] * vector[self.indices[k]]
        return result


def main() -> None:
    matrix = CSR(
        rows=3,
        cols=3,
        indptr=[0, 2, 2, 3],
        indices=[0, 2, 1],
        data=[1, 4, 5],
    )
    print("get:", matrix.get(0, 2), matrix.get(1, 1))
    print("matvec:", matrix.matvec([10, 20, 30]))


if __name__ == "__main__":
    main()
