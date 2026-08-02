"""用途：用 itertools.accumulate 计算前缀和、前缀最大值和自定义累积。
示例输入：[3, -1, 4, 2]，查询半开区间 [1,4)。
示例输出：前缀和 [0,3,2,6,8]，区间和 5。
复杂度：构造 O(n)、区间和 O(1)、保存前缀数组 O(n)。
常见陷阱：initial=0 可让 prefix[r]-prefix[l] 直接对应 [l,r)；accumulate 返回迭代器。
"""

from itertools import accumulate
from operator import mul


def main() -> None:
    values = [3, -1, 4, 2]
    prefix = list(accumulate(values, initial=0))
    left, right = 1, 4
    print("prefix:", prefix)
    print("range sum:", prefix[right] - prefix[left])
    print("prefix max:", list(accumulate(values, max)))
    print("prefix product:", list(accumulate([2, 3, 4], mul, initial=1)))


if __name__ == "__main__":
    main()
