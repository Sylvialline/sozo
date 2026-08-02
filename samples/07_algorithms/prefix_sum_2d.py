"""用途：构造二维前缀和，O(1) 查询半开矩形 [top,bottom)×[left,right)。
示例输入：[[1,2,3],[4,5,6]]，查询行 [0,2)、列 [1,3)。
示例输出：2+3+5+6 = 16。
复杂度：预处理 O(hw)、查询 O(1)、空间 O(hw)。
常见陷阱：前缀表尺寸为 (h+1)×(w+1)；空矩阵和不规则行需要显式处理。
"""


def build_prefix(grid: list[list[int]]) -> list[list[int]]:
    height = len(grid)
    width = len(grid[0]) if height else 0
    if any(len(row) != width for row in grid):
        raise ValueError("矩阵每行长度必须相同")
    prefix = [[0] * (width + 1) for _ in range(height + 1)]
    for row in range(height):
        row_sum = 0
        for column in range(width):
            row_sum += grid[row][column]
            prefix[row + 1][column + 1] = prefix[row][column + 1] + row_sum
    return prefix


def rectangle_sum(
    prefix: list[list[int]], top: int, left: int, bottom: int, right: int
) -> int:
    return (
        prefix[bottom][right]
        - prefix[top][right]
        - prefix[bottom][left]
        + prefix[top][left]
    )


def main() -> None:
    grid = [[1, 2, 3], [4, 5, 6]]
    prefix = build_prefix(grid)
    print("sum:", rectangle_sum(prefix, 0, 1, 2, 3))
    print("one cell:", rectangle_sum(prefix, 1, 2, 2, 3))


if __name__ == "__main__":
    main()
