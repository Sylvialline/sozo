"""用途：用 heapq.nlargest/nsmallest 取得 top-k，避免完整排序。
示例输入：[8,1,6,3,9,2]，k=3。
示例输出：largest=[9,8,6]，smallest=[1,2,3]。
复杂度：通常 O(n log k)、额外空间 O(k)；k 接近 n 时实现可能改用排序。
常见陷阱：结果是新 list；k<=0 返回空；大量重复值仍会按元素次数保留。
"""

import heapq
from collections.abc import Iterable


def top_k_largest(values: Iterable[int], k: int) -> list[int]:
    if k < 0:
        raise ValueError("k 不能为负")
    return heapq.nlargest(k, values)


def main() -> None:
    values = [8, 1, 6, 3, 9, 2]
    print("largest:", top_k_largest(values, 3))
    print("smallest:", heapq.nsmallest(3, values))

    records = [("A", 70), ("B", 95), ("C", 80)]
    print("best records:", heapq.nlargest(2, records, key=lambda item: item[1]))


if __name__ == "__main__":
    main()
