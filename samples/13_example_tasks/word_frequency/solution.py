"""用途：批量统计多个文本文件中的词频，忽略大小写并输出前 k 项。
示例输入：input/a.txt 与 input/b.txt。
示例输出：apple 3、banana 3、pear 2。
复杂度：O(文本总长度 + U log U)，U 为不同单词数。
陷阱：Counter.most_common 对同频项依赖首次出现顺序；本例显式按单词排序打破平局。
"""

import argparse
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def count_words(directory: Path) -> Counter[str]:
    counts: Counter[str] = Counter()
    for path in sorted(directory.glob("*.txt")):
        text = path.read_text(encoding="utf-8").casefold()
        counts.update(re.findall(r"[a-z]+", text))
    return counts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", nargs="?", type=Path, default=ROOT / "input")
    parser.add_argument("--top", type=int, default=3)
    args = parser.parse_args()

    counts = count_words(args.input_dir)
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    for word, count in ranked[: args.top]:
        print(word, count)


if __name__ == "__main__":
    main()
