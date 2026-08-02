"""用途：排序并合并重叠或接触的区间。
示例输入：[(5,7),(1,3),(2,4),(8,8),(7,9)]。
示例输出：[(1,4),(5,9)]（接触端点也合并）。
复杂度：排序 O(n log n)，扫描 O(n)，结果空间 O(n)。
常见陷阱：先明确闭区间/半开区间语义；本例用 left <= last_right 合并接触端点。
"""


def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if any(left > right for left, right in intervals):
        raise ValueError("区间左端点不能大于右端点")
    merged: list[list[int]] = []
    for left, right in sorted(intervals):
        if not merged or left > merged[-1][1]:
            merged.append([left, right])
        else:
            merged[-1][1] = max(merged[-1][1], right)
    return [(left, right) for left, right in merged]


def main() -> None:
    intervals = [(5, 7), (1, 3), (2, 4), (8, 8), (7, 9)]
    print("merged:", merge_intervals(intervals))
    print("empty:", merge_intervals([]))


if __name__ == "__main__":
    main()
