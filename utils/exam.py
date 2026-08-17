from __future__ import annotations

import inspect
from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import partial
from pathlib import Path
from typing import Any

from ._caller import caller_directory
from .answer_book import AnswerBook
from .data_io import read_data, read_files


class _UseDefaultTimeout:
    pass


class _PrintToStdout:
    pass


class _Inherit(Enum):
    VALUE = auto()


_USE_DEFAULT_TIMEOUT = _UseDefaultTimeout()
_PRINT_TO_STDOUT = _PrintToStdout()
INHERIT = _Inherit.VALUE


Reader = Callable[[str], Any]
Parser = Callable[[str], Any]


def _validate_parser(
    parser: Parser | None | _Inherit,
) -> None:
    if parser is not INHERIT and parser is not None and not callable(parser):
        raise TypeError("parser 必须是可调用对象、None 或 INHERIT")


def _validate_reader(reader: Reader | _Inherit) -> None:
    if reader is not INHERIT and not callable(reader):
        raise TypeError("reader 必须是可调用对象或 INHERIT")


def _bind_reader(reader: Reader, base_dir: Path) -> Reader:
    if reader is read_data or reader is read_files:
        return partial(reader, base_dir=base_dir)
    return reader


@dataclass(frozen=True)
class Input:
    """An opaque selector resolved by an inherited or local reader/parser."""

    name: str
    reader: Reader | _Inherit = field(default=INHERIT, kw_only=True)
    parser: Parser | None | _Inherit = field(default=INHERIT, kw_only=True)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("Input.name 必须是字符串")
        _validate_reader(self.reader)
        _validate_parser(self.parser)


def _parse_reader_output(value: Any, parser: Parser) -> Any:
    if isinstance(value, Mapping):
        return {
            key: _parse_reader_output(item, parser)
            for key, item in value.items()
        }
    return parser(value)


def _resolve_input(
    value: Any,
    reader: Reader,
    parser: Parser | None,
    base_dir: Path,
) -> Any:
    if isinstance(value, Input):
        effective_reader = reader if value.reader is INHERIT else value.reader
        effective_parser = parser if value.parser is INHERIT else value.parser
        data = _bind_reader(effective_reader, base_dir)(value.name)
        return (
            data
            if effective_parser is None
            else _parse_reader_output(data, effective_parser)
        )
    if isinstance(value, tuple):
        return tuple(
            _resolve_input(item, reader, parser, base_dir)
            for item in value
        )
    if isinstance(value, list):
        return [
            _resolve_input(item, reader, parser, base_dir)
            for item in value
        ]
    if isinstance(value, dict):
        return {
            key: _resolve_input(item, reader, parser, base_dir)
            for key, item in value.items()
        }
    return value


def _execute_case(
    task: Callable[..., Any],
    args: tuple[Any, ...],
    reader: Reader,
    parser: Parser | None,
    base_dir: Path,
) -> Any:
    resolved_args = tuple(
        _resolve_input(arg, reader, parser, base_dir)
        for arg in args
    )
    return task(*resolved_args)


@dataclass(frozen=True, init=False)
class Case:
    """One labeled invocation of a task."""

    label: str
    args: tuple[Any, ...]
    files: tuple[str | Input, ...]
    timeout: float | None | _UseDefaultTimeout
    reader: Reader | _Inherit
    parser: Parser | None | _Inherit

    def __init__(
        self,
        label: str,
        /,
        *args: Any,
        files: tuple[str | Input, ...] = (),
        timeout: float | None | _UseDefaultTimeout = _USE_DEFAULT_TIMEOUT,
        reader: Reader | _Inherit = INHERIT,
        parser: Parser | None | _Inherit = INHERIT,
    ) -> None:
        if not isinstance(label, str) or not label:
            raise ValueError("Case.label 必须是非空字符串")
        if not isinstance(files, tuple):
            raise TypeError("files 必须是文件名 tuple")
        if any(not isinstance(item, (str, Input)) for item in files):
            raise TypeError("files 中的每项必须是字符串或 Input")
        _validate_reader(reader)
        _validate_parser(parser)
        object.__setattr__(self, "label", label)
        object.__setattr__(
            self,
            "args",
            args + tuple(
                Input(item) if isinstance(item, str) else item
                for item in files
            ),
        )
        object.__setattr__(self, "files", files)
        object.__setattr__(self, "timeout", timeout)
        object.__setattr__(self, "reader", reader)
        object.__setattr__(self, "parser", parser)


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
        reader: Reader | _Inherit = INHERIT,
        parser: Parser | None | _Inherit = INHERIT,
    ) -> None:
        if not isinstance(prefix, str) or not prefix:
            raise ValueError("Series.prefix 必须是非空字符串")
        if (
            isinstance(input_count, bool)
            or not isinstance(input_count, int)
            or input_count < 0
        ):
            raise ValueError("input_count 必须是非负整数")
        _validate_reader(reader)
        _validate_parser(parser)

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
        self.reader = reader
        self.parser = parser

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
                reader=self.reader,
                parser=self.parser,
            )


