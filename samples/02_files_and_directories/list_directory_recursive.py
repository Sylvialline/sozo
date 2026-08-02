"""用途：递归列出目录树中的全部文件，并保留相对路径。

示例输入：``a.txt`` 与 ``sub/b.txt``。
示例输出：``['a.txt', 'sub/b.txt']``（显示时统一为正斜杠）。
复杂度：遍历 O(目录项总数)，排序 O(f log f)。
常见陷阱：``rglob('*')`` 会深入所有子目录，真实磁盘根目录可能很慢。
"""

from pathlib import Path
import tempfile


def relative_files(root: Path) -> list[str]:
    paths = (path for path in root.rglob("*") if path.is_file())
    return [path.relative_to(root).as_posix() for path in sorted(paths)]


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        (root / "sub").mkdir()
        (root / "a.txt").write_text("a", encoding="utf-8")
        (root / "sub" / "b.txt").write_text("b", encoding="utf-8")
        print(relative_files(root))


if __name__ == "__main__":
    main()
