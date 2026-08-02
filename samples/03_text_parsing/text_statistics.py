"""用途：统计文本的行数、字符数、词频和最长行。

示例输入：``"Red blue\\nred green blue blue\\n"``。
示例输出：``lines=2 chars=29 words=6``，最高词频 ``blue:3``。
复杂度：时间 O(文本长度 + u log u)，空间 O(u)，u 为不同单词数。
常见陷阱：``split()`` 的“单词”定义很粗；本例用正则并用 casefold 忽略大小写。
"""

from collections import Counter
import re


WORD = re.compile(r"[^\W\d_]+", re.UNICODE)


def statistics(text: str) -> dict[str, object]:
    lines = text.splitlines()
    words = [match.group().casefold() for match in WORD.finditer(text)]
    counts = Counter(words)
    longest = max(lines, key=len, default="")
    return {
        "lines": len(lines),
        "characters": len(text),
        "words": len(words),
        "frequencies": sorted(counts.items(), key=lambda item: (-item[1], item[0])),
        "longest_line": longest,
    }


def main() -> None:
    text = "Red blue\nred green blue blue\n"
    info = statistics(text)
    print(
        f"lines={info['lines']} chars={info['characters']} "
        f"words={info['words']}"
    )
    print("frequencies:", info["frequencies"])
    print("longest:", info["longest_line"])


if __name__ == "__main__":
    main()