class Exam:
    """Register cases declaratively and execute them through ``AnswerBook``."""

    def __init__(
        self,
        reader: Reader,
        *,
        timeout: float | None = None,
        show_log: bool = True,
        book: AnswerBook | None = None,
        parser: Parser | None = None,
        base_dir: str | Path | None = None,
    ) -> None:
        if not callable(reader):
            raise TypeError("reader 必须是可调用对象")
        if parser is INHERIT:
            raise TypeError("Exam.parser 必须是可调用对象或 None")
        _validate_parser(parser)

        resolved_base_dir = (
            caller_directory("Exam()", action="创建")
            if base_dir is None
            else Path(base_dir).resolve()
        )
        self._base_dir = resolved_base_dir
        self.reader = _bind_reader(reader, resolved_base_dir)
        self.parser = parser
        self.book = (
            book
            if book is not None
            else AnswerBook(
                timeout=timeout,
                show_log=show_log,
                base_dir=resolved_base_dir,
            )
        )
        self._entries: list[tuple[Callable[..., Any], Case]] = []
        self._executed = False

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

    @staticmethod
    def _default_series(task: Callable[..., Any]) -> Series:
        name = getattr(task, "__name__", "")
        if not name.startswith("task") or len(name) == 4:
            raise ValueError(
                "@exam.task 默认注册要求函数名形如 task1；"
                "其他名称请显式传入 Case 或 Series"
            )

        parameters = tuple(inspect.signature(task).parameters.values())
        if any(
            parameter.kind is inspect.Parameter.VAR_POSITIONAL
            for parameter in parameters
        ):
            raise TypeError(
                "@exam.task 无法推导 *args 对应的输入文件数量；"
                "请显式传入 Case 或 Series"
            )
        if any(
            parameter.kind is inspect.Parameter.KEYWORD_ONLY
            and parameter.default is inspect.Parameter.empty
            for parameter in parameters
        ):
            raise TypeError(
                "@exam.task 无法为必需的仅关键字参数提供输入；"
                "请显式传入 Case 或 Series"
            )

        input_count = sum(
            parameter.kind
            in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
            for parameter in parameters
        )
        return Series(name[4:], input_count=input_count)

    def task(
        self,
        first: Callable[..., Any] | Case | Series,
        /,
        *groups: Case | Series,
    ) -> Any:
        """Register a task as ``@exam.task`` or ``@exam.task(...)``."""
        if callable(first):
            if groups:
                raise TypeError(
                    "直接传入 task 函数时不能再附加 Case 或 Series"
                )
            self.add(first, self._default_series(first))
            return first

        configured_groups = (first, *groups)

        def decorator(task: Callable[..., Any]) -> Callable[..., Any]:
            self.add(task, *configured_groups)
            return task

        return decorator

    def _select_entries(
        self,
        only: Callable[..., Any] | Iterable[Callable[..., Any]] | None,
    ) -> list[tuple[Callable[..., Any], Case]]:
        if only is None:
            return self._entries

        if callable(only):
            selected = (only,)
        else:
            try:
                selected = tuple(only)
            except TypeError as error:
                raise TypeError(
                    "only 必须是已注册的 task、task 可迭代对象或 None"
                ) from error
            if not selected:
                raise ValueError("only 至少需要一个 task；传 None 执行全部")
            if any(not callable(task) for task in selected):
                raise TypeError("only 中的每一项都必须是已注册的 task")

        registered = tuple(task for task, _ in self._entries)
        missing = tuple(
            task
            for task in selected
            if not any(task is registered_task for registered_task in registered)
        )
        if missing:
            names = ", ".join(
                getattr(task, "__name__", repr(task))
                for task in missing
            )
            raise ValueError(f"only 中包含未注册的 task: {names}")

        return [
            (task, case)
            for task, case in self._entries
            if any(task is selected_task for selected_task in selected)
        ]

    @staticmethod
    def _validate_labels(
        entries: Iterable[tuple[Callable[..., Any], Case]],
    ) -> None:
        seen: set[str] = set()
        duplicates: list[str] = []
        for _, case in entries:
            if case.label in seen and case.label not in duplicates:
                duplicates.append(case.label)
            seen.add(case.label)
        if duplicates:
            labels = ", ".join(map(repr, duplicates))
            raise ValueError(f"Exam 中存在重复答案编号: {labels}")

    def execute(
        self,
        *,
        only: Callable[..., Any] | Iterable[Callable[..., Any]] | None = None,
        output: str | Path | bool | None | _PrintToStdout = _PRINT_TO_STDOUT,
        indent: int | None = 2,
        inline_simple_lists: bool = True,
    ) -> AnswerBook:
        if self._executed:
            raise RuntimeError("Exam 不能重复执行")
        entries = self._select_entries(only)
        self._validate_labels(entries)
        self._executed = True

        for task, case in entries:
            reader = (
                self.reader
                if case.reader is INHERIT
                else _bind_reader(case.reader, self._base_dir)
            )
            parser = (
                self.parser
                if case.parser is INHERIT
                else case.parser
            )
            if case.timeout is _USE_DEFAULT_TIMEOUT:
                self.book.run(
                    case.label,
                    _execute_case,
                    task,
                    case.args,
                    reader,
                    parser,
                    self._base_dir,
                )
            else:
                self.book.run(
                    case.label,
                    _execute_case,
                    task,
                    case.args,
                    reader,
                    parser,
                    self._base_dir,
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
