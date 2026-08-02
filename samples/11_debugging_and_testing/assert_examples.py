"""用 ``assert`` 检查程序内部不变量，而非验证不可信输入。

示例输入：二分查找有序列表 [1,3,5,7] 中的 5，并故意检查无序列表。
示例输出：下标 2；无序列表触发并捕获 AssertionError。
复杂度：二分查找 O(log n)，示例中的有序性断言本身 O(n)。
常见陷阱：``python -O`` 会删除 assert；用户输入校验应显式 ``raise ValueError``。
"""


def binary_search(sorted_values: list[int], target: int) -> int:
    assert all(
        sorted_values[i] <= sorted_values[i + 1]
        for i in range(len(sorted_values) - 1)
    ), "binary_search requires sorted input"
    left, right = 0, len(sorted_values)
    while left < right:
        middle = (left + right) // 2
        if sorted_values[middle] < target:
            left = middle + 1
        else:
            right = middle
    return left if left < len(sorted_values) and sorted_values[left] == target else -1


def parse_positive(text: str) -> int:
    value = int(text)
    if value <= 0:
        raise ValueError("value must be positive")
    return value


def main() -> None:
    print("index:", binary_search([1, 3, 5, 7], 5))
    try:
        binary_search([3, 1, 2], 1)
    except AssertionError as error:
        print("caught invariant failure:", error)
    print("validated input:", parse_positive("8"))


if __name__ == "__main__":
    main()
