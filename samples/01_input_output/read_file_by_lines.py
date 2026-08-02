"""用途：逐行读取文本，适合不应整体载入内存的大文件。

示例输入：三行 ``10``、空行、``20``。
示例输出：``values=[10, 20] sum=30``。
复杂度：时间 O(文件大小)；若边读边处理可把额外空间降到 O(1)。
常见陷阱：行尾含换行符；``strip()`` 会同时删除行首尾所有空白。
"""

from pathlib import Path
import tempfile


def read_nonempty_integers(path: Path) -> list[int]:
    values: list[int] = []
    with path.open(encoding="utf-8") as stream:
        for raw_line in stream:
            line = raw_line.strip()
            if line:
                values.append(int(line))
    return values


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "numbers.txt"
        path.write_text("10\n\n20\n", encoding="utf-8", newline="\n")
        values = read_nonempty_integers(path)
        print(f"values={values} sum={sum(values)}")


if __name__ == "__main__":
    main()
