"""用途：收集可读性良好的 Python 常用一行写法。

示例输入：内置 ``[3, 1, 4, 1, 5]``。
示例输出：去重、计数、分组、转置和安全查找的结果。
复杂度：除排序 O(n log n) 外，多数写法为 O(n)。
常见陷阱：一行式不应塞入复杂副作用；生成器只能消费一次。
"""

from collections import Counter, defaultdict


def main() -> None:
    values = [3, 1, 4, 1, 5]

    print("ordered unique:", list(dict.fromkeys(values)))
    print("frequencies:", Counter(values).most_common())
    print("argmax:", max(range(len(values)), key=values.__getitem__))
    print("first even:", next((x for x in values if x % 2 == 0), None))
    print("all positive:", all(x > 0 for x in values))
    print("any duplicate:", len(values) != len(set(values)))
    print("clamp 9 to [0, 5]:", max(0, min(9, 5)))
    print("flatten:", [x for row in [[1, 2], [3], [4, 5]] for x in row])
    print("transpose:", [list(col) for col in zip(*[[1, 2], [3, 4]])])

    groups: defaultdict[int, list[int]] = defaultdict(list)
    for value in values:
        groups[value % 2].append(value)
    print("group by parity:", dict(groups))


if __name__ == "__main__":
    main()
