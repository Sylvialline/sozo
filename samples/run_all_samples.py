"""用途：用独立 Python 进程批量运行 samples 下的所有示例并汇总失败项。
示例输入：python samples/run_all_samples.py --pattern heap
示例输出：[OK] .../heapq_priority_queue.py；统计：成功 n，失败 0。
复杂度：等于所有被选示例运行时间之和。
陷阱：示例彼此隔离但仍可能读写文件；每个进程有超时，NumPy 示例依赖可选环境。
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = ROOT.parent


@dataclass(slots=True)
class Result:
    path: Path
    returncode: int
    seconds: float
    stdout: str
    stderr: str
    timed_out: bool = False


def discover(pattern: str | None) -> list[Path]:
    files = []
    for path in ROOT.rglob("*.py"):
        relative = path.relative_to(ROOT)
        if path == Path(__file__).resolve():
            continue
        if "input" in relative.parts:
            continue
        if pattern is not None and pattern.casefold() not in relative.as_posix().casefold():
            continue
        files.append(path)
    return sorted(files, key=lambda path: path.relative_to(ROOT).as_posix())


def run_one(path: Path, timeout: float) -> Result:
    started = perf_counter()
    try:
        completed = subprocess.run(
            [sys.executable, str(path)],
            cwd=REPOSITORY_ROOT,
            # 关闭子进程 stdin，避免阻塞；需要输入的示例会使用各自的内置样例。
            input="",
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return Result(
            path,
            completed.returncode,
            perf_counter() - started,
            completed.stdout,
            completed.stderr,
        )
    except subprocess.TimeoutExpired as error:
        return Result(
            path,
            -1,
            perf_counter() - started,
            error.stdout or "",
            error.stderr or "",
            timed_out=True,
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pattern", help="只运行相对路径中包含该字符串的示例")
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--show-output", action="store_true")
    parser.add_argument("--stop-on-error", action="store_true")
    args = parser.parse_args()

    files = discover(args.pattern)
    results = []
    for path in files:
        result = run_one(path, args.timeout)
        results.append(result)
        relative = path.relative_to(ROOT).as_posix()
        status = "TIMEOUT" if result.timed_out else "OK" if result.returncode == 0 else "FAIL"
        print(f"[{status}] {relative} ({result.seconds * 1000:.1f} ms)")

        if args.show_output or status != "OK":
            if result.stdout:
                print("--- stdout ---")
                print(result.stdout.rstrip())
            if result.stderr:
                print("--- stderr ---")
                print(result.stderr.rstrip())
        if status != "OK" and args.stop_on_error:
            break

    failed = [result for result in results if result.returncode != 0]
    print(f"统计：发现 {len(files)}，运行 {len(results)}，成功 {len(results) - len(failed)}，失败 {len(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
