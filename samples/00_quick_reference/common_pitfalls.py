"""用途：用可运行断言演示 C++ 使用者最容易踩到的 Python 陷阱。

示例输入：脚本内置二维数组、可变参数和浅拷贝示例。
示例输出：打印共享行、排序返回值、浅拷贝和取整差异。
复杂度：示例均为 O(n) 或更小。
常见陷阱：共享二维行、可变默认参数、浅拷贝、递归深度、相对路径见注释。
"""

from copy import deepcopy
from pathlib import Path


def unsafe_append(value: int, result: list[int] = []) -> list[int]:
    """反例：默认列表只在函数定义时创建一次。"""
    result.append(value)
    return result


def safe_append(value: int, result: list[int] | None = None) -> list[int]:
    """正例：用 None 延迟创建可变对象。"""
    if result is None:
        result = []
    result.append(value)
    return result


def main() -> None:
    bad_grid = [[0] * 3] * 2
    bad_grid[0][0] = 9
    good_grid = [[0] * 3 for _ in range(2)]
    good_grid[0][0] = 9
    print("shared rows:", bad_grid, "; independent rows:", good_grid)

    values = [3, 1, 2]
    returned = values.sort()
    print("sort result:", returned, "; list:", values)

    shallow = [[1], [2]]
    shallow_copy = shallow.copy()
    deep_copy = deepcopy(shallow)
    shallow[0].append(9)
    print("shallow:", shallow_copy, "; deep:", deep_copy)

    print("mutable default:", unsafe_append(1), unsafe_append(2))
    print("safe default:", safe_append(1), safe_append(2))
    print("floor division:", -3 // 2, "; truncation toward zero:", int(-3 / 2))
    print("string replace creates new:", "abc".replace("a", "A"))

    # 相对路径基于 Path.cwd()；脚本旁资源应从 __file__ 推导。
    print("cwd:", Path.cwd())
    print("script dir:", Path(__file__).resolve().parent)
    print("提醒：深 DFS 优先写迭代版；Python 默认递归深度通常只有约一千层。")


if __name__ == "__main__":
    main()
