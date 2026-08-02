"""继承、普通方法覆写、``super()`` 与可选 ``@override`` 标记。

示例输入：Dog("Pochi").speak()。
示例输出：Pochi says woof；通过 Animal 引用调用时仍执行 Dog 方法。
复杂度：示例方法均为 O(1)。
常见陷阱：Python 覆写不需要修饰器；``@override`` 主要服务 IDE/类型检查器。
"""

from collections.abc import Callable
from typing import Any, TypeVar

try:
    # Python 3.12+ 标准库提供；它不改变运行时多态行为。
    from typing import override
except ImportError:
    F = TypeVar("F", bound=Callable[..., Any])

    def override(method: F) -> F:
        """Python 3.11- 的无依赖运行时回退；静态检查可选 typing_extensions。"""
        return method


class Animal:
    def __init__(self, name: str) -> None:
        self.name = name

    def speak(self) -> str:
        return f"{self.name} makes a sound"


class Dog(Animal):
    @override
    def speak(self) -> str:
        return f"{self.name} says woof"


class GuideDog(Dog):
    @override
    def speak(self) -> str:
        return super().speak() + " and is ready to guide"


def announce(animal: Animal) -> None:
    print(animal.speak())


def main() -> None:
    announce(Animal("Unknown"))
    announce(Dog("Pochi"))
    announce(GuideDog("Hachi"))


if __name__ == "__main__":
    main()
