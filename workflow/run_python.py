from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from time import perf_counter
from typing import Iterator


RUNTIME_DIRECTORY = Path(__file__).resolve().parent / "runtimes"
PYPY_EXECUTABLE = re.compile(r"pypy3(?:\.\d+)?(?:\.exe)?")
UTF8_CODE_PAGE = 65001


def utf8_environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-8"
    environment["PYTHONUTF8"] = "1"
    return environment


@contextmanager
def utf8_console() -> Iterator[None]:
    if sys.platform != "win32":
        yield
        return

    import ctypes

    kernel32 = ctypes.windll.kernel32
    input_code_page = kernel32.GetConsoleCP()
    output_code_page = kernel32.GetConsoleOutputCP()
    input_changed = False
    output_changed = False

    try:
        if input_code_page and input_code_page != UTF8_CODE_PAGE:
            if not kernel32.SetConsoleCP(UTF8_CODE_PAGE):
                raise OSError("Cannot switch the console input to UTF-8.")
            input_changed = True
        if output_code_page and output_code_page != UTF8_CODE_PAGE:
            if not kernel32.SetConsoleOutputCP(UTF8_CODE_PAGE):
                raise OSError("Cannot switch the console output to UTF-8.")
            output_changed = True
        yield
    finally:
        if output_changed:
            kernel32.SetConsoleOutputCP(output_code_page)
        if input_changed:
            kernel32.SetConsoleCP(input_code_page)


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

    with utf8_console():
        print(f"[runtime] {runtime_name}: {interpreter}", flush=True)
        print(f"[script]  {script}", flush=True)

        started = perf_counter()
        try:
            return subprocess.run(
                command,
                cwd=script.parent,
                env=utf8_environment(),
            ).returncode
        except KeyboardInterrupt:
            print("[interrupted] Ctrl+C", file=sys.stderr, flush=True)
            return 130
        finally:
            elapsed = perf_counter() - started
            print(f"[elapsed] {elapsed:.3f}s", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
