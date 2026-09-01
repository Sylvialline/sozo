from __future__ import annotations

import argparse
import importlib.util
import platform
import pstats
import subprocess
import sys
from pathlib import Path

try:
    from .run_python import utf8_console, utf8_environment
except ImportError:
    from run_python import utf8_console, utf8_environment


DEFAULT_TOP = 15


def _positive_int(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Profile one Python script with cProfile or line_profiler."
    )
    subparsers = parser.add_subparsers(dest="mode", required=True)

    functions = subparsers.add_parser(
        "functions",
        help="find expensive functions with the standard-library cProfile",
    )
    functions.add_argument("--top", type=_positive_int, default=DEFAULT_TOP)
    functions.add_argument("script", type=Path)
    functions.add_argument("script_arguments", nargs=argparse.REMAINDER)

    lines = subparsers.add_parser(
        "lines",
        help="find expensive lines with line_profiler auto-profiling",
    )
    lines.add_argument("script", type=Path)
    lines.add_argument("script_arguments", nargs=argparse.REMAINDER)
    return parser


def _resolve_script(path: Path) -> Path:
    script = path.resolve()
    if not script.is_file():
        raise FileNotFoundError(f"Cannot find Python script: {script}")
    return script


def _run(command: list[str], script: Path) -> int:
    return subprocess.run(
        command,
        cwd=script.parent,
        env=utf8_environment(),
    ).returncode


def profile_functions(script: Path, script_arguments: list[str], top: int) -> int:
    output = script.with_name(script.name + ".prof")
    command = [
        sys.executable,
        "-u",
        "-m",
        "cProfile",
        "-o",
        str(output),
        script.name,
        *script_arguments,
    ]
    returncode = _run(command, script)
    if returncode:
        return returncode

    print(f"[profile] {output}", flush=True)
    print(f"\n[cumulative time: top {top}]", flush=True)
    pstats.Stats(str(output)).strip_dirs().sort_stats("cumulative").print_stats(top)
    print(f"\n[self time: top {top}]", flush=True)
    pstats.Stats(str(output)).strip_dirs().sort_stats("time").print_stats(top)
    return 0


def profile_lines(script: Path, script_arguments: list[str]) -> int:
    if platform.python_implementation() != "CPython":
        raise RuntimeError("line_profiler must be run with CPython in this workflow")
    if importlib.util.find_spec("line_profiler") is None:
        raise RuntimeError(
            "line_profiler is not installed; run: "
            "python -m pip install --user -r workflow/requirements-profiling.txt"
        )

    output = script.with_name(script.name + ".lprof")
    command = [
        sys.executable,
        "-u",
        "-m",
        "kernprof",
        "-l",
        "-v",
        "-z",
        "--summarize",
        "-o",
        str(output),
        "-p",
        script.name,
        script.name,
        *script_arguments,
    ]
    return _run(command, script)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    script = _resolve_script(args.script)

    with utf8_console():
        print(f"[runtime] CPython: {sys.executable}", flush=True)
        print(f"[script]  {script}", flush=True)
        if args.mode == "functions":
            return profile_functions(script, args.script_arguments, args.top)
        return profile_lines(script, args.script_arguments)


if __name__ == "__main__":
    raise SystemExit(main())
