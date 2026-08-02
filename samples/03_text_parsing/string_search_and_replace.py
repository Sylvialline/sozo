"""用途：展示普通字符串查找/替换与基于正则回调的替换。

示例输入：``"cat 12, cat 7"``。
示例输出：cat 出现 2 次；替换为 dog；数字翻倍成 24 和 14。
复杂度：普通操作 O(n)；本正则替换通常 O(n)。
常见陷阱：``find`` 未找到返回 -1；``index`` 未找到抛 ValueError；字符串不可变。
"""

import re


def main() -> None:
    text = "cat 12, cat 7"
    print("first:", text.find("cat"), "count:", text.count("cat"))
    print("plain:", text.replace("cat", "dog"))
    doubled = re.sub(r"\d+", lambda match: str(int(match.group()) * 2), text)
    print("regex:", doubled)
    print("original unchanged:", text)


if __name__ == "__main__":
    main()
