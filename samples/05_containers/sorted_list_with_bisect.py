"""用途：用 bisect 在有序 list 中二分查找并维持排序。
示例输入：[1, 2, 2, 4]，查询/插入 2 和 3。
示例输出：2 的区间 [1,3)，插入后 [1,2,2,3,4]。
复杂度：二分查询 O(log n)，insort/中间删除因搬移元素为 O(n)。
常见陷阱：这不是平衡树；重复值用 bisect_left/right 区分；序列必须始终有序。
"""

from bisect import bisect_left, bisect_right, insort


def erase_one(values: list[int], target: int) -> bool:
    index = bisect_left(values, target)
    if index == len(values) or values[index] != target:
        return False
    values.pop(index)
    return True


def main() -> None:
    values = [1, 2, 2, 4]
    left = bisect_left(values, 2)       # lower_bound
    right = bisect_right(values, 2)     # upper_bound
    print("range of 2:", left, right)
    insort(values, 3)
    print("after insert:", values)
    print("erase 2:", erase_one(values, 2), values)
    print("erase 9:", erase_one(values, 9), values)


if __name__ == "__main__":
    main()
