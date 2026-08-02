"""用途：让 data2.txt 排在 data10.txt 前，而不是按纯字符串排序。

示例输入：``data10.txt data2.txt data1.txt``。
示例输出：``['data1.txt', 'data2.txt', 'data10.txt']``。
复杂度：构造键 O(名字总长度)，排序 O(n log n)。
常见陷阱：键中数字和文本类型不能在同一位置直接互比；统一键结构。
"""

from pathlib import Path
import re
import tempfile


def natural_key(path: Path) -> tuple[tuple[int, object], ...]:
    parts = re.split(r"(\d+)", path.name.casefold())
    return tuple(
        (0, int(part)) if part.isdigit() else (1, part)
        for part in parts
        if part
    )


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        for name in ("data10.txt", "data2.txt", "data1.txt"):
            (root / name).touch()
        ordered = sorted(root.iterdir(), key=natural_key)
        print([path.name for path in ordered])


if __name__ == "__main__":
    main()
