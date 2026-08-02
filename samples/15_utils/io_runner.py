"""用途：可复用的离线考试批量文件运行器。
示例输入：目录内 data1.txt、data2.txt；每个文件调用 solver(text)。
示例输出：逐文件答案、耗时以及总成功/失败统计，也可镜像写入输出目录。
复杂度：文件发现 O(F log F)，求解成本为各文件 solver 成本之和。
陷阱：相对路径基于当前工作目录；正则使用 fullmatch；生成器会被完整消费。
"""

from __future__ import annotations

import re
import tempfile
import traceback
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any


@dataclass(slots=True)
class RunConfig:
    input_dir: Path
    output_dir: Path | None = None
    merged_output: Path | None = None
    recursive: bool = False
    regex: str | None = None
    substring: str | None = None
    suffixes: tuple[str, ...] = (".txt",)
    output_suffix: str = ".out"
    encoding: str = "utf-8"
    print_terminal: bool = True
    continue_on_error: bool = False
    debug: bool = False


@dataclass(slots=True)
class CaseResult:
    path: Path
    output: str | None
    seconds: float
    error: Exception | None = None


def natural_key(path: Path) -> list[object]:
    parts = re.split(r"(\d+)", path.as_posix().casefold())
    return [int(part) if part.isdigit() else part for part in parts]


def discover_files(config: RunConfig) -> list[Path]:
    if not config.input_dir.is_dir():
        raise NotADirectoryError(config.input_dir)

    pattern = re.compile(config.regex) if config.regex else None
    suffixes = {suffix.casefold() for suffix in config.suffixes}
    candidates = (
        config.input_dir.rglob("*")
        if config.recursive
        else config.input_dir.iterdir()
    )
    files = [
        path
        for path in candidates
        if path.is_file()
        and (not suffixes or path.suffix.casefold() in suffixes)
        and (config.substring is None or config.substring in path.name)
        and (pattern is None or pattern.fullmatch(path.name))
    ]
    return sorted(
        files,
        key=lambda path: natural_key(path.relative_to(config.input_dir)),
    )


def format_output(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        return value.decode("utf-8")
    if isinstance(value, Mapping):
        return str(value)
    if isinstance(value, Iterable):
        return "\n".join(map(str, value))
    return str(value)


def _terminal_block(relative: Path, output: str) -> str:
    return (
        "输入数据的文件名：\n"
        f"{relative.as_posix()}\n\n"
        "该文件对应的输出：\n"
        f"{output}"
    )


def _write_case(config: RunConfig, path: Path, output: str) -> Path:
    assert config.output_dir is not None
    relative = path.relative_to(config.input_dir)
    output_path = config.output_dir / relative.with_suffix(config.output_suffix)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output, encoding=config.encoding)
    return output_path


def run_batch(
    solver: Callable[[str], Any],
    config: RunConfig,
) -> list[CaseResult]:
    files = discover_files(config)
    results: list[CaseResult] = []
    merged_blocks: list[str] = []
    total_started = perf_counter()

    for path in files:
        started = perf_counter()
        try:
            text = path.read_text(encoding=config.encoding)
            output = format_output(solver(text))
            elapsed = perf_counter() - started
            relative = path.relative_to(config.input_dir)
            block = _terminal_block(relative, output)

            if config.print_terminal:
                print(block)
                print(f"\n[用时 {elapsed * 1000:.3f} ms]\n")
            if config.output_dir is not None:
                _write_case(config, path, output)
            if config.merged_output is not None:
                merged_blocks.append(block)
            results.append(CaseResult(path, output, elapsed))
        except Exception as error:
            elapsed = perf_counter() - started
            results.append(CaseResult(path, None, elapsed, error))
            relative = path.relative_to(config.input_dir)
            print(
                f"[ERROR] {relative.as_posix()}: "
                f"{type(error).__name__}: {error} "
                f"[用时 {elapsed * 1000:.3f} ms]"
            )
            if config.debug:
                traceback.print_exc()
            if not config.continue_on_error:
                break

    if config.merged_output is not None:
        config.merged_output.parent.mkdir(parents=True, exist_ok=True)
        config.merged_output.write_text(
            "\n\n".join(merged_blocks),
            encoding=config.encoding,
        )

    succeeded = sum(result.error is None for result in results)
    failed = len(results) - succeeded
    total = perf_counter() - total_started
    print(
        f"统计：发现 {len(files)}，处理 {len(results)}，"
        f"成功 {succeeded}，失败 {failed}，总用时 {total:.3f} s"
    )
    return results


def main() -> None:
    def line_lengths(text: str) -> Iterable[str]:
        for line in text.splitlines():
            yield f"{line}: {len(line)}"

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        (root / "data2.txt").write_text("alpha\nbeta", encoding="utf-8")
        (root / "data10.txt").write_text("gamma", encoding="utf-8")
        run_batch(
            line_lengths,
            RunConfig(root, regex=r"data\d+\.txt"),
        )


if __name__ == "__main__":
    main()
