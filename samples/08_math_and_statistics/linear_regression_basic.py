"""不依赖 NumPy 的一元线性回归闭式解。

示例输入：点 (0,1)、(1,3)、(2,5)、(3,7)。
示例输出：斜率 2、截距 1、RMSE 0、x=4 时预测 9。
复杂度：时间 O(n)，额外空间 O(1)（若输入已存为列表）。
常见陷阱：所有 x 相同时分母为 0；大数数据可先中心化以改善数值稳定性。
"""

from math import sqrt


def linear_regression(points: list[tuple[float, float]]) -> tuple[float, float, float]:
    """返回 ``(slope, intercept, rmse)``。"""
    if len(points) < 2:
        raise ValueError("at least two points are required")
    n = len(points)
    mean_x = sum(x for x, _ in points) / n
    mean_y = sum(y for _, y in points) / n
    sxx = sum((x - mean_x) ** 2 for x, _ in points)
    if sxx == 0:
        raise ValueError("x values must not all be equal")
    slope = sum((x - mean_x) * (y - mean_y) for x, y in points) / sxx
    intercept = mean_y - slope * mean_x
    mse = sum((slope * x + intercept - y) ** 2 for x, y in points) / n
    return slope, intercept, sqrt(mse)


def main() -> None:
    points = [(0, 1), (1, 3), (2, 5), (3, 7)]
    slope, intercept, rmse = linear_regression(points)
    print(f"y = {slope:g}x + {intercept:g}")
    print(f"RMSE: {rmse:g}")
    print(f"predict(4): {slope * 4 + intercept:g}")


if __name__ == "__main__":
    main()
