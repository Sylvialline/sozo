"""用途：用 bisect 实现 lower_bound、upper_bound、计数和前驱/后继查询。
示例输入：有序数组 [1,2,2,2,5,8]，目标 2 和 4。
示例输出：2 的区间 [1,4)、出现 3 次；4 的插入位置 4。
复杂度：每次二分 O(log n)，不复制输入时额外空间 O(1)。
常见陷阱：输入必须有序；bisect 返回插入下标而非“找到/没找到”；切片会复制。
"""

from bisect import bisect_left, bisect_right


def equal_range(values: list[int], target: int) -> tuple[int, int]:
    return bisect_left(values, target), bisect_right(values, target)


def find_exact(values: list[int], target: int) -> int | None:
    index = bisect_left(values, target)
    return index if index < len(values) and values[index] == target else None


def main() -> None:
    values = [1, 2, 2, 2, 5, 8]
    left, right = equal_range(values, 2)
    print("range:", left, right, "count:", right - left)
    print("find 5:", find_exact(values, 5))
    print("find 4:", find_exact(values, 4))

    insertion = bisect_left(values, 4)
    predecessor = values[insertion - 1] if insertion > 0 else None
    successor = values[insertion] if insertion < len(values) else None
    print("for 4:", insertion, predecessor, successor)


if __name__ == "__main__":
    main()
