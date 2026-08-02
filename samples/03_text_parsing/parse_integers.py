"""用途：解析空白分隔整数、逗号分隔整数和逐行整数。

示例输入：``"-3 0 12"`` 与 ``"10, 20, -5"``。
示例输出：``[-3, 0, 12]``、``[10, 20, -5]``、总和 34。
复杂度：O(字符数 + 整数个数)。
常见陷阱：``int("1.0")`` 会 ValueError；数据格式错误应直接暴露而非静默忽略。
"""


def parse_whitespace(text: str) -> list[int]:
    return list(map(int, text.split()))


def parse_commas(text: str) -> list[int]:
    return [int(field.strip()) for field in text.split(",") if field.strip()]


def main() -> None:
    first = parse_whitespace("-3 0 12")
    second = parse_commas("10, 20, -5")
    lines = [int(line) for line in "1\n2\n3\n".splitlines()]
    print(first)
    print(second)
    print("sum:", sum(first + second + lines))


if __name__ == "__main__":
    main()
