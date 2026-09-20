from __future__ import annotations

import json
import math
import sys
import traceback
from collections.abc import Callable, Iterable, Mapping
from dataclasses import fields, is_dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum
from multiprocessing import get_context
from multiprocessing.connection import Connection
from numbers import Integral, Real
from pathlib import Path
from time import perf_counter
from typing import Any
from uuid import UUID

from ._caller import caller_directory


_PROCESS_START_TIMEOUT = 30.0


def _type_name(value: Any) -> str:
    value_type = type(value)
    return f"{value_type.__module__}.{value_type.__qualname__}"


def _json_key_value(key: Any) -> str:
    if isinstance(key, str):
        return key
    if key is None:
        return "null"
    if key is True:
        return "true"
    if key is False:
        return "false"
    if isinstance(key, (int, float)):
        return json.dumps(key)
    raise TypeError("JSON 对象的键必须是 str、int、float、bool 或 None")


def to_jsonable(value: Any) -> Any:
    """递归返回可交给 ``json.dumps`` 的副本。

    支持常见容器、集合、dataclass、Enum、Path、日期时间、Decimal、
    NumPy 标量和数组，以及提供 ``__json__``、``tolist``、``item`` 或
    ``to_dict`` 方法的对象。普通容器不会被原地修改；一次性迭代器会被消费。
    """
    seen: set[int] = set()

    def convert(item: Any) -> Any:
        if isinstance(item, Enum):
            return convert(item.value)
        if item is None or isinstance(item, (str, bool, int, float)):
            return item
        if isinstance(item, Integral):
            return int(item)
        if isinstance(item, Real):
            return float(item)
        if isinstance(item, Decimal):
            return str(item)
        if isinstance(item, (Path, UUID)):
            return str(item)
        if isinstance(item, (datetime, date, time)):
            return item.isoformat()
        if isinstance(item, timedelta):
            return item.total_seconds()
        if isinstance(item, (bytes, bytearray, memoryview)):
            return list(item)

        marker = id(item)
        if marker in seen:
            raise ValueError("Circular reference detected")

        seen.add(marker)
        try:
            if isinstance(item, Mapping):
                converted: dict[Any, Any] = {}
                encoded_keys: set[str] = set()
                for key, child in item.items():
                    converted_key = convert(key)
                    if not (
                        converted_key is None
                        or isinstance(
                            converted_key,
                            (str, bool, int, float),
                        )
                    ):
                        raise TypeError(
                            "JSON 对象的键转换后必须是 "
                            "str、int、float、bool 或 None，"
                            f"实际为 {_type_name(converted_key)}"
                        )
                    encoded_key = _json_key_value(converted_key)
                    if encoded_key in encoded_keys:
                        raise ValueError(
                            "JSON 对象的键在转换后发生冲突: "
                            f"{encoded_key!r}"
                        )
                    encoded_keys.add(encoded_key)
                    converted[converted_key] = convert(child)
                return converted

            if is_dataclass(item) and not isinstance(item, type):
                return {
                    field.name: convert(getattr(item, field.name))
                    for field in fields(item)
                }

            if isinstance(item, (set, frozenset)):
                members = [convert(child) for child in item]
                return sorted(
                    members,
                    key=lambda child: json.dumps(
                        child,
                        ensure_ascii=False,
                        separators=(",", ":"),
                    ),
                )

            if isinstance(item, (list, tuple)):
                return [convert(child) for child in item]

            for method_name in (
                "__json__",
                "tolist",
                "item",
                "to_dict",
            ):
                method = getattr(item, method_name, None)
                if callable(method):
                    return convert(method())

            if isinstance(item, Iterable):
                return [convert(child) for child in item]
        finally:
            seen.remove(marker)

        raise TypeError(
            f"{_type_name(item)} 不能序列化为 JSON；"
            "请返回 JSON 基础类型，或提供 __json__()、tolist()、"
            "item()、to_dict() 之一"
        )

    return convert(value)


def _json_key(key: Any) -> str:
    return json.dumps(_json_key_value(key), ensure_ascii=False)


def _is_json_scalar(value: Any) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))


def _format_pretty_json(value: Any, indent: int) -> str:
    width = max(indent, 0)
    seen: set[int] = set()

    def format_value(item: Any, level: int) -> str:
        if _is_json_scalar(item):
            return json.dumps(item, ensure_ascii=False)

        if isinstance(item, Mapping):
            marker = id(item)
            if marker in seen:
                raise ValueError("Circular reference detected")
            if not item:
                return "{}"

            seen.add(marker)
            try:
                child_indent = " " * (width * (level + 1))
                closing_indent = " " * (width * level)
                members = [
                    (
                        f"{child_indent}{_json_key(key)}: "
                        f"{format_value(child, level + 1)}"
                    )
                    for key, child in item.items()
                ]
                return (
                    "{\n"
                    + ",\n".join(members)
                    + f"\n{closing_indent}}}"
                )
            finally:
                seen.remove(marker)

        if isinstance(item, (list, tuple)):
            marker = id(item)
            if marker in seen:
                raise ValueError("Circular reference detected")
            if not item:
                return "[]"
            if all(_is_json_scalar(child) for child in item):
                return (
                    "["
                    + ", ".join(
                        json.dumps(child, ensure_ascii=False)
                        for child in item
                    )
                    + "]"
                )

            seen.add(marker)
            try:
                child_indent = " " * (width * (level + 1))
                closing_indent = " " * (width * level)
                members = [
                    f"{child_indent}{format_value(child, level + 1)}"
                    for child in item
                ]
                return (
                    "[\n"
                    + ",\n".join(members)
                    + f"\n{closing_indent}]"
                )
            finally:
                seen.remove(marker)

        return json.dumps(item, ensure_ascii=False)

    return format_value(value, 0)


