"""用途：读取一个文件并调用 solve(text)，没有参数时运行内置样例。
示例输入："apple banana apple"
示例输出：words=3, unique=2
复杂度：O(文本长度)。
陷阱：命令行相对路径基于 Path.cwd()，不是脚本所在目录。
"""

import argparse
from pathlib import Path


def solve(text: str) -> str:
    words = text.split()
    return f"words={len(words)}, unique={len(set(words))}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", type=Path)
    args = parser.parse_args()
    text = (
        args.input.read_text(encoding="utf-8")
        if args.input
        else "apple banana apple"
    )
    print(solve(text))


if __name__ == "__main__":
    main()
