"""用途：可选 NumPy 的均值、总体/样本方差和分位数。
示例输入：[1, 2, 3, 4, 10]
示例输出：mean=4、population variance、sample variance、median。
复杂度：每项 O(n)。
陷阱：np.var 默认 ddof=0 是总体方差；样本方差通常需要 ddof=1。
"""


def main() -> None:
    try:
        import numpy as np
    except ImportError:
        print("NumPy is optional and is not installed.")
        return

    values = np.array([1, 2, 3, 4, 10], dtype=float)
    print("mean:", np.mean(values))
    print("population variance:", np.var(values))
    print("sample variance:", np.var(values, ddof=1))
    print("median:", np.quantile(values, 0.5))


if __name__ == "__main__":
    main()
