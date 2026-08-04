from __future__ import annotations

import inspect
import json
import math
import sys
import traceback
from collections.abc import Callable, Mapping
from multiprocessing import get_context
from multiprocessing.connection import Connection
from pathlib import Path
from time import perf_counter
from typing import Any


_PROCESS_START_TIMEOUT = 30.0


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
    """Run tasks, collect timed answers, and serialize the results."""

    def __init__(
        self,
        timeout: float | None = None,
        *,
        show_log: bool = True,
    ) -> None:
        self.timeout = self._normalize_timeout(timeout)
        self.show_log = show_log
        self.answers: dict[str, dict[str, Any]] = {}
        self._base_dir = self._caller_directory()

    @staticmethod
    def _caller_directory() -> Path:
        frame = inspect.currentframe()
        if frame is None or frame.f_back is None or frame.f_back.f_back is None:
            raise RuntimeError("无法确定 AnswerBook() 的调用代码文件")

        try:
            caller_filename = frame.f_back.f_back.f_code.co_filename
        finally:
            del frame

        if caller_filename.startswith("<") and caller_filename.endswith(">"):
            raise RuntimeError("AnswerBook() 必须从代码文件中创建")
        return Path(caller_filename).resolve().parent

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
        """Run and time one task, then store its answer under ``label``."""
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
                started = perf_counter()
                result = task(*args, **kwargs)
                elapsed = perf_counter() - started
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
                "time": error.elapsed,
                "timeout_limit": error.limit,
            }
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

        answer = dict(result) if isinstance(result, Mapping) else {"result": result}
        if "time" in answer:
            self._log("FAILED", label, "task 返回值包含保留键 'time'")
            raise KeyError("task 返回值不能包含保留键 'time'")
        answer["time"] = elapsed
        self.answers[label] = answer
        self._log("DONE", label, f"完成，用时 {elapsed:.6f} 秒")
        return answer

    def as_dict(self) -> dict[str, dict[str, Any]]:
        return dict(self.answers)

    def dumps(self, *, indent: int | None = 2) -> str:
        return json.dumps(self.answers, ensure_ascii=False, indent=indent)

    def print_json(self, *, indent: int | None = 2) -> None:
        print(self.dumps(indent=indent))

    def write_json(
        self,
        path: str | Path | None = None,
        *,
        indent: int | None = 2,
    ) -> Path:
        """Write answers to a UTF-8 file and return its resolved path."""
        output_path = Path("output.txt") if path is None else Path(path)
        if not output_path.is_absolute():
            output_path = self._base_dir / output_path
        output_path = output_path.resolve()

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            self.dumps(indent=indent) + "\n",
            encoding="utf-8",
        )
        return output_path
