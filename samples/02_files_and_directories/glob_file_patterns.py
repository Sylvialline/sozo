"""用途：用 pathlib glob 按通配符筛选文件。

示例输入：根目录和子目录中含 txt/csv 文件。
示例输出：打印非递归 ``*.txt`` 与递归 ``**/*.txt`` 的匹配结果。
复杂度：取决于扫描目录项数；排序匹配项另需 O(k log k)。
常见陷阱：glob 不是正则；``*`` 不跨目录，``**`` 才用于递归。
"""

from pathlib import Path
import tempfile


def names(root: Path, pattern: str) -> list[str]:
    return sorted(path.relative_to(root).as_posix() for path in root.glob(pattern))


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        (root / "sub").mkdir()
        for relative in ("a.txt", "b.csv", "sub/c.txt"):
            (root / relative).write_text(relative, encoding="utf-8")
        print("non-recursive:", names(root, "*.txt"))
        print("recursive:", names(root, "**/*.txt"))


if __name__ == "__main__":
    main()
