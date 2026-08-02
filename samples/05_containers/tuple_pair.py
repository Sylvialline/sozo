"""用途：用 tuple 表示 C++ pair / 不可变定长记录并进行解包。
示例输入：(2, "Tokyo") 与若干 (分数, 名字)。
示例输出：解包字段，以及按元组字典序排序的记录。
复杂度：创建/解包定长元组 O(1)；排序 n 条记录 O(n log n)。
常见陷阱：tuple 不可修改；(1) 是整数，单元素元组必须写成 (1,)。
"""


def main() -> None:
    record = (2, "Tokyo")
    rank, city = record                 # 类似结构化绑定
    print(f"rank={rank} city={city}")

    scores = [(90, "Bob"), (90, "Alice"), (85, "Carol")]
    print("lexicographic:", sorted(scores))
    print("name first:", sorted(scores, key=lambda item: item[1]))

    first, *middle, last = (10, 20, 30, 40)
    print("unpack:", first, middle, last)
    print("single tuple:", (1,))


if __name__ == "__main__":
    main()
