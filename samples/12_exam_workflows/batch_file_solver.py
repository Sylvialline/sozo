"""用途：自然排序后批量读取 data*.txt，并逐文件调用 solve(text)。
示例输入：data2.txt="1 2"，data10.txt="3 4"
示例输出：data2.txt: 3；data10.txt: 7
复杂度：发现文件 O(F log F)，求和 O(总数字数)。
陷阱：glob 不保证自然顺序；示例用正则拆分数字排序。
"""

import re
import tempfile
from pathlib import Path


def natural_key(path: Path) -> list[object]:
    return [
        int(part) if part.isdigit() else part
        for part in re.split(r"(\d+)", path.name)
    ]


def solve(text: str) -> int:
    return sum(map(int, text.split()))


def process(directory: Path) -> None:
    for path in sorted(directory.glob("data*.txt"), key=natural_key):
        print(f"{path.name}: {solve(path.read_text(encoding='utf-8'))}")


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        (root / "data10.txt").write_text("3 4", encoding="utf-8")
        (root / "data2.txt").write_text("1 2", encoding="utf-8")
        process(root)


if __name__ == "__main__":
    main()
