"""用途：只列出指定目录的直接子项，不进入子目录。

示例输入：目录含 ``a.txt``、``b.csv`` 和子目录 ``nested``。
示例输出：``files=['a.txt', 'b.csv'] dirs=['nested']``。
复杂度：设直接子项数为 n，遍历 O(n)，排序 O(n log n)。
常见陷阱：``iterdir()`` 顺序由文件系统决定；需要稳定输出就显式 sorted。
"""

from pathlib import Path
import tempfile


def list_children(root: Path) -> tuple[list[str], list[str]]:
    children = sorted(root.iterdir(), key=lambda path: path.name.casefold())
    files = [path.name for path in children if path.is_file()]
    directories = [path.name for path in children if path.is_dir()]
    return files, directories


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        (root / "a.txt").write_text("a", encoding="utf-8")
        (root / "b.csv").write_text("b", encoding="utf-8")
        (root / "nested").mkdir()
        files, directories = list_children(root)
        print(f"files={files} dirs={directories}")


if __name__ == "__main__":
    main()
