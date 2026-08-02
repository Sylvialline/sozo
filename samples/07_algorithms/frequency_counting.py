"""用途：用 Counter 统计频率，并处理众数、相同频率下的稳定排序。
示例输入：[4,1,4,2,1,4]。
示例输出：频率 {1:2,2:1,4:3}，众数 4。
复杂度：统计平均 O(n)，对不同键排序 O(k log k)，空间 O(k)。
常见陷阱：dict/Counter 是哈希结构；most_common 的并列顺序依赖首次出现顺序。
"""

from collections import Counter


def frequencies(values: list[int]) -> list[tuple[int, int]]:
    counts = Counter(values)
    return sorted(counts.items())       # 确定性的按值输出


def main() -> None:
    values = [4, 1, 4, 2, 1, 4]
    counts = Counter(values)
    print("frequencies:", frequencies(values))
    mode, count = min(counts.items(), key=lambda item: (-item[1], item[0]))
    print("mode:", mode, "count:", count)
    print("exactly twice:", sorted(value for value, c in counts.items() if c == 2))


if __name__ == "__main__":
    main()
