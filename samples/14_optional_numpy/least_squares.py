"""用途：可选 NumPy 的一元线性最小二乘拟合。
示例输入：x=[0,1,2,3]，y=[1,3,5,7]
示例输出：slope=2、intercept=1。
复杂度：对 n×2 设计矩阵约 O(n)。
陷阱：lstsq 返回多个值；显式加入全 1 列才能拟合截距。
"""


def main() -> None:
    try:
        import numpy as np
    except ImportError:
        print("NumPy is optional and is not installed.")
        return

    x = np.array([0.0, 1.0, 2.0, 3.0])
    y = np.array([1.0, 3.0, 5.0, 7.0])
    design = np.column_stack((x, np.ones_like(x)))
    slope, intercept = np.linalg.lstsq(design, y, rcond=None)[0]
    print(f"slope={slope:.3f}, intercept={intercept:.3f}")


if __name__ == "__main__":
    main()
