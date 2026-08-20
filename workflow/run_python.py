from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path
from time import perf_counter


RUNTIME_DIRECTORY = Path(__file__).resolve().parent / "runtimes"
PYPY_EXECUTABLE = re.compile(r"pypy3(?:\.\d+)?(?:\.exe)?")


def find_pypy() -> Path | None:
    if RUNTIME_DIRECTORY.is_dir():
        candidates = sorted(
            path
            for path in RUNTIME_DIRECTORY.rglob("*")
            if path.is_file() and PYPY_EXECUTABLE.fullmatch(path.name)
        )
        if candidates:
            return candidates[0]

    for name in ("pypy3", "pypy3.11", "pypy3.10", "pypy3.9"):
        executable = shutil.which(name)
        if executable is not None:
            return Path(executable)
    return None


def choose_interpreter(runtime: str) -> tuple[str, Path]:
    if runtime == "python":
        return "CPython", Path(sys.executable)

    pypy = find_pypy()
    if pypy is not None:
        return "PyPy", pypy

    if runtime == "auto":
        print(
            "[warning] PyPy was not found; falling back to CPython.",
            file=sys.stderr,
            flush=True,
        )
        return "CPython", Path(sys.executable)

    raise FileNotFoundError(
        "Cannot find PyPy 3. Download the Windows 64-bit PyPy3 archive "
        "from https://pypy.org/download.html and extract it under "
        f"{RUNTIME_DIRECTORY}, or add pypy3 to PATH. See workflow/PYPY.md."
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run one Python script with CPython or PyPy."
    )
    parser.add_argument("runtime", choices=("python", "pypy", "auto"))
    parser.add_argument("script", type=Path)
    parser.add_argument("script_arguments", nargs=argparse.REMAINDER)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    script = args.script.resolve()
    if not script.is_file():
        raise FileNotFoundError(f"Cannot find Python script: {script}")

    runtime_name, interpreter = choose_interpreter(args.runtime)
    command = [
        str(interpreter),
        "-u",
        str(script),
        *args.script_arguments,
    ]

    print(f"[runtime] {runtime_name}: {interpreter}", flush=True)
    print(f"[script]  {script}", flush=True)

    started = perf_counter()
    try:
        return subprocess.run(command, cwd=script.parent).returncode
    except KeyboardInterrupt:
        print("[interrupted] Ctrl+C", file=sys.stderr, flush=True)
        return 130
    finally:
        elapsed = perf_counter() - started
        print(f"[elapsed] {elapsed:.3f}s", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
