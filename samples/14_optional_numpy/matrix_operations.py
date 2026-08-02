"""用途：可选 NumPy 的转置、矩阵乘法和线性方程求解。
示例输入：2×2 矩阵 A 与向量 b。
示例输出：A.T、A@A 和满足 Ax=b 的 x。
复杂度：矩阵乘法通常 O(n^3)，求解稠密方程通常 O(n^3)。
陷阱：* 是逐元素乘法，@ 才是矩阵乘法；不要显式求逆来解 Ax=b。
"""


def main() -> None:
    try:
        import numpy as np
    except ImportError:
        print("NumPy is optional and is not installed.")
        return

    matrix = np.array([[2.0, 1.0], [1.0, 3.0]])
    vector = np.array([5.0, 7.0])
    print("transpose:\n", matrix.T, sep="")
    print("A @ A:\n", matrix @ matrix, sep="")
    print("solution:", np.linalg.solve(matrix, vector))


if __name__ == "__main__":
    main()
