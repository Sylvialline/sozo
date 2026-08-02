"""用途：完整演示可筛选、递归、计时、容错和多种输出方式的考试批处理框架。
示例输入：python full_exam_template.py data --regex "data\\d+\\.txt" --output-dir out
示例输出：逐文件答案/耗时，以及文件数、成功数、失败数和总耗时。
复杂度：文件发现 O(F log F)，求解示例 O(所有输入字符数)。
陷阱：相对路径基于当前工作目录；--continue-on-error 才会跳过坏文件继续。
"""

import argparse
import sys
import tempfile
from collections.abc import Iterable
from pathlib import Path

UTILS_DIR = Path(__file__).resolve().parents[1] / "15_utils"
sys.path.insert(0, str(UTILS_DIR))
from io_runner import RunConfig, run_batch  # noqa: E402


def solve(text: str) -> Iterable[str]:
    """示例求解器；可替换为返回标量、列表或生成器的题目逻辑。"""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    yield f"非空行数：{len(lines)}"
    yield f"总字符数：{sum(map(len, lines))}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", nargs="?", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--merged-output", type=Path)
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--regex")
    parser.add_argument("--contains")
    parser.add_argument("--suffix", action="append")
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    return parser


def execute(args: argparse.Namespace, input_dir: Path) -> None:
    config = RunConfig(
        input_dir=input_dir,
        output_dir=args.output_dir,
        merged_output=args.merged_output,
        recursive=args.recursive,
        regex=args.regex,
        substring=args.contains,
        suffixes=tuple(args.suffix or [".txt"]),
        print_terminal=not args.quiet,
        continue_on_error=args.continue_on_error,
        debug=args.debug,
    )
    run_batch(solve, config)


def main() -> None:
    args = build_parser().parse_args()
    if args.input_dir is not None:
        execute(args, args.input_dir)
        return

    print("未指定目录，运行内置临时样例。\n")
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        (root / "data2.txt").write_text("alpha\nbeta", encoding="utf-8")
        (root / "data10.txt").write_text("gamma", encoding="utf-8")
        execute(args, root)


if __name__ == "__main__":
    main()
