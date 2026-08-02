"""用途：速查 Python list（近似 C++ vector）的常用操作。
示例输入：[3, 1, 4]，追加 1、删除一个 1、查找并排序。
示例输出：排序结果 [1, 3, 4]，下标与值。
复杂度：末尾 append/pop 摊还 O(1)；中间插删、in/index 为 O(n)；排序 O(n log n)。
常见陷阱：pop(0) 是 O(n)；list.sort() 原地修改并返回 None；切片复制是浅拷贝。
"""


def main() -> None:
    values = [3, 1, 4]               # 创建
    values.append(1)                 # 末尾添加
    values.extend([5, 9])            # 添加多个
    values.insert(1, 2)              # 中间插入 O(n)
    last = values.pop()              # 删除并返回末尾元素
    values.remove(1)                 # 删除第一个匹配值；不存在则 ValueError

    print("popped:", last)
    print("contains 4:", 4 in values)
    print("first 4:", values.index(4))
    copied = values.copy()            # 等价于 values[:]
    copied.sort()                     # 返回 None，不要写 copied = copied.sort()
    print("sorted:", copied)
    print("original:", values)
    for index, value in enumerate(copied):
        print(index, value)


if __name__ == "__main__":
    main()
