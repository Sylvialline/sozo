"""用嵌套 ``list`` 创建、检查、读取和打印稠密矩阵。

示例输入：文本 ``"1 2 3\\n4 5 6"``。
示例输出：2×3 矩阵，并将 (1,2) 元素从 6 改为 99。
复杂度：解析和遍历 r×c 矩阵均为 O(rc)。
常见陷阱：``[[0] * cols] * rows`` 共享行；矩阵下标通常写作 ``a[row][col]``。
"""


def zeros(rows: int, cols: int) -> list[list[int]]:
    return [[0] * cols for _ in range(rows)]


def parse_matrix(text: str) -> list[list[int]]:
    matrix = [[int(token) for token in line.split()] for line in text.splitlines()]
    matrix = [row for row in matrix if row]
    if matrix and any(len(row) != len(matrix[0]) for row in matrix):
        raise ValueError("ragged matrix")
    return matrix


def shape(matrix: list[list[int]]) -> tuple[int, int]:
    return len(matrix), len(matrix[0]) if matrix else 0


def format_matrix(matrix: list[list[int]]) -> str:
    return "\n".join(" ".join(map(str, row)) for row in matrix)


def main() -> None:
    matrix = parse_matrix("1 2 3\n4 5 6")
    print("shape:", shape(matrix))
    matrix[1][2] = 99
    print(format_matrix(matrix))

    independent = zeros(2, 3)
    independent[0][0] = 7
    print("independent rows:", independent)


if __name__ == "__main__":
    main()
