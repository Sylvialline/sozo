"""用途：用可选 NumPy 对照完成同一组一元线性最小二乘。
示例输入：input/points.csv。
示例输出：NumPy available 时输出 slope=2、intercept=1、mse=0。
复杂度：O(n)，底层向量运算由 NumPy 实现。
陷阱：NumPy 不是标准库；考试电脑未预装时不能依赖此文件。
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> None:
    try:
        import numpy as np
    except ImportError:
        print("NumPy is optional and is not installed.")
        return

    with (ROOT / "input" / "points.csv").open(
        encoding="utf-8",
        newline="",
    ) as file:
        points = [
            (float(row["x"]), float(row["y"]))
            for row in csv.DictReader(file)
        ]
    x = np.array([point[0] for point in points])
    y = np.array([point[1] for point in points])
    design = np.column_stack((x, np.ones_like(x)))
    slope, intercept = np.linalg.lstsq(design, y, rcond=None)[0]
    mse = np.mean((y - (slope * x + intercept)) ** 2)
    print(f"slope: {slope:.3f}")
    print(f"intercept: {intercept:.3f}")
    print(f"mse: {mse:.3f}")


if __name__ == "__main__":
    main()
