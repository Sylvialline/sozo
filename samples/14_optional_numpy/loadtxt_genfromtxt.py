"""用途：比较 NumPy loadtxt 与能处理缺失值的 genfromtxt。
示例输入：规则数字 CSV 和包含空字段的 CSV。
示例输出：二维数组；缺失位置为 nan。
复杂度：O(元素数)。
陷阱：loadtxt 遇到缺失值会失败；delimiter、dtype 和 skip_header 必须匹配文件。
"""

from io import StringIO


def main() -> None:
    try:
        import numpy as np
    except ImportError:
        print("NumPy is optional and is not installed.")
        return

    regular = np.loadtxt(StringIO("1,2\n3,4\n"), delimiter=",")
    missing = np.genfromtxt(StringIO("1,\n3,4\n"), delimiter=",")
    print(regular)
    print(missing)


if __name__ == "__main__":
    main()
