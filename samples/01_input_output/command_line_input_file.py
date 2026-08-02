"""用途：支持 ``python script.py input.txt``，无参数时改读标准输入。

示例输入：文件内容或标准输入 ``3 6 7 8``。
示例输出：``count=3 sum=21``。
复杂度：读取为 O(输入大小)，解析前 n 个整数为 O(n)。
常见陷阱：相对路径基于当前工作目录；只消费格式声明的数据，后续可另行解析。
"""

import argparse
from pathlib import Path
import sys


SAMPLE = "3 6 7 8\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", nargs="?", type=Path)
    return parser.parse_args(argv)


def load_text(input_file: Path | None) -> str:
    if input_file is not None:
        return input_file.read_text(encoding="utf-8")
    if sys.stdin.isatty():
        return SAMPLE
    return sys.stdin.read() or SAMPLE


def parse_counted_integers(text: str) -> list[int]:
    tokens = iter(text.split())
    first = next(tokens, None)
    if first is None:
        raise ValueError("输入为空")
    count = int(first)
    try:
        return [int(next(tokens)) for _ in range(count)]
    except StopIteration as error:
        raise ValueError(f"声明 {count} 个整数，但输入提前结束") from error


def main() -> None:
    args = parse_args()
    values = parse_counted_integers(load_text(args.input_file))
    print(f"count={len(values)} sum={sum(values)}")


if __name__ == "__main__":
    main()
