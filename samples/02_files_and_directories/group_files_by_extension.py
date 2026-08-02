"""用途：按不区分大小写的扩展名对文件分组。

示例输入：``a.TXT b.txt table.csv README``。
示例输出：``{'<none>': ['README'], '.csv': [...], '.txt': [...]}``。
复杂度：分组 O(n)，组内排序总计至多 O(n log n)。
常见陷阱：``Path.suffix`` 只返回最后一个后缀；多重后缀可查看 ``suffixes``。
"""

from collections import defaultdict
from pathlib import Path
import tempfile


def group_by_extension(paths: list[Path]) -> dict[str, list[str]]:
    groups: defaultdict[str, list[str]] = defaultdict(list)
    for path in paths:
        extension = path.suffix.casefold() or "<none>"
        groups[extension].append(path.name)
    return {
        extension: sorted(names, key=str.casefold)
        for extension, names in sorted(groups.items())
    }


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        for name in ("a.TXT", "b.txt", "table.csv", "README"):
            (root / name).touch()
        print(group_by_extension(list(root.iterdir())))


if __name__ == "__main__":
    main()
