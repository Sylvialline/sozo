"""用途：可选 NumPy 的数组创建、切片、广播和布尔索引。
示例输入：[1, 2, 3, 4]
示例输出：[2, 4, 6, 8] 与大于 2 的元素。
复杂度：各向量操作 O(n)，底层循环在 C 中执行。
陷阱：NumPy 切片通常是视图而非复制；NumPy 不是 Python 标准库。
"""


def main() -> None:
    try:
        import numpy as np
    except ImportError:
        print("NumPy is optional and is not installed.")
        return

    array = np.array([1, 2, 3, 4])
    print(array * 2)
    print(array[array > 2])
    view = array[1:3]
    view[0] = 99
    print("slice is a view:", array)


if __name__ == "__main__":
    main()
