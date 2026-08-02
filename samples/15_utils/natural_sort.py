"""用途：按文件名中的数字自然排序。
示例输入：["data10.txt", "data2.txt", "data1.txt"]
示例输出：["data1.txt", "data2.txt", "data10.txt"]
复杂度：排序 O(n log n)，每个键的构造与字符串长度线性相关。
陷阱：普通字符串排序会把 "10" 放在 "2" 前；本例不处理小数或负数语义。
"""

import re
from pathlib import Path
from typing import Any


def natural_key(value: str | Path) -> list[Any]:
    """返回可用于 sorted(key=...) 的自然排序键。"""
    text = value.as_posix() if isinstance(value, Path) else value
    return [
        int(part) if part.isdigit() else part.casefold()
        for part in re.split(r"(\d+)", text)
    ]


def main() -> None:
    names = ["data10.txt", "Data2.txt", "data1.txt"]
    print(sorted(names, key=natural_key))


if __name__ == "__main__":
    main()
