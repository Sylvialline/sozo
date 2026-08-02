"""用途：用列表推导式完成映射、过滤、扁平化和安全矩阵初始化。
示例输入：range(8) 与 [[1,2],[3,4]]。
示例输出：偶数平方 [0,4,16,36]，扁平列表 [1,2,3,4]。
复杂度：单层推导 O(n)，生成结果占 O(n)；二维初始化 O(nm)。
常见陷阱：[[0] * m] * n 共享行；复杂副作用不应塞进推导式；变量只在推导式内有效。
"""


def main() -> None:
    even_squares = [x * x for x in range(8) if x % 2 == 0]
    nested = [[1, 2], [3, 4]]
    flat = [value for row in nested for value in row]
    matrix = [[0 for _ in range(3)] for _ in range(2)]
    matrix[0][0] = 9

    print("even squares:", even_squares)
    print("flat:", flat)
    print("matrix:", matrix)
    pairs = [(x, y) for x in range(2) for y in range(3) if x != y]
    print("pairs:", pairs)


if __name__ == "__main__":
    main()
