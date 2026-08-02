"""用途：用 permutations 枚举有顺序、无重复位置的排列。
示例输入："ABC" 取长度 2。
示例输出：AB、AC、BA、BC、CA、CB。
复杂度：产生 n!/(n-r)! 项，每项构造 O(r)，数量可能爆炸。
常见陷阱：输入有重复值会产生重复排列；需要唯一值时先去重并明确是否改变语义。
"""

from itertools import permutations


def main() -> None:
    print("length 2:", ["".join(p) for p in permutations("ABC", 2)])
    print("all:", ["".join(p) for p in permutations("ABC")])

    duplicated = list(permutations("AAB"))
    unique = sorted(set(duplicated))
    print("raw count:", len(duplicated))
    print("unique count:", len(unique), unique)


if __name__ == "__main__":
    main()
