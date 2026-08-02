"""用途：速查 set（哈希集合，近似 unordered_set）与集合运算。
示例输入：{3, 1, 4} 和 {1, 5}。
示例输出：并集、交集、差集及排序后的元素。
复杂度：成员查询/增删平均 O(1)、最坏 O(n)；排序输出 O(n log n)。
常见陷阱：set 无序且元素必须可哈希；标准库没有 C++ set 那样的平衡树有序集合。
"""


def main() -> None:
    left = {3, 1, 4}
    right = {1, 5}
    left.add(2)
    left.discard(9)             # 不存在也不报错；remove(9) 会 KeyError
    removed = left.pop()        # 删除任意元素，不能假定是哪一个
    left.add(removed)

    print("contains 4:", 4 in left)
    print("union:", sorted(left | right))
    print("intersection:", sorted(left & right))
    print("difference:", sorted(left - right))
    copied = left.copy()
    print("sorted traversal:", *sorted(copied))


if __name__ == "__main__":
    main()
