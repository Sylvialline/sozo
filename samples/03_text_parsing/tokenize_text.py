"""用途：把自然文本拆成单词、数字和标点 token，并保留位置。

示例输入：``"Room A-12: score=98.5!"``。
示例输出：依次打印 token ``Room A - 12 : score = 98.5 !`` 及跨度。
复杂度：对本正则通常为 O(文本长度)，结果占 O(token 数)。
常见陷阱：``\\w`` 会匹配 Unicode 字符和下划线；词法规则必须按题目定义。
"""

import re


TOKEN = re.compile(r"[^\W\d_]+|\d+(?:\.\d+)?|[^\w\s]", re.UNICODE)


def tokenize(text: str) -> list[tuple[str, int, int]]:
    return [(match.group(), match.start(), match.end()) for match in TOKEN.finditer(text)]


def main() -> None:
    tokens = tokenize("Room A-12: score=98.5!")
    print([token for token, _, _ in tokens])
    print(tokens)


if __name__ == "__main__":
    main()
