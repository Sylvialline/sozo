"""覆写时参数名和参数数量不兼容导致的运行时陷阱。

示例输入：分别用位置参数和 ``value=10`` 调用覆写方法。
示例输出：位置参数正常；改名后的关键字调用和少参数调用产生 TypeError。
复杂度：示例调用均为 O(1)。
常见陷阱：类定义阶段通常不检查签名兼容性；关键字参数会绑定“参数名”。
"""

from collections.abc import Callable
import inspect


class BaseProcessor:
    def process(self, value: int) -> int:
        return value * 2


class RenamedParameter(BaseProcessor):
    # 位置调用可用，但 process(value=10) 不再兼容。
    def process(self, x: int) -> int:
        return x * 3


class ExtraRequiredParameter(BaseProcessor):
    # Python 允许定义，但通过 BaseProcessor 接口调用 process(10) 会失败。
    def process(self, value: int, offset: int) -> int:
        return value + offset


def show_type_error(label: str, call: Callable[[], object]) -> None:
    try:
        call()
    except TypeError as error:
        print(f"{label}: {type(error).__name__}")


def main() -> None:
    renamed = RenamedParameter()
    extra = ExtraRequiredParameter()
    print("positional:", renamed.process(10))
    show_type_error("renamed keyword", lambda: renamed.process(value=10))  # type: ignore[call-arg]
    show_type_error("missing argument", lambda: extra.process(10))  # type: ignore[call-arg]
    print("base signature:", inspect.signature(BaseProcessor.process))
    print("child signature:", inspect.signature(RenamedParameter.process))


if __name__ == "__main__":
    main()
