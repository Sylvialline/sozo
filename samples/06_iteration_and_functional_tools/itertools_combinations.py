"""用途：用 combinations 枚举不计顺序且不重复选位置的组合。
示例输入：["A","B","C","D"] 中选 2 个。
示例输出：AB、AC、AD、BC、BD、CD；另示范可重复组合。
复杂度：产生 C(n,r) 项，每项构造 O(r)，总空间可保持 O(r)。
常见陷阱：按“位置”去重，输入有重复值时输出值可能重复；r > n 时为空。
"""

from itertools import combinations, combinations_with_replacement


def main() -> None:
    items = ["A", "B", "C", "D"]
    print("choose 2:", ["".join(pair) for pair in combinations(items, 2)])
    print(
        "with replacement:",
        ["".join(pair) for pair in combinations_with_replacement("AB", 2)],
    )
    for indices in combinations(range(5), 3):
        print("indices:", indices)


if __name__ == "__main__":
    main()
