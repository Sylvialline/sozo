"""用途：将同一批结果同时打印到终端并保存到文件。

示例输入：``["alpha: 3", "beta: 5"]``。
示例输出：终端和 output.txt 都出现这两行。
复杂度：O(总输出字符数)，文件内容占 O(总字符数)。
常见陷阱：print 默认使用平台换行；需稳定文件格式时显式 newline="\\n"。
"""

from pathlib import Path
import tempfile
from typing import Iterable


def print_and_save(lines: Iterable[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for line in lines:
            print(line)
            print(line, file=stream)


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        output = Path(temporary) / "output.txt"
        print_and_save(["alpha: 3", "beta: 5"], output)
        assert output.read_text(encoding="utf-8") == "alpha: 3\nbeta: 5\n"


if __name__ == "__main__":
    main()