def pretty_json(
    value: Any,
    *,
    indent: int | None = 2,
    inline_simple_lists: bool = True,
) -> str:
    """将对象编码为易读且鲁棒的 JSON 字符串。

    默认缩进对象和嵌套数组，但让仅含简单值的一维数组保持单行。传入
    ``inline_simple_lists=False`` 可使用标准 ``json.dumps`` 缩进；传入
    ``indent=None`` 可生成紧凑 JSON。
    """
    converted = to_jsonable(value)
    if indent is not None and inline_simple_lists:
        return _format_pretty_json(converted, indent)
    return json.dumps(converted, ensure_ascii=False, indent=indent)


class _TaskTimedOut(TimeoutError):
    def __init__(self, label: str, limit: float, elapsed: float) -> None:
        self.limit = limit
        self.elapsed = elapsed
        super().__init__(
            f"任务 {label!r} 用时 {elapsed:.6f} 秒，"
            f"超过限制 {limit:.6f} 秒"
        )


def _send_worker_error(
    connection: Connection,
    error: BaseException,
    elapsed: float,
) -> None:
    traceback_text = "".join(
        traceback.format_exception(type(error), error, error.__traceback__)
    )
    try:
        connection.send(("error", error, traceback_text, elapsed))
    except BaseException:
        error_name = f"{type(error).__module__}.{type(error).__qualname__}"
        connection.send(
            ("error_text", error_name, str(error), traceback_text, elapsed)
        )


