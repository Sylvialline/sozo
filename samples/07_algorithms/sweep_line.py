"""用途：扫描线计算半开区间 [start,end) 的最大同时覆盖数及开始位置。
示例输入：[(1,4),(2,5),(4,6)]。
示例输出：最大覆盖 2，首次达到位置 2。
复杂度：聚合事件 O(n)，排序不同坐标 O(k log k)，空间 O(k)。
常见陷阱：端点语义必须统一；先按坐标聚合增减可正确处理同点开始/结束。
"""

from collections import defaultdict


def maximum_overlap(intervals: list[tuple[int, int]]) -> tuple[int, int | None]:
    delta: defaultdict[int, int] = defaultdict(int)
    for start, end in intervals:
        if start > end:
            raise ValueError("start 不能大于 end")
        if start == end:
            continue
        delta[start] += 1
        delta[end] -= 1

    current = best = 0
    best_position = None
    for position in sorted(delta):
        current += delta[position]
        if current > best:
            best = current
            best_position = position
    return best, best_position


def main() -> None:
    intervals = [(1, 4), (2, 5), (4, 6)]
    print("maximum, first position:", maximum_overlap(intervals))
    print("empty:", maximum_overlap([]))


if __name__ == "__main__":
    main()
