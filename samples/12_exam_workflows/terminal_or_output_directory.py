"""用途：组合“输入文件 + 输出目录”，也可把同一结果直接打印到终端。
示例输入：python terminal_or_output_directory.py data/input1.txt --output-dir results
示例输出：results/input1.out；省略 --output-dir 时把求和结果打印到终端。
复杂度：读取、解析和写出均为 O(文件大小)。
陷阱：相对路径基于当前工作目录；write_text 会覆盖同名旧输出文件。
"""

import argparse
from pathlib import Path


def solve(text: str) -> str:
    return str(sum(map(int, text.split())))


def emit(result: str, output_dir: Path | None, input_path: Path | None) -> Path | None:
    if output_dir is None:
        print(result)
        return None
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = input_path.with_suffix(".out").name if input_path else "answer.out"
    path = output_dir / filename
    path.write_text(result + "\n", encoding="utf-8")
    print(f"written: {path}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    text = (
        args.input.read_text(encoding="utf-8")
        if args.input is not None
        else "1 2 3"
    )
    emit(solve(text), args.output_dir, args.input)


if __name__ == "__main__":
    main()
