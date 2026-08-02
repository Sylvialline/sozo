"""用途：集中展示考试代码最常用的 Python 基础语法。

示例输入：内置文本 ``"4 7 2 7 1"``。
示例输出：``sum=17 min=1 odd=[7, 7, 1]`` 等摘要。
复杂度：解析、推导式与聚合均为 O(n)。
常见陷阱：``//`` 对负数向下取整；字符串不可修改；函数关键字参数依赖参数名。
"""


def summarize(values: list[int], *, limit: int = 3) -> tuple[int, int, list[int]]:
    """``limit`` 是仅能用关键字传入的参数。"""
    total = sum(values)
    minimum = min(values, default=0)
    odds = [x for x in values if x % 2]
    return total, minimum, odds[:limit]


def main() -> None:
    text = "4 7 2 7 1"
    count, *values = map(int, text.split())
    assert count == len(values)

    total, minimum, odds = summarize(values, limit=4)
    print(f"sum={total} min={minimum} odd={odds}")

    for index, value in enumerate(values):
        if value == minimum:
            print("minimum index:", index)
            break

    matrix = [[r * 10 + c for c in range(3)] for r in range(2)]
    transposed = [list(column) for column in zip(*matrix)]
    print("matrix:", matrix)
    print("transpose:", transposed)
    print("-3 // 2 =", -3 // 2, "; -3 / 2 =", -3 / 2)


if __name__ == "__main__":
    main()
