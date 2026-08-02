"""用途：处理字符矩阵，包括连通区域、旋转、翻转和转置。
示例输入：由 '.' 和 '#' 组成的矩形网格。
示例输出：区域大小，以及三种变换后的网格。
复杂度：每项操作均为 O(HW)。
陷阱：二维列表不要用 [[x] * w] * h；zip 转置结果是 tuple，需要再 join。
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIR4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def components(grid: list[str]) -> list[int]:
    height, width = len(grid), len(grid[0])
    seen = [bytearray(width) for _ in range(height)]
    sizes = []
    for row in range(height):
        for col in range(width):
            if grid[row][col] != "#" or seen[row][col]:
                continue
            seen[row][col] = 1
            stack = [(row, col)]
            size = 0
            while stack:
                r, c = stack.pop()
                size += 1
                for dr, dc in DIR4:
                    nr, nc = r + dr, c + dc
                    if (
                        0 <= nr < height
                        and 0 <= nc < width
                        and not seen[nr][nc]
                        and grid[nr][nc] == "#"
                    ):
                        seen[nr][nc] = 1
                        stack.append((nr, nc))
            sizes.append(size)
    return sorted(sizes, reverse=True)


def rotate_clockwise(grid: list[str]) -> list[str]:
    return ["".join(column) for column in zip(*grid[::-1])]


def flip_horizontal(grid: list[str]) -> list[str]:
    return [row[::-1] for row in grid]


def transpose(grid: list[str]) -> list[str]:
    return ["".join(column) for column in zip(*grid)]


def print_grid(title: str, grid: list[str]) -> None:
    print(title)
    print(*grid, sep="\n")


def main() -> None:
    grid = (ROOT / "input" / "grid.txt").read_text(encoding="utf-8").splitlines()
    if not grid or len({len(row) for row in grid}) != 1:
        raise ValueError("grid must be non-empty and rectangular")
    print("components:", components(grid))
    print_grid("rotated:", rotate_clockwise(grid))
    print_grid("flipped:", flip_horizontal(grid))
    print_grid("transposed:", transpose(grid))


if __name__ == "__main__":
    main()
