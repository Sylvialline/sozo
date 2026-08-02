"""用途：仅用标准库完成一元线性最小二乘拟合。
示例输入：points.csv 中的 (0,1)、(1,3)、(2,5)、(3,7)。
示例输出：slope=2、intercept=1、mse=0。
复杂度：O(n) 时间和 O(n) 存储；流式实现可降到 O(1) 额外空间。
陷阱：所有 x 相同时分母为零；浮点结果应使用 isclose 或容差比较。
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def least_squares(points: list[tuple[float, float]]) -> tuple[float, float, float]:
    if len(points) < 2:
        raise ValueError("at least two points are required")
    mean_x = sum(x for x, _ in points) / len(points)
    mean_y = sum(y for _, y in points) / len(points)
    denominator = sum((x - mean_x) ** 2 for x, _ in points)
    if denominator == 0:
        raise ValueError("all x values are equal")
    slope = sum(
        (x - mean_x) * (y - mean_y) for x, y in points
    ) / denominator
    intercept = mean_y - slope * mean_x
    mse = sum(
        (y - (slope * x + intercept)) ** 2 for x, y in points
    ) / len(points)
    return slope, intercept, mse


def main() -> None:
    with (ROOT / "input" / "points.csv").open(
        encoding="utf-8",
        newline="",
    ) as file:
        points = [
            (float(row["x"]), float(row["y"]))
            for row in csv.DictReader(file)
        ]
    slope, intercept, mse = least_squares(points)
    print(f"slope: {slope:.3f}")
    print(f"intercept: {intercept:.3f}")
    print(f"mse: {mse:.3f}")


if __name__ == "__main__":
    main()
