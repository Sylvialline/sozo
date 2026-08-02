"""用途：用 sorted/list.sort 的 key、reverse 和稳定排序处理记录。
示例输入：[("Bob",90),("Alice",90),("Carol",85)]。
示例输出：按分数降序、姓名升序；以及稳定的多关键字排序。
复杂度：Timsort 为 O(n log n)，对已有序数据可接近 O(n)，复制排序需 O(n)。
常见陷阱：list.sort() 返回 None；reverse=True 会反转所有键，混合方向常写成 (-score,name)。
"""

from operator import itemgetter


def main() -> None:
    records = [("Bob", 90), ("Alice", 90), ("Carol", 85)]
    ranked = sorted(records, key=lambda item: (-item[1], item[0]))
    print("ranked:", ranked)

    by_name = sorted(records, key=itemgetter(0))
    print("by name:", by_name)

    # 稳定排序：后执行的键是主键。
    stable = records.copy()
    stable.sort(key=itemgetter(0))
    stable.sort(key=itemgetter(1), reverse=True)
    print("stable two-pass:", stable)


if __name__ == "__main__":
    main()
