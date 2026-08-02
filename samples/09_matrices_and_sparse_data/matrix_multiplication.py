"""纯 Python 稠密矩阵乘法，使用 i-k-j 循环并跳过 A 中的零。

示例输入：2×3 矩阵 A 与 3×2 矩阵 B。
示例输出：A×B=[[4,5],[10,11]]。
复杂度：一般为 O(rows_A*shared*cols_B)，结果空间 O(rows_A*cols_B)。
常见陷阱：必须检查维度和矩阵是否等长；纯 Python 不适合超大稠密矩阵。
"""

Number = int | float


def shape(matrix: list[list[Number]]) -> tuple[int, int]:
    if not matrix:
        return 0, 0
    cols = len(matrix[0])
    if any(len(row) != cols for row in matrix):
        raise ValueError("ragged matrix")
    return len(matrix), cols


def matmul(a: list[list[Number]], b: list[list[Number]]) -> list[list[Number]]:
    rows_a, shared = shape(a)
    rows_b, cols_b = shape(b)
    if shared != rows_b:
        raise ValueError("incompatible dimensions")
    result: list[list[Number]] = [[0] * cols_b for _ in range(rows_a)]
    for i, row_a in enumerate(a):
        for k, value_a in enumerate(row_a):
            if value_a == 0:
                continue
            for j, value_b in enumerate(b[k]):
                result[i][j] += value_a * value_b
    return result


def main() -> None:
    a = [[1, 0, 2], [0, 3, 4]]
    b = [[2, 1], [2, 1], [1, 2]]
    print("A x B:", matmul(a, b))
    print("row vector x column vector:", matmul([[1, 2, 3]], [[4], [5], [6]]))


if __name__ == "__main__":
    main()
