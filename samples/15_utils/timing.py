"""用途：用上下文管理器测量一段代码耗时。
示例输入：with Timer("sum"): sum(range(100_000))
示例输出：[sum] 约若干 ms
复杂度：计时本身 O(1)。
陷阱：短任务易受系统噪声影响；性能比较应重复多次且使用 perf_counter。
"""

from dataclasses import dataclass, field
from time import perf_counter
from types import TracebackType


@dataclass
class Timer:
    label: str = "elapsed"
    started: float = field(init=False, default=0.0)
    seconds: float = field(init=False, default=0.0)

    def __enter__(self) -> "Timer":
        self.started = perf_counter()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.seconds = perf_counter() - self.started
        print(f"[{self.label}] {self.seconds * 1000:.3f} ms")


def main() -> None:
    with Timer("sum") as timer:
        result = sum(range(100_000))
    print(result, timer.seconds >= 0)


if __name__ == "__main__":
    main()