def _run_task_in_process(
    connection: Connection,
    task: Callable[..., Any],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> None:
    try:
        connection.send(("ready",))
        if connection.recv() != ("run",):
            return

        started = perf_counter()
        try:
            result = task(*args, **kwargs)
        except BaseException as error:
            _send_worker_error(connection, error, perf_counter() - started)
            return

        elapsed = perf_counter() - started
        try:
            connection.send(("result", result, elapsed))
        except BaseException as error:
            _send_worker_error(connection, error, elapsed)
    finally:
        connection.close()


class _UseDefaultTimeout:
    pass


_USE_DEFAULT_TIMEOUT = _UseDefaultTimeout()


class AnswerBook:
    """Run tasks, collect answers, and serialize the results."""

    def __init__(
        self,
        timeout: float | None = None,
        *,
        show_time: bool = False,
        show_log: bool = True,
        base_dir: str | Path | None = None,
    ) -> None:
        self.timeout = self._normalize_timeout(timeout)
        if not isinstance(show_time, bool):
            raise TypeError("show_time 必须是 bool")
        self.show_time = show_time
        self.show_log = show_log
        self.answers: dict[str, dict[str, Any]] = {}
        self._base_dir = (
            caller_directory("AnswerBook()", action="创建")
            if base_dir is None
            else Path(base_dir).resolve()
        )

    @staticmethod
    def _normalize_timeout(timeout: float | None) -> float | None:
        if timeout is None:
            return None
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
            raise TypeError("timeout 必须是正数秒数或 None")
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("timeout 必须是有限的正数")
        return float(timeout)

    @staticmethod
    def _terminate_process(process: Any) -> None:
        if process.is_alive():
            process.terminate()
        process.join(timeout=1)
        if process.is_alive():
            process.kill()
            process.join()

    def _log(self, status: str, label: str, message: str) -> None:
        if self.show_log:
            print(
                f"[{status}] {label}: {message}",
                file=sys.stderr,
                flush=True,
            )

    def _run_with_timeout(
        self,
        label: str,
        task: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        timeout: float,
    ) -> tuple[Any, float]:
        context = get_context("spawn")
        parent_connection, child_connection = context.Pipe(duplex=True)
        process = context.Process(
            target=_run_task_in_process,
            args=(child_connection, task, args, kwargs),
        )

        try:
            process.start()
            child_connection.close()

            if not parent_connection.poll(_PROCESS_START_TIMEOUT):
                self._terminate_process(process)
                raise RuntimeError(
                    f"任务 {label!r} 的子进程未能在 "
                    f"{_PROCESS_START_TIMEOUT:g} 秒内启动"
                )

            try:
                message = parent_connection.recv()
            except EOFError as error:
                process.join()
                raise RuntimeError(
                    f"任务 {label!r} 的子进程在启动时异常退出，"
                    f"退出码为 {process.exitcode}"
                ) from error

            if message != ("ready",):
                self._terminate_process(process)
                raise RuntimeError(f"任务 {label!r} 收到异常的启动消息")

            parent_connection.send(("run",))
            waiting_started = perf_counter()
            if not parent_connection.poll(timeout):
                elapsed = perf_counter() - waiting_started
                self._terminate_process(process)
                raise _TaskTimedOut(label, timeout, elapsed)

            try:
                message = parent_connection.recv()
            except EOFError as error:
                process.join()
                raise RuntimeError(
                    f"任务 {label!r} 的子进程异常退出，"
                    f"退出码为 {process.exitcode}"
                ) from error

            process.join(timeout=1)
            if process.is_alive():
                self._terminate_process(process)

            kind = message[0]
            if kind == "result":
                _, result, elapsed = message
                if elapsed > timeout:
                    raise _TaskTimedOut(label, timeout, elapsed)
                return result, elapsed

            if kind == "error":
                _, error, traceback_text, _ = message
                if isinstance(error, Exception):
                    error.add_note("子进程 traceback:\n" + traceback_text)
                    raise error
                raise RuntimeError(
                    f"任务 {label!r} 在子进程中抛出 "
                    f"{type(error).__qualname__}: {error}\n{traceback_text}"
                )

            if kind == "error_text":
                _, error_name, error_message, traceback_text, _ = message
                raise RuntimeError(
                    f"任务 {label!r} 在子进程中抛出 "
                    f"{error_name}: {error_message}\n{traceback_text}"
                )

            raise RuntimeError(f"任务 {label!r} 返回了未知的子进程消息")
        finally:
            parent_connection.close()
            child_connection.close()
            if process.pid is not None:
                if process.is_alive():
                    self._terminate_process(process)
                else:
                    process.join()
                process.close()

    def run(
        self,
        label: str,
        task: Callable[..., Any],
        /,
        *args: Any,
        timeout: float | None | _UseDefaultTimeout = _USE_DEFAULT_TIMEOUT,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Run one task and store its answer under ``label``."""
        if label in self.answers:
            self._log("FAILED", label, "答案编号重复")
            raise KeyError(f"答案编号重复: {label}")

        effective_timeout = (
            self.timeout
            if timeout is _USE_DEFAULT_TIMEOUT
            else self._normalize_timeout(timeout)
        )

        self._log("START", label, "开始执行")
        try:
            if effective_timeout is None:
                if self.show_time:
                    started = perf_counter()
                    result = task(*args, **kwargs)
                    elapsed = perf_counter() - started
                else:
                    result = task(*args, **kwargs)
                    elapsed = None
            else:
                result, elapsed = self._run_with_timeout(
                    label,
                    task,
                    args,
                    kwargs,
                    effective_timeout,
                )
        except _TaskTimedOut as error:
            answer = {
                "timeout": True,
                "timeout_limit": error.limit,
            }
            if self.show_time:
                answer["time"] = error.elapsed
            self.answers[label] = answer
            self._log(
                "TIMEOUT",
                label,
                f"超过 {error.limit:.6f} 秒限制，子进程已终止",
            )
            return answer
        except BaseException as error:
            self._log(
                "FAILED",
                label,
                f"{type(error).__qualname__}: {error}",
            )
            raise

        answer = {
            "result": (
                dict(result)
                if isinstance(result, Mapping)
                else result
            ),
        }
        if self.show_time:
            answer["time"] = elapsed
        self.answers[label] = answer
        message = (
            f"完成，用时 {elapsed:.6f} 秒"
            if self.show_time
            else "完成"
        )
        self._log("DONE", label, message)
        return answer

    def as_dict(self) -> dict[str, dict[str, Any]]:
        return dict(self.answers)

    def dumps(
        self,
        *,
        indent: int | None = 2,
        inline_simple_lists: bool = True,
    ) -> str:
        return pretty_json(
            self.answers,
            indent=indent,
            inline_simple_lists=inline_simple_lists,
        )

    def print_json(
        self,
        *,
        indent: int | None = 2,
        inline_simple_lists: bool = True,
    ) -> None:
        print(
            self.dumps(
                indent=indent,
                inline_simple_lists=inline_simple_lists,
            )
        )

    def write_json(
        self,
        path: str | Path | None = None,
        *,
        indent: int | None = 2,
        inline_simple_lists: bool = True,
    ) -> Path:
        """Write answers to a UTF-8 file and return its resolved path."""
        output_path = Path("answer.json") if path is None else Path(path)
        if not output_path.is_absolute():
            output_path = self._base_dir / output_path
        output_path = output_path.resolve()

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            self.dumps(
                indent=indent,
                inline_simple_lists=inline_simple_lists,
            )
            + "\n",
            encoding="utf-8",
        )
        return output_path
