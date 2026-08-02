"""用途：在有序数组中用双指针寻找和为 target 的一对元素。
示例输入：[1,2,4,7,11]，target=9。
示例输出：下标 (1,3)，值 (2,7)。
复杂度：扫描 O(n)、额外空间 O(1)；若先排序则另需 O(n log n)。
常见陷阱：此移动规则要求数组已升序；返回排序后下标未必是原数组下标。
"""


def two_sum_sorted(values: list[int], target: int) -> tuple[int, int] | None:
    left, right = 0, len(values) - 1
    while left < right:
        total = values[left] + values[right]
        if total == target:
            return left, right
        if total < target:
            left += 1
        else:
            right -= 1
    return None


def main() -> None:
    values = [1, 2, 4, 7, 11]
    answer = two_sum_sorted(values, 9)
    print("indices:", answer)
    if answer is not None:
        left, right = answer
        print("values:", values[left], values[right])
    print("missing:", two_sum_sorted(values, 100))


if __name__ == "__main__":
    main()
