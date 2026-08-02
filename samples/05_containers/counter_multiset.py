"""用途：用 collections.Counter 表示频率表或 C++ multiset。
示例输入："banana" 和额外元素 "band"。
示例输出：最高频元素、计数、展开元素及 Counter 集合运算。
复杂度：统计 O(n)；单键查询/更新平均 O(1)；most_common(k) 约 O(n log k)。
常见陷阱：访问缺失键返回 0；subtract 会保留零/负计数；+counter 可清除非正项。
"""

from collections import Counter


def main() -> None:
    counts = Counter("banana")
    counts.update("band")               # 添加计数
    counts["a"] -= 1                    # 删除一次
    print("missing:", counts["z"])
    print("top 3:", counts.most_common(3))
    print("expanded:", "".join(sorted(counts.elements())))

    other = Counter("ananas")
    print("multiset union:", counts | other)         # 每键取 max
    print("multiset intersection:", counts & other)  # 每键取 min

    counts.subtract({"x": 2})
    print("negative kept:", counts["x"])
    print("positive only:", +counts)


if __name__ == "__main__":
    main()
