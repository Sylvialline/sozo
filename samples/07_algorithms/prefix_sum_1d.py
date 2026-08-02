"""用途：构造一维前缀和，O(1) 查询任意半开区间 [left, right)。
示例输入：[3,-1,4,2]，查询 [1,4)。
示例输出：prefix=[0,3,2,6,8]，区间和 5。
复杂度：预处理 O(n)、每次查询 O(1)、空间 O(n)。
常见陷阱：统一使用半开区间；prefix 长度是 n+1，答案为 prefix[r]-prefix[l]。
"""

from itertools import accumulate


def build_prefix(values: list[int]) -> list[int]:
    return list(accumulate(values, initial=0))


def range_sum(prefix: list[int], left: int, right: int) -> int:
    if not 0 <= left <= right < len(prefix):
        raise IndexError("区间必须满足 0 <= left <= right <= n")
    return prefix[right] - prefix[left]


def main() -> None:
    values = [3, -1, 4, 2]
    prefix = build_prefix(values)
    print("prefix:", prefix)
    print("[1, 4):", range_sum(prefix, 1, 4))
    print("empty:", range_sum(prefix, 2, 2))


if __name__ == "__main__":
    main()
