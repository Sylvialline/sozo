"""用途：用 pathlib 一次读取完整 UTF-8 文本文件。

示例输入：文件内容 ``alpha\\nbeta\\n``。
示例输出：``characters=11 lines=2``。
复杂度：时间与额外内存均为 O(文件大小)。
常见陷阱：大文件不宜 read_text；显式指定 encoding，避免不同 Windows 配置不一致。
"""

from pathlib import Path
import tempfile


def inspect_file(path: Path) -> tuple[int, int]:
    text = path.read_text(encoding="utf-8")
    return len(text), len(text.splitlines())


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "sample.txt"
        path.write_text("alpha\nbeta\n", encoding="utf-8", newline="\n")
        characters, lines = inspect_file(path)
        print(f"characters={characters} lines={lines}")


if __name__ == "__main__":
    main()
