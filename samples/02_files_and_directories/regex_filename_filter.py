"""用途：用正则表达式精确筛选数据文件名。

示例输入：``data1.txt data02.txt metadata1.txt data3.csv``。
示例输出：``['data1.txt', 'data02.txt']``。
复杂度：扫描 n 个名字约 O(名字总长度)，排序 O(k log k)。
常见陷阱：用 ``fullmatch`` 匹配整个文件名；``match`` 只要求从开头匹配。
"""

from pathlib import Path
import re
import tempfile


PATTERN = re.compile(r"data\d+\.txt", re.IGNORECASE)


def filter_names(root: Path) -> list[str]:
    return sorted(
        path.name
        for path in root.iterdir()
        if path.is_file() and PATTERN.fullmatch(path.name)
    )


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        for name in ("data1.txt", "data02.txt", "metadata1.txt", "data3.csv"):
            (root / name).touch()
        print(filter_names(root))


if __name__ == "__main__":
    main()
