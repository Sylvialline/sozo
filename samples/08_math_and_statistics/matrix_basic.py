"""二维列表矩阵的加法、转置和乘法。

示例输入：A=[[1,2],[3,4]]、B=[[5,6],[7,8]]。
示例输出：A+B=[[6,8],[10,12]]，A×B=[[19,22],[43,50]]。
复杂度：加法 O(rc)，转置 O(rc)，r×k 乘 k×c 为 O(rkc)。
常见陷阱：不要用 ``[[0]*m]*n`` 建矩阵，它会让各行引用同一列表。
"""


def add(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    if len(a) != len(b) or any(len(x) != len(y) for x, y in zip(a, b)):
        raise ValueError("matrix sizes differ")
    return [[x + y for x, y in zip(row_a, row_b)] for row_a, row_b in zip(a, b)]


def transpose(a: list[list[int]]) -> list[list[int]]:
    if not a:
        return []
    if any(len(row) != len(a[0]) for row in a):
        raise ValueError("ragged matrix")
    return [list(column) for column in zip(*a)]


def multiply(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    if not a or not b or not b[0] or len(a[0]) != len(b):
        raise ValueError("incompatible matrix sizes")
    if any(len(row) != len(a[0]) for row in a) or any(
        len(row) != len(b[0]) for row in b
    ):
        raise ValueError("ragged matrix")
    bt = transpose(b)
    return [[sum(x * y for x, y in zip(row, col)) for col in bt] for row in a]


def main() -> None:
    a = [[1, 2], [3, 4]]
    b = [[5, 6], [7, 8]]
    print("add:", add(a, b))
    print("transpose:", transpose(a))
    print("multiply:", multiply(a, b))
    safe_zero_matrix = [[0] * 3 for _ in range(2)]
    print("independent rows:", safe_zero_matrix)


if __name__ == "__main__":
    main()
