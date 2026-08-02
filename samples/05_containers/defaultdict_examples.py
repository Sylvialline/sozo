"""用途：用 defaultdict 简化分组、计数和邻接表构造。
示例输入：[("A", 3), ("B", 2), ("A", 5)]。
示例输出：A -> [3, 5]、B -> [2]，以及字符计数。
复杂度：构造 O(n)，单次访问平均 O(1)，保存数据 O(n)。
常见陷阱：读取 missing[key] 也会插入默认值；仅查询时可优先用普通 dict.get。
"""

from collections import defaultdict


def main() -> None:
    pairs = [("A", 3), ("B", 2), ("A", 5)]
    grouped: defaultdict[str, list[int]] = defaultdict(list)
    for key, value in pairs:
        grouped[key].append(value)

    counts: defaultdict[str, int] = defaultdict(int)
    for char in "abac":
        counts[char] += 1

    for key in sorted(grouped):
        print(key, "->", grouped[key])
    print("counts:", dict(counts))
    print("before missing access:", "Z" in grouped)
    _ = grouped["Z"]                    # 会插入 Z: []
    print("after missing access:", "Z" in grouped)


if __name__ == "__main__":
    main()
