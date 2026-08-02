"""用途：按确定顺序批量读取一个目录中的文本文件。

示例输入：``a.txt`` 内容 A，``b.txt`` 内容 B，另有忽略的 csv。
示例输出：``a.txt -> A``、``b.txt -> B``。
复杂度：扫描 O(n)，排序 O(k log k)，读取 O(匹配文件总大小)。
常见陷阱：不要依赖目录原始顺序；批量读取时要明确编码和递归范围。
"""

from pathlib import Path
import tempfile
from typing import Iterator


def read_matching(root: Path, pattern: str = "*.txt") -> Iterator[tuple[Path, str]]:
    for path in sorted(root.glob(pattern), key=lambda item: item.name.casefold()):
        if path.is_file():
            yield path, path.read_text(encoding="utf-8")


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        (root / "b.txt").write_text("B\n", encoding="utf-8")
        (root / "a.txt").write_text("A\n", encoding="utf-8")
        (root / "ignore.csv").write_text("C\n", encoding="utf-8")
        for path, text in read_matching(root):
            print(f"{path.name} -> {text.strip()}")


if __name__ == "__main__":
    main()
