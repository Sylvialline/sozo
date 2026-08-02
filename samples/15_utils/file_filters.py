"""用途：组合扩展名、子字符串和正则表达式筛选文件名。
示例输入：data12.txt、note.md；suffixes={".txt"}，regex=r"data\\d+\\.txt"
示例输出：data12.txt
复杂度：每个路径 O(文件名长度)；正则复杂度取决于表达式。
陷阱：re.fullmatch 要求整个文件名匹配；扩展名比较应统一大小写。
"""

import re
from collections.abc import Iterable
from pathlib import Path


def filter_paths(
    paths: Iterable[Path],
    *,
    suffixes: set[str] | None = None,
    substring: str | None = None,
    regex: str | None = None,
) -> list[Path]:
    normalized = {suffix.casefold() for suffix in suffixes} if suffixes else None
    pattern = re.compile(regex) if regex else None
    result = []

    for path in paths:
        name = path.name
        if normalized is not None and path.suffix.casefold() not in normalized:
            continue
        if substring is not None and substring not in name:
            continue
        if pattern is not None and pattern.fullmatch(name) is None:
            continue
        result.append(path)

    return result


def main() -> None:
    paths = map(Path, ["data12.txt", "data2.csv", "note.md"])
    selected = filter_paths(
        paths,
        suffixes={".txt"},
        substring="data",
        regex=r"data\d+\.txt",
    )
    print([path.name for path in selected])


if __name__ == "__main__":
    main()
