"""精确比较输出，并用 unified diff 定位首尾空白和行差异。

示例输入：expected 为两行，actual 的第二行数字不同且尾部有空格。
示例输出：``match: False``，随后显示以 ``-``/``+`` 标记的差异。
复杂度：比较与生成 diff 均为 O(总字符数)。
常见陷阱：``strip`` 会掩盖首尾空白错误；是否规范化必须由题目要求决定。
"""

from difflib import unified_diff


def compare(expected: str, actual: str) -> tuple[bool, str]:
    if expected == actual:
        return True, ""
    diff = unified_diff(
        expected.splitlines(keepends=True),
        actual.splitlines(keepends=True),
        fromfile="expected",
        tofile="actual",
    )
    return False, "".join(diff)


def normalize_lines(text: str) -> str:
    """可选：忽略每行尾部空白及末尾多余空行。"""
    return "\n".join(line.rstrip() for line in text.rstrip().splitlines()) + "\n"


def main() -> None:
    expected = "count: 3\nsum: 10\n"
    actual = "count: 3\nsum: 11 \n"
    matches, difference = compare(expected, actual)
    print("match:", matches)
    print(difference, end="")
    print("match after normalization:", normalize_lines(expected) == normalize_lines(actual))


if __name__ == "__main__":
    main()
