"""矩阵转置：``zip(*matrix)`` 和显式下标两种写法。

示例输入：[[1,2,3],[4,5,6]]。
示例输出：[[1,4],[2,5],[3,6]]。
复杂度：时间和输出空间均为 O(rows*cols)。
常见陷阱：``zip`` 返回迭代器且会按最短行截断，因此应先拒绝不等长矩阵。
"""

from typing import TypeVar

T = TypeVar("T")


def transpose(matrix: list[list[T]]) -> list[list[T]]:
    if not matrix:
        return []
    if any(len(row) != len(matrix[0]) for row in matrix):
        raise ValueError("ragged matrix")
    return [list(column) for column in zip(*matrix)]


def transpose_by_index(matrix: list[list[T]]) -> list[list[T]]:
    if not matrix:
        return []
    cols = len(matrix[0])
    if any(len(row) != cols for row in matrix):
        raise ValueError("ragged matrix")
    return [[matrix[row][col] for row in range(len(matrix))] for col in range(cols)]


def main() -> None:
    matrix = [[1, 2, 3], [4, 5, 6]]
    print("zip:", transpose(matrix))
    print("index:", transpose_by_index(matrix))
    print("back:", transpose(transpose(matrix)))


if __name__ == "__main__":
    main()
