from __future__ import annotations

import inspect
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .answer_book import AnswerBook


class _UseDefaultTimeout:
    pass


class _PrintToStdout:
    pass


_USE_DEFAULT_TIMEOUT = _UseDefaultTimeout()
_PRINT_TO_STDOUT = _PrintToStdout()


@dataclass(frozen=True)
class Input:
    """A data-file name that ``Exam`` resolves with its configured reader."""

    name: str

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Input.name 必须是非空字符串")


def _resolve_input(value: Any, reader: Callable[[str], Any]) -> Any:
    if isinstance(value, Input):
        return reader(value.name)
    if isinstance(value, tuple):
        return tuple(_resolve_input(item, reader) for item in value)
    if isinstance(value, list):
        return [_resolve_input(item, reader) for item in value]
    if isinstance(value, dict):
        return {
            key: _resolve_input(item, reader)
            for key, item in value.items()
        }
    return value


def _execute_case(
    task: Callable[..., Any],
    args: tuple[Any, ...],
    reader: Callable[[str], Any],
) -> Any:
    resolved_args = tuple(
        _resolve_input(arg, reader)
        for arg in args
    )
    return task(*resolved_args)


@dataclass(frozen=True, init=False)
class Case:
    """One labeled invocation of a task."""

    label: str
    args: tuple[Any, ...]
    files: tuple[str, ...]
    timeout: float | None | _UseDefaultTimeout

    def __init__(
        self,
        label: str,
        /,
        *args: Any,
        files: tuple[str, ...] = (),
        timeout: float | None | _UseDefaultTimeout = _USE_DEFAULT_TIMEOUT,
    ) -> None:
        if not isinstance(label, str) or not label:
            raise ValueError("Case.label 必须是非空字符串")
        if not isinstance(files, tuple):
            raise TypeError("files 必须是文件名 tuple")
        if any(not isinstance(name, str) or not name for name in files):
            raise ValueError("files 中的每个文件名必须是非空字符串")
        object.__setattr__(self, "label", label)
        object.__setattr__(
            self,
            "args",
            args + tuple(Input(name) for name in files),
        )
        object.__setattr__(self, "files", files)
        object.__setattr__(self, "timeout", timeout)


class Series:
    """Generate regularly named cases such as ``1a``/``1b``/``1c``."""

    def __init__(
        self,
        prefix: str,
        variants: str | Mapping[str, tuple[Any, ...]] = "abc",
        *,
        input_count: int = 1,
        label_separator: str = "",
        timeout: float | None | _UseDefaultTimeout = _USE_DEFAULT_TIMEOUT,
    ) -> None:
        if not isinstance(prefix, str) or not prefix:
            raise ValueError("Series.prefix 必须是非空字符串")
        if (
            isinstance(input_count, bool)
            or not isinstance(input_count, int)
            or input_count < 0
        ):
            raise ValueError("input_count 必须是非负整数")

        if isinstance(variants, str):
            items = [(variant, ()) for variant in variants]
        elif isinstance(variants, Mapping):
            items = []
            for variant, params in variants.items():
                if not isinstance(variant, str) or not variant:
                    raise ValueError("variant 必须是非空字符串")
                if not isinstance(params, tuple):
                    raise TypeError("每个 variant 的参数必须写成 tuple")
                items.append((variant, params))
        else:
            raise TypeError("variants 必须是字符串或 {variant: 参数元组} 映射")

        if not items:
            raise ValueError("Series 至少需要一个 variant")
        variant_names = [variant for variant, _ in items]
        if len(variant_names) != len(set(variant_names)):
            raise ValueError("Series 中存在重复 variant")

        self.prefix = prefix
        self.items = tuple(items)
        self.input_count = input_count
        self.label_separator = label_separator
        self.timeout = timeout

    def __iter__(self) -> Iterator[Case]:
        for variant, params in self.items:
            label = f"{self.prefix}{self.label_separator}{variant}"
            file_stem = f"{self.prefix}{variant}"

            if self.input_count == 1:
                files = (file_stem,)
            else:
                files = tuple(
                    f"{file_stem}{index}"
                    for index in range(1, self.input_count + 1)
                )

            yield Case(
                label,
                *params,
                files=files,
                timeout=self.timeout,
            )


class Exam:
    """Register cases declaratively and execute them through ``AnswerBook``."""

    def __init__(
        self,
        reader: Callable[[str], Any],
        *,
        timeout: float | None = None,
        show_log: bool = True,
        book: AnswerBook | None = None,
    ) -> None:
        if not callable(reader):
            raise TypeError("reader 必须是可调用对象")

        self.reader = reader
        self.book = (
            book
            if book is not None
            else AnswerBook(
                timeout=timeout,
                show_log=show_log,
                base_dir=self._caller_directory(),
            )
        )
        self._entries: list[tuple[Callable[..., Any], Case]] = []
        self._executed = False

    @staticmethod
    def _caller_directory() -> Path:
        frame = inspect.currentframe()
        if frame is None or frame.f_back is None or frame.f_back.f_back is None:
            raise RuntimeError("无法确定 Exam() 的调用代码文件")

        try:
            caller_filename = frame.f_back.f_back.f_code.co_filename
        finally:
            del frame

        if caller_filename.startswith("<") and caller_filename.endswith(">"):
            raise RuntimeError("Exam() 必须从代码文件中创建")
        return Path(caller_filename).resolve().parent

    def add(
        self,
        task: Callable[..., Any],
        /,
        *groups: Case | Series,
    ) -> Exam:
        if self._executed:
            raise RuntimeError("Exam 执行后不能继续添加 case")
        if not callable(task):
            raise TypeError("task 必须是可调用对象")
        if not groups:
            raise ValueError("每个 task 至少需要一个 Case 或 Series")

        for group in groups:
            if isinstance(group, Case):
                self._entries.append((task, group))
            elif isinstance(group, Series):
                self._entries.extend((task, case) for case in group)
            else:
                raise TypeError("case 组必须是 Case 或 Series")
        return self

    def _validate_labels(self) -> None:
        seen: set[str] = set()
        duplicates: list[str] = []
        for _, case in self._entries:
            if case.label in seen and case.label not in duplicates:
                duplicates.append(case.label)
            seen.add(case.label)
        if duplicates:
            labels = ", ".join(map(repr, duplicates))
            raise ValueError(f"Exam 中存在重复答案编号: {labels}")

    def execute(
        self,
        *,
        output: str | Path | bool | None | _PrintToStdout = _PRINT_TO_STDOUT,
        indent: int | None = 2,
        inline_simple_lists: bool = True,
    ) -> AnswerBook:
        if self._executed:
            raise RuntimeError("Exam 不能重复执行")
        self._validate_labels()
        self._executed = True

        for task, case in self._entries:
            if case.timeout is _USE_DEFAULT_TIMEOUT:
                self.book.run(
                    case.label,
                    _execute_case,
                    task,
                    case.args,
                    self.reader,
                )
            else:
                self.book.run(
                    case.label,
                    _execute_case,
                    task,
                    case.args,
                    self.reader,
                    timeout=case.timeout,
                )

        if output is _PRINT_TO_STDOUT:
            self.book.print_json(
                indent=indent,
                inline_simple_lists=inline_simple_lists,
            )
        elif output is True:
            self.book.write_json(
                indent=indent,
                inline_simple_lists=inline_simple_lists,
            )
        elif output is not None and output is not False:
            self.book.write_json(
                output,
                indent=indent,
                inline_simple_lists=inline_simple_lists,
            )
        return self.book
