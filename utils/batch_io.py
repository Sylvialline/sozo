from __future__ import annotations

import re
import sys
import time
import traceback
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any, Callable


class BatchIO:
    """批量读取测试文件，调用 solve(str)，并打印或写出答案。"""

    SEPARATOR = "-" * 21

    def __init__(
        self,
        data_dir: str | Path,
        pattern: str = r"data.*\.txt",
        *,
        output_dir: str | Path | None = None,
        encoding: str = "utf-8",
        recursive: bool = False,
        only: str | None = None,
        show_time: bool = False,
        answer_index: int | None = None,
        continue_on_error: bool = False,
        output_suffix: str = ".out",
    ) -> None:
        self.data_dir = Path(data_dir)
        self.pattern = re.compile(pattern)
        self.output_dir = Path(output_dir) if output_dir is not None else None
        self.encoding = encoding
        self.recursive = recursive
        self.only = re.compile(only) if only else None
        self.show_time = show_time
        self.answer_index = answer_index
        self.continue_on_error = continue_on_error
        self.output_suffix = output_suffix

        if not output_suffix.startswith("."):
            raise ValueError("output_suffix 应以 '.' 开头，例如 '.out'")
        if answer_index is not None and answer_index < 1:
            raise ValueError("answer_index 必须是从 1 开始的整数")

    @staticmethod
    def _natural_key(path: Path) -> list[object]:
        """让 data2.txt 排在 data10.txt 前面。"""
        parts = re.split(r"(\d+)", path.as_posix().casefold())
        return [int(part) if part.isdigit() else part for part in parts]

    @staticmethod
    def _format_item(item: Any) -> str:
        if item is None:
            return ""
        if isinstance(item, str):
            return item
        if isinstance(item, bytes):
            return item.decode("utf-8")
        return str(item)

    def _select_answer(self, result: Any) -> Any:
        if not isinstance(result, Iterator):
            raise TypeError(
                "--answer 只适用于返回迭代器或生成器的 solve()"
            )

        close = getattr(result, "close", None)
        try:
            for index, item in enumerate(result, 1):
                if index == self.answer_index:
                    return item
        finally:
            if callable(close):
                close()

        raise IndexError(
            f"solve() 没有生成第 {self.answer_index} 个答案"
        )

    def _format_result(self, result: Any) -> str:
        """允许 solve 返回 str、数字、list、tuple 和 generator。"""
        if self.answer_index is not None:
            return self._format_item(self._select_answer(result))
        if result is None:
            return ""
        if isinstance(result, str):
            return result
        if isinstance(result, bytes):
            return result.decode("utf-8")
        if isinstance(result, Iterable):
            return "\n".join(map(self._format_item, result))
        return str(result)

    def collect_files(self) -> list[Path]:
        if not self.data_dir.is_dir():
            raise NotADirectoryError(f"找不到数据目录: {self.data_dir}")

        candidates: Iterable[Path]
        candidates = (
            self.data_dir.rglob("*")
            if self.recursive
            else self.data_dir.iterdir()
        )

        files = [
            path
            for path in candidates
            if path.is_file()
            and self.pattern.fullmatch(path.name)
            and (self.only is None or self.only.search(path.name))
        ]
        files.sort(
            key=lambda path: self._natural_key(path.relative_to(self.data_dir))
        )
        return files

    def _print_case(self, filename: str, answer: str, elapsed: float) -> None:
        print(f"{filename}：")
        if answer:
            print(answer, end="" if answer.endswith("\n") else "\n")
        if self.show_time:
            print(f"[用时 {elapsed * 1000:.3f} ms]")
        print(self.SEPARATOR)

    def _write_case(self, input_path: Path, answer: str, elapsed: float) -> None:
        assert self.output_dir is not None

        relative_path = input_path.relative_to(self.data_dir)
        output_path = self.output_dir / relative_path.with_suffix(
            self.output_suffix
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(answer, encoding=self.encoding)

        timing = f" ({elapsed * 1000:.3f} ms)" if self.show_time else ""
        print(f"{relative_path} -> {output_path}{timing}")

    def run(self, func: Callable[[str], Any]) -> int:
        files = self.collect_files()
        if not files:
            raise FileNotFoundError(
                f"目录 {self.data_dir} 中没有与正则 "
                f"{self.pattern.pattern!r} 完整匹配的文件"
            )

        if self.output_dir is not None:
            self.output_dir.mkdir(parents=True, exist_ok=True)

        failed = 0
        for input_path in files:
            try:
                source = input_path.read_text(encoding=self.encoding)

                started = time.perf_counter()
                answer = self._format_result(func(source))
                elapsed = time.perf_counter() - started

                if self.output_dir is None:
                    relative_name = input_path.relative_to(self.data_dir).as_posix()
                    self._print_case(relative_name, answer, elapsed)
                else:
                    self._write_case(input_path, answer, elapsed)

            except Exception:
                failed += 1
                print(f"[ERROR] {input_path.name}", file=sys.stderr)
                traceback.print_exc()
                if not self.continue_on_error:
                    return 1

        return 1 if failed else 0
