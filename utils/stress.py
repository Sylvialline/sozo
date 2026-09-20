"""用小规模随机或枚举数据对拍两个函数，遇到首个反例立即停止。"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from copy import deepcopy
from hashlib import sha256
from operator import eq
from pathlib import Path
import pickle
from pprint import pformat
from random import Random
import sys
from tempfile import NamedTemporaryFile
from typing import Any

from ._caller import caller_directory


class _AutoFile:
    pass


_AUTO_FILE = _AutoFile()


class StressFailure(AssertionError):
    """保存首次失败的原始参数、两份答案和复现位置；运行异常通过 __cause__ 保留。"""

    def __init__(
        self,
        *,
        seed: int,
        case_index: int,
        phase: str,
        inputs: tuple[Any, ...] | None,
        actual: Any = None,
        expected: Any = None,
        replayed: bool = False,
    ) -> None:
        self.seed = seed
        self.case_index = case_index
        self.phase = phase
        self.inputs = inputs
        self.actual = actual
        self.expected = expected
        self.replayed = replayed
        self.failure_file: Path | None = None
        super().__init__(
            f"Stress {'replay ' if replayed else ''}failed: "
            f"case={case_index}, seed={seed}, phase={phase}\n"
            f"inputs = {pformat(inputs)}\n"
            f"actual = {pformat(actual)}\n"
            f"expected = {pformat(expected)}"
        )


def _failure_path(candidate, reference, failure_file) -> Path | None:
    if failure_file is None:
        return None
    if failure_file is _AUTO_FILE:
        identities = [
            (getattr(task, "__module__", type(task).__module__),
             getattr(task, "__qualname__", type(task).__qualname__))
            for task in (candidate, reference)
        ]
        key = sha256(repr(identities).encode("utf-8")).hexdigest()[:16]
        path = Path(".stress") / f"{key}.pickle"
    else:
        path = Path(failure_file)
    if not path.is_absolute():
        path = caller_directory("stress()") / path
    return path


def _save_failure(path: Path, failure: StressFailure) -> None:
    data = pickle.dumps({
        "version": 1,
        "inputs": failure.inputs,
        "seed": failure.seed,
        "case_index": failure.case_index,
    }, protocol=pickle.HIGHEST_PROTOCOL)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _check(candidate, reference, equal, raw, seed, case_index, replayed=False):
    inputs = actual = expected = None
    phase = "generate"
    try:
        if not isinstance(raw, tuple):
            raise TypeError("each case must be an argument tuple; use (value,) for one argument")
        phase = "copy"
        inputs = deepcopy(raw)
        candidate_args = deepcopy(inputs)
        reference_args = deepcopy(inputs)
        phase = "candidate"
        actual = deepcopy(candidate(*candidate_args))
        phase = "reference"
        expected = deepcopy(reference(*reference_args))
        phase = "compare"
        matches = bool(equal(actual, expected))
    except Exception as error:
        raise StressFailure(
            seed=seed, case_index=case_index, phase=phase,
            inputs=inputs, actual=actual, expected=expected, replayed=replayed,
        ) from error
    if not matches:
        raise StressFailure(
            seed=seed, case_index=case_index, phase="mismatch",
            inputs=inputs, actual=actual, expected=expected, replayed=replayed,
        )


def stress(
    candidate: Callable[..., Any],
    reference: Callable[..., Any],
    cases: Callable[[Random], tuple[Any, ...]] | Iterable[tuple[Any, ...]] | None = None,
    *,
    trials: int = 1000,
    seed: int = 0,
    equal: Callable[[Any, Any], bool] = eq,
    failure_file: str | Path | None | _AutoFile = _AUTO_FILE,
) -> int:
    """对拍 candidate 与 reference，全部通过后打印摘要并返回通过组数。

    cases 可以是 generate(rng)，也可以是参数 tuple 的可迭代对象；每个 tuple
    都展开为一次位置参数调用。单个列表参数写成 (a,)，无参数写成 ()。
    最多运行 trials 组新数据；有限序列提前耗尽则停止，空序列报错。
    默认先重测上次保存的反例；省略 cases 时仅重测反例。返回组数包括重测。

    反例默认按函数身份保存到调用脚本旁的 .stress/；failure_file 可指定路径，
    相对路径也以调用脚本目录为基准。传 None 关闭持久化和重测。
    文件采用 pickle，仅加载自己生成且可信的文件；输入还须支持 pickle。
    重测通过后保留反例，下次新失败覆盖它；两个解法及 equal 都使用当前版本。

    seed 控制独立 Random，不改变全局随机状态。每个解法各取参数的独立深拷贝，
    并立即深拷贝返回值；输入和答案须支持 deepcopy，迭代器答案应先转成 list。
    equal(actual, expected) 默认使用 ==，可换成容差比较或无序比较。

    首次答案不同或运行异常抛出 StressFailure，case_index 从 1 开始。
    同进程执行，不隔离全局变量、不限制耗时，也不把两个解法同时报错视为通过。
    """
    if not callable(candidate) or not callable(reference) or not callable(equal):
        raise TypeError("candidate, reference and equal must be callable")
    if isinstance(trials, bool) or not isinstance(trials, int) or trials <= 0:
        raise ValueError("trials must be a positive integer")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise TypeError("seed must be an integer")

    path = _failure_path(candidate, reference, failure_file)
    replay_count = 0
    if path is not None and path.exists():
        saved = pickle.loads(path.read_bytes())
        if (
            not isinstance(saved, dict) or saved.get("version") != 1
            or not isinstance(saved.get("inputs"), tuple)
            or type(saved.get("seed")) is not int
            or type(saved.get("case_index")) is not int
            or saved["case_index"] < 1
        ):
            raise ValueError(f"Invalid stress failure file: {path}")
        try:
            _check(candidate, reference, equal, saved["inputs"],
                   saved["seed"], saved["case_index"], replayed=True)
        except StressFailure as failure:
            failure.failure_file = path
            failure.add_note(f"Replayed from: {path}")
            raise
        replay_count = 1
        print(f"Stress replay passed: {path}", file=sys.stderr)
    if cases is None:
        if not replay_count:
            raise FileNotFoundError("No saved counterexample; supply cases to start testing")
        return replay_count

    rng = Random(seed)
    generate = cases if callable(cases) else None
    iterator = None if generate is not None else iter(cases)
    end = object()
    passed = 0
    for case_index in range(1, trials + 1):
        try:
            raw = generate(rng) if generate is not None else next(iterator, end)
        except Exception as error:
            raise StressFailure(
                seed=seed, case_index=case_index, phase="generate", inputs=None,
            ) from error
        if raw is end:
            break
        try:
            _check(candidate, reference, equal, raw, seed, case_index)
        except StressFailure as failure:
            if path is not None and failure.phase in (
                "candidate", "reference", "compare", "mismatch",
            ):
                try:
                    _save_failure(path, failure)
                except Exception as error:
                    failure.add_note(f"Could not save counterexample to {path}: {error!r}")
                else:
                    failure.failure_file = path
                    failure.add_note(f"Counterexample saved: {path}")
            raise
        passed += 1

    if not passed:
        raise ValueError("cases must contain at least one case")
    print(f"Stress passed: {passed} cases, seed={seed}", file=sys.stderr)
    return passed + replay_count
