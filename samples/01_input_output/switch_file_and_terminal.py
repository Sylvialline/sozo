"""用途：用布尔开关（或谨慎的自动检测）在文件和终端输入之间切换。

示例输入：调试文件内容 ``4 10 20 30 40``。
示例输出：``source=file count=4 sum=100``。
复杂度：读取和拆分为 O(文件字符数)，整数列表占 O(n)。
常见陷阱：自动读到遗留 input.txt 会悄悄使用旧数据；显式开关更安全。
"""

from io import StringIO
from pathlib import Path
import tempfile
from typing import TextIO


DEBUG_INPUT = True


def read_source(
    debug_input: bool,
    input_path: Path,
    terminal: TextIO,
) -> tuple[str, str]:
    if debug_input:
        return input_path.read_text(encoding="utf-8"), "file"
    return terminal.read(), "terminal"


def read_auto(input_path: Path, terminal: TextIO) -> tuple[str, str]:
    """存在 input.txt 就读文件，否则读终端；方便但可能误读遗留文件。"""
    if input_path.is_file():
        return input_path.read_text(encoding="utf-8"), "auto-file"
    return terminal.read(), "auto-terminal"


def summarize(text: str) -> tuple[int, int]:
    count, *values = map(int, text.split())
    if count != len(values):
        raise ValueError("数量与数据个数不一致")
    return count, sum(values)


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        input_path = Path(temporary) / "input.txt"
        input_path.write_text("4 10 20 30 40\n", encoding="utf-8")
        text, source = read_source(DEBUG_INPUT, input_path, StringIO("2 7 8\n"))
        count, total = summarize(text)
        print(f"source={source} count={count} sum={total}")
        auto_text, auto_source = read_auto(input_path, StringIO("1 99\n"))
        assert summarize(auto_text) == (4, 100)
        print("automatic detection:", auto_source, "(beware stale files)")


if __name__ == "__main__":
    main()
