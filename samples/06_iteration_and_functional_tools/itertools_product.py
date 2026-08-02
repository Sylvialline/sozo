"""用途：用 itertools.product 生成笛卡尔积、坐标和可重复选择。
示例输入：颜色 [R,G]、编号 [1,2,3]。
示例输出：六个 (颜色, 编号) 组合；二进制长度 3 的八种序列。
复杂度：遍历为 O(各输入长度乘积)，product 迭代器不一次保存全部结果。
常见陷阱：组合数呈指数增长；repeat=k 表示重复整个输入 k 次，不是重复每个元素。
"""

from itertools import product


def main() -> None:
    for color, number in product(["R", "G"], [1, 2, 3]):
        print(color, number)

    bit_strings = ["".join(bits) for bits in product("01", repeat=3)]
    print("bits:", bit_strings)

    grid_points = list(product(range(2), range(3)))
    print("grid:", grid_points)


if __name__ == "__main__":
    main()
