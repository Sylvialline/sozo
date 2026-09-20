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
from .data_io import read_data, read_data_file, read_files


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
Calls = Callable[[Any], Iterable[Any]]


class Rows:
    """Turn non-empty whitespace-separated text lines into task arguments.

    Each converter handles one field.  With no converters, every non-empty
    line produces one argument-free invocation, which is useful when rows are
    only repeated query markers.
    """

    def __init__(self, *converters: Callable[[str], Any]) -> None:
        if any(not callable(converter) for converter in converters):
            raise TypeError("Rows 的每个转换器都必须是可调用对象")
        self.converters = converters

    def __call__(self, text: str) -> Iterator[tuple[Any, ...]]:
        if not isinstance(text, str):
            raise TypeError("Rows 只能解析字符串")

        for line_number, raw_line in enumerate(text.splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue
            if not self.converters:
                yield ()
                continue

            fields = line.split()
            if len(fields) != len(self.converters):
                raise ValueError(
                    f"第 {line_number} 行需要 {len(self.converters)} 个字段，"
                    f"实际得到 {len(fields)} 个"
                )
            yield tuple(
                converter(field)
                for converter, field in zip(self.converters, fields)
            )


def _validate_parser(
    parser: Parser | None | _Inherit,
) -> None:
    if parser is not INHERIT and parser is not None and not callable(parser):
        raise TypeError("parser 必须是可调用对象、None 或 INHERIT")


def _validate_reader(reader: Reader | _Inherit) -> None:
    if reader is not INHERIT and not callable(reader):
        raise TypeError("reader 必须是可调用对象或 INHERIT")


def _bind_reader(reader: Reader, base_dir: Path) -> Reader:
    if (
        reader is read_data
        or reader is read_data_file
        or reader is read_files
    ):
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


def _execute_batch(
    task: Callable[..., Any],
    source: Input,
    calls: Calls,
    reader: Reader,
    parser: Parser | None,
    base_dir: Path,
) -> Any:
    data = _resolve_input(source, reader, parser, base_dir)

    invocations = calls(data)
    if isinstance(invocations, (str, bytes, bytearray, Mapping)):
        raise TypeError("Batch.calls 必须返回多组调用参数，不能返回字符串或映射")
    try:
        iterator = iter(invocations)
    except TypeError as error:
        raise TypeError("Batch.calls 必须返回可迭代对象") from error

    results = []
    for invocation in iterator:
        call_args = invocation if isinstance(invocation, tuple) else (invocation,)
        results.append(task(*call_args))
    return results


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


@dataclass(frozen=True, init=False)
class Batch:
    """One input source expanded into multiple invocations of a task."""

    label: str
    source: Input
    calls: Calls
    timeout: float | None | _UseDefaultTimeout
    reader: Reader | _Inherit
    parser: Parser | None | _Inherit

    def __init__(
        self,
        label: str,
        source: str | Input,
        /,
        calls: Calls,
        *,
        timeout: float | None | _UseDefaultTimeout = _USE_DEFAULT_TIMEOUT,
        reader: Reader | _Inherit = INHERIT,
        parser: Parser | None | _Inherit = INHERIT,
    ) -> None:
        if not isinstance(label, str) or not label:
            raise ValueError("Batch.label 必须是非空字符串")
        if not isinstance(source, (str, Input)):
            raise TypeError("Batch.source 必须是文件名字符串或 Input")
        if not callable(calls):
            raise TypeError("Batch.calls 必须是可调用对象")
        _validate_reader(reader)
        _validate_parser(parser)
        object.__setattr__(self, "label", label)
        object.__setattr__(
            self,
            "source",
            Input(source) if isinstance(source, str) else source,
        )
        object.__setattr__(self, "calls", calls)
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
        reader: Reader = read_data_file,
        *,
        timeout: float | None = None,
        show_time: bool = False,
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
                show_time=show_time,
                show_log=show_log,
                base_dir=resolved_base_dir,
            )
        )
        self._entries: list[tuple[Callable[..., Any], Case | Batch]] = []
        self._executed = False

    def add(
        self,
        task: Callable[..., Any],
        /,
        *groups: Case | Batch | Series,
    ) -> Exam:
        """注册显式任务组；省略时按函数签名生成默认 Series。"""
        if self._executed:
            raise RuntimeError("Exam 执行后不能继续添加任务项")
        if not callable(task):
            raise TypeError("task 必须是可调用对象")
        if not groups:
            groups = (self._default_series(task),)

        for group in groups:
            if isinstance(group, (Case, Batch)):
                self._entries.append((task, group))
            elif isinstance(group, Series):
                self._entries.extend((task, case) for case in group)
            else:
                raise TypeError("任务组必须是 Case、Batch 或 Series")
        return self

    def add_once(self, task: Callable[[], Any], /) -> Exam:
        """以函数名为 label，注册一次无参数调用。"""
        if not callable(task):
            raise TypeError("task 必须是可调用对象")
        label = getattr(task, "__name__", None)
        if not isinstance(label, str) or not label:
            raise ValueError("add_once 要求 task 具有非空 __name__")
        return self.add(task, Case(label))

    @staticmethod
    def _default_series(task: Callable[..., Any]) -> Series:
        name = getattr(task, "__name__", None)
        if not isinstance(name, str) or not name:
            raise ValueError("默认注册要求 task 具有非空 __name__")

        parameters = tuple(inspect.signature(task).parameters.values())
        if any(
            parameter.kind is inspect.Parameter.VAR_POSITIONAL
            for parameter in parameters
        ):
            raise TypeError(
                "默认注册无法推导 *args 对应的输入文件数量；"
                "请显式传入 Case、Batch 或 Series"
            )
        if any(
            parameter.kind is inspect.Parameter.KEYWORD_ONLY
            and parameter.default is inspect.Parameter.empty
            for parameter in parameters
        ):
            raise TypeError(
                "默认注册无法为必需的仅关键字参数提供输入；"
                "请显式传入 Case、Batch 或 Series"
            )

        input_count = sum(
            parameter.kind
            in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
            for parameter in parameters
        )
        return Series(name, input_count=input_count)

    def task(
        self,
        first: Callable[..., Any] | Case | Batch | Series,
        /,
        *groups: Case | Batch | Series,
    ) -> Any:
        """用裸装饰器自动推导 Series，或显式指定任务组。"""
        if callable(first):
            if groups:
                raise TypeError(
                    "直接传入 task 函数时不能再附加 Case、Batch 或 Series"
                )
            self.add(first)
            return first

        configured_groups = (first, *groups)

        def decorator(task: Callable[..., Any]) -> Callable[..., Any]:
            self.add(task, *configured_groups)
            return task

        return decorator

    def _select_entries(
        self,
        only: Callable[..., Any] | Iterable[Callable[..., Any]] | None,
    ) -> list[tuple[Callable[..., Any], Case | Batch]]:
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
            (task, entry)
            for task, entry in self._entries
            if any(task is selected_task for selected_task in selected)
        ]

    @staticmethod
    def _validate_labels(
        entries: Iterable[tuple[Callable[..., Any], Case | Batch]],
    ) -> None:
        seen: set[str] = set()
        duplicates: list[str] = []
        for _, entry in entries:
            if entry.label in seen and entry.label not in duplicates:
                duplicates.append(entry.label)
            seen.add(entry.label)
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

        for task, entry in entries:
            reader = (
                self.reader
                if entry.reader is INHERIT
                else _bind_reader(entry.reader, self._base_dir)
            )
            parser = (
                self.parser
                if entry.parser is INHERIT
                else entry.parser
            )
            if isinstance(entry, Batch):
                run_args = (
                    entry.label,
                    _execute_batch,
                    task,
                    entry.source,
                    entry.calls,
                    reader,
                    parser,
                    self._base_dir,
                )
            else:
                run_args = (
                    entry.label,
                    _execute_case,
                    task,
                    entry.args,
                    reader,
                    parser,
                    self._base_dir,
                )
            if entry.timeout is _USE_DEFAULT_TIMEOUT:
                self.book.run(*run_args)
            else:
                self.book.run(*run_args, timeout=entry.timeout)

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
