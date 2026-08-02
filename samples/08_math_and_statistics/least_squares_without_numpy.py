"""纯标准库的多项式最小二乘（正规方程 + 高斯消元）。

示例输入：由 y=1+2x+x² 生成的 5 个点，拟合二次多项式。
示例输出：系数 [1.0, 2.0, 1.0]（按常数项到高次项排列）。
复杂度：n 个点、d+1 个系数时为 O(n*d²+d³)，空间 O(d²)。
常见陷阱：正规方程会放大病态性；奇异矩阵应报错，严肃数值计算宜用 QR/SVD。
"""


def solve_linear_system(a: list[list[float]], b: list[float]) -> list[float]:
    """用带部分选主元的 Gauss-Jordan 消元解方阵方程。"""
    n = len(a)
    aug = [row[:] + [rhs] for row, rhs in zip(a, b)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(aug[row][col]))
        if abs(aug[pivot][col]) < 1e-12:
            raise ValueError("singular or nearly singular matrix")
        aug[col], aug[pivot] = aug[pivot], aug[col]
        divisor = aug[col][col]
        aug[col] = [value / divisor for value in aug[col]]
        for row in range(n):
            if row == col:
                continue
            factor = aug[row][col]
            for j in range(col, n + 1):
                aug[row][j] -= factor * aug[col][j]
    return [aug[i][-1] for i in range(n)]


def polynomial_least_squares(
    points: list[tuple[float, float]], degree: int
) -> list[float]:
    """返回 ``c``，使 y≈c[0]+c[1]x+...+c[degree]x^degree。"""
    if degree < 0 or len(points) < degree + 1:
        raise ValueError("insufficient points for requested degree")
    size = degree + 1
    sums = [sum(x**power for x, _ in points) for power in range(2 * degree + 1)]
    matrix = [[sums[i + j] for j in range(size)] for i in range(size)]
    rhs = [sum(y * x**i for x, y in points) for i in range(size)]
    return solve_linear_system(matrix, rhs)


def main() -> None:
    points = [(x, 1 + 2 * x + x * x) for x in range(-2, 3)]
    coefficients = polynomial_least_squares(points, degree=2)
    print("coefficients:", [round(value, 10) for value in coefficients])


if __name__ == "__main__":
    main()
