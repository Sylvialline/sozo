"""用途：组合正则、普通子字符串和扩展名筛选批处理文件。
示例输入：data1.txt、data2.csv、note.txt
示例输出：data1.txt
复杂度：O(F × 文件名长度)。
陷阱：re.fullmatch 与 re.search 不同；后者只要求局部匹配。
"""

import re
from pathlib import Path


def matching(
    paths: list[Path],
    regex: str,
    substring: str,
    suffix: str,
) -> list[Path]:
    pattern = re.compile(regex)
    return [
        path
        for path in paths
        if path.suffix.casefold() == suffix.casefold()
        and substring in path.name
        and pattern.fullmatch(path.name)
    ]


def main() -> None:
    paths = list(map(Path, ["data1.txt", "data2.csv", "note.txt"]))
    print([p.name for p in matching(paths, r"data\d+\.txt", "data", ".txt")])


if __name__ == "__main__":
    main()
