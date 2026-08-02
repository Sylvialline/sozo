"""用途：用生成器表达式惰性处理数据，避免先创建完整中间列表。
示例输入：1..5。
示例输出：平方和 55；展示生成器只能顺序消费一次。
复杂度：求和 O(n)，生成器自身 O(1) 额外空间。
常见陷阱：生成器是一次性的；创建时不执行主体；需要复用应重新创建或转为 list。
"""


def main() -> None:
    total = sum(x * x for x in range(1, 6))
    print("sum of squares:", total)

    squares = (x * x for x in range(4))
    print("first:", next(squares))
    print("rest:", list(squares))
    print("already exhausted:", list(squares))

    # 函数只有一个参数时可省略额外括号：
    print("any > 3:", any(x > 3 for x in [1, 2, 5]))


if __name__ == "__main__":
    main()
