"""用 ``dict[(row, col)] = value`` 表示稀疏矩阵。

示例输入：3×4 矩阵中的 (0,1)=2、(2,0)=5，向量 [10,20,30,40]。
示例输出：查询缺失元素得到 0，矩阵乘向量得到 [40,0,50]。
复杂度：查询/修改平均 O(1)，乘向量 O(nnz+rows)；dict 是哈希结构。
常见陷阱：零值应从字典删除，否则 ``nnz`` 和遍历成本会虚增。
"""

SparseMatrix = dict[tuple[int, int], float]


def set_value(matrix: SparseMatrix, row: int, col: int, value: float) -> None:
    if value == 0:
        matrix.pop((row, col), None)
    else:
        matrix[row, col] = value


def get_value(matrix: SparseMatrix, row: int, col: int) -> float:
    return matrix.get((row, col), 0.0)


def matvec(matrix: SparseMatrix, rows: int, vector: list[float]) -> list[float]:
    result = [0.0] * rows
    for (row, col), value in matrix.items():
        if not (0 <= row < rows and 0 <= col < len(vector)):
            raise IndexError((row, col))
        result[row] += value * vector[col]
    return result


def main() -> None:
    matrix: SparseMatrix = {}
    set_value(matrix, 0, 1, 2)
    set_value(matrix, 2, 0, 5)
    print("entries:", sorted(matrix.items()))
    print("missing:", get_value(matrix, 1, 1))
    print("matvec:", matvec(matrix, 3, [10, 20, 30, 40]))
    set_value(matrix, 0, 1, 0)
    print("after deleting zero:", matrix)


if __name__ == "__main__":
    main()
