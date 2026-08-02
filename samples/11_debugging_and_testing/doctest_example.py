"""把短小输入/输出例子直接写进函数 docstring 并用 ``doctest`` 校验。

示例输入：``python doctest_example.py``。
示例输出：doctest 报告所有示例通过，最后打印 ``failures: 0``。
复杂度：``chunks`` 复制全部元素，时间和输出空间均为 O(n)。
常见陷阱：doctest 比较文本表示，浮点数、dict 顺序和空白变化可能造成脆弱测试。
"""

import doctest
from typing import TypeVar

T = TypeVar("T")


def chunks(values: list[T], size: int) -> list[list[T]]:
    """把列表按固定大小分块。

    >>> chunks([1, 2, 3, 4, 5], 2)
    [[1, 2], [3, 4], [5]]
    >>> chunks([], 3)
    []
    >>> chunks([1], 0)
    Traceback (most recent call last):
    ...
    ValueError: size must be positive
    """
    if size <= 0:
        raise ValueError("size must be positive")
    return [values[index : index + size] for index in range(0, len(values), size)]


def main() -> None:
    result = doctest.testmod(verbose=True)
    print("failures:", result.failed)
    print("attempted:", result.attempted)


if __name__ == "__main__":
    main()
