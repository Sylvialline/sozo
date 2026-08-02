"""用途：在字符网格上 BFS，绕过 # 障碍求 S 到 G 的最短步数。
示例输入：["S..#",".#..","...G"]。
示例输出：distance=5。
复杂度：O(hw) 时间，距离矩阵与队列 O(hw) 空间。
常见陷阱：二维 list 要逐行创建；入队即标记；先检查边界再访问 grid[nr][nc]。
"""

from collections import deque


DIRECTIONS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def shortest_grid_path(grid: list[str]) -> int | None:
    height = len(grid)
    width = len(grid[0]) if height else 0
    if any(len(row) != width for row in grid):
        raise ValueError("网格行长度不一致")
    start = goal = None
    for row in range(height):
        for column in range(width):
            if grid[row][column] == "S":
                start = (row, column)
            elif grid[row][column] == "G":
                goal = (row, column)
    if start is None or goal is None:
        raise ValueError("网格必须各含一个 S 和 G")

    distance = [[-1] * width for _ in range(height)]
    distance[start[0]][start[1]] = 0
    queue = deque([start])
    while queue:
        row, column = queue.popleft()
        if (row, column) == goal:
            return distance[row][column]
        for dr, dc in DIRECTIONS:
            next_row, next_column = row + dr, column + dc
            if not (0 <= next_row < height and 0 <= next_column < width):
                continue
            if grid[next_row][next_column] == "#" or distance[next_row][next_column] != -1:
                continue
            distance[next_row][next_column] = distance[row][column] + 1
            queue.append((next_row, next_column))
    return None


def main() -> None:
    grid = ["S..#", ".#..", "...G"]
    print("distance:", shortest_grid_path(grid))


if __name__ == "__main__":
    main()
