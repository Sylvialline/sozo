"""用途：清理行首尾空白，并按空白或指定分隔符切分文本。

示例输入：``"  alpha   beta \\n gamma, delta ,, epsilon "``。
示例输出：``['alpha', 'beta']`` 与 ``['gamma', 'delta', 'epsilon']``。
复杂度：O(文本长度)。
常见陷阱：无参数 ``split()`` 会合并连续空白；``split(',')`` 会保留空字段。
"""


def main() -> None:
    text = "  alpha   beta \n gamma, delta ,, epsilon "
    first, second = text.splitlines()
    whitespace_fields = first.strip().split()
    comma_fields = [field.strip() for field in second.split(",") if field.strip()]
    print(whitespace_fields)
    print(comma_fields)


if __name__ == "__main__":
    main()
