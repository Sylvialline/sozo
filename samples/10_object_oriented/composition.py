"""组合：对象持有并委托给其他对象，避免不自然的继承关系。

示例输入：Report 使用 MemoryRepository 取数据、使用 Formatter 生成文本。
示例输出：``A:10 | B:20``。
复杂度：n 条记录的读取与格式化均为 O(n)。
常见陷阱：组合对象常应通过构造参数注入，便于替换、测试和复用。
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Item:
    name: str
    value: int


class Repository(Protocol):
    def load(self) -> list[Item]:
        """加载条目。"""


class MemoryRepository:
    def __init__(self, items: list[Item]) -> None:
        self._items = items[:]

    def load(self) -> list[Item]:
        return self._items[:]


class Formatter:
    def format(self, items: list[Item]) -> str:
        return " | ".join(f"{item.name}:{item.value}" for item in items)


class Report:
    def __init__(self, repository: Repository, formatter: Formatter) -> None:
        self.repository = repository
        self.formatter = formatter

    def render(self) -> str:
        return self.formatter.format(self.repository.load())


def main() -> None:
    repository = MemoryRepository([Item("A", 10), Item("B", 20)])
    report = Report(repository, Formatter())
    print(report.render())


if __name__ == "__main__":
    main()
