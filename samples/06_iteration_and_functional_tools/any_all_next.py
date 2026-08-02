"""用途：用 any/all 做短路判定，用 next(generator, default) 实现 find_if。
示例输入：[2, 4, 7, 8]。
示例输出：存在奇数 True、全为正数 True、首个奇数 7。
复杂度：最坏 O(n)，短路时可能提前结束；额外空间 O(1)。
常见陷阱：any([]) 为 False、all([]) 为 True；next(iterator) 无默认值时可能 StopIteration。
"""


def main() -> None:
    values = [2, 4, 7, 8]
    print("has odd:", any(value % 2 for value in values))
    print("all positive:", all(value > 0 for value in values))
    first_odd = next((value for value in values if value % 2), None)
    print("first odd:", first_odd)
    missing = next((value for value in values if value < 0), "not found")
    print("negative:", missing)
    print("empty:", any([]), all([]))


if __name__ == "__main__":
    main()
