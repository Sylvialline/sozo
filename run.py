from __future__ import annotations

import argparse
import importlib.util
import sys
import traceback
from pathlib import Path
from typing import Any, Callable

from utils import BatchIO


def load_solver(
    solve_path: Path,
    func_name: str = "solve",
) -> Callable[[str], Any]:
    """从任意路径加载 solve.py，不要求目录名是合法 Python 包名。"""
    if not solve_path.is_file():
        raise FileNotFoundError(f"找不到解题文件: {solve_path}")

    module_name = f"_exam_solve_{abs(hash(solve_path.resolve()))}"
    spec = importlib.util.spec_from_file_location(module_name, solve_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"无法加载解题文件: {solve_path}")

    module = importlib.util.module_from_spec(spec)

    # 允许 solve.py 导入同目录下的 helper.py 等文件。
    sys.path.insert(0, str(solve_path.parent))
    sys.modules[module_name] = module
    try:
        try:
            spec.loader.exec_module(module)
        except Exception:
            sys.modules.pop(module_name, None)
            raise
    finally:
        sys.path.pop(0)

    func = getattr(module, func_name, None)
    if not callable(func):
        raise AttributeError(
            f"{solve_path.name} 中没有可调用的 {func_name}(str) 函数"
        )
    return func


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="批量读取测试数据并调用 solve(str)"
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="题目目录或 solve.py 路径；默认当前目录",
    )
    parser.add_argument("--data", default="data", help="数据目录；默认 data")
    parser.add_argument(
        "--pattern",
        default=r"data.*\.txt",
        help=r"文件名完整匹配正则；默认 data.*\.txt",
    )
    parser.add_argument("--out", help="输出目录；不指定时输出到终端")
    parser.add_argument("--func", default="solve", help="函数名；默认 solve")
    parser.add_argument("--encoding", default="utf-8")
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument(
        "--only",
        help="对匹配结果再次用正则筛选，例如 data0[1-3]\\.txt",
    )
    parser.add_argument("--time", action="store_true", help="显示每组用时")
    parser.add_argument(
        "--answer",
        type=positive_int,
        metavar="N",
        help="只取得 solve() 生成器的第 N 个答案（从 1 开始）",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="某组报错后继续运行后续数据",
    )
    parser.add_argument("--suffix", default=".out", help="输出后缀；默认 .out")
    return parser


def positive_int(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("必须是从 1 开始的整数")
    return number


def resolve_child(problem_dir: Path, value: str | None) -> Path | None:
    if value is None:
        return None
    path = Path(value)
    return path if path.is_absolute() else problem_dir / path


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    target = Path(args.target).resolve()

    if target.is_dir():
        problem_dir = target
        solve_path = target / "solve.py"
    else:
        solve_path = target
        problem_dir = target.parent

    try:
        solve = load_solver(solve_path, args.func)
        runner = BatchIO(
            data_dir=resolve_child(problem_dir, args.data),
            pattern=args.pattern,
            output_dir=resolve_child(problem_dir, args.out),
            encoding=args.encoding,
            recursive=args.recursive,
            only=args.only,
            show_time=args.time,
            answer_index=args.answer,
            continue_on_error=args.continue_on_error,
            output_suffix=args.suffix,
        )
        return runner.run(solve)
    except Exception:
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
