"""鸭子类型的运行时多态：不同对象提供同名方法即可。

示例输入：同一行记录分别交给 TextFormatter 和 CsvFormatter。
示例输出：``name=Alice score=95`` 与 ``Alice,95``。
复杂度：格式化含 k 个字段的 dict 为 O(k)。
常见陷阱：Python 的运行时多态不依赖 ``@override``；接口拼写错误到调用时才暴露。
"""

from typing import Protocol


class Formatter(Protocol):
    def format(self, record: dict[str, object]) -> str:
        """将记录格式化为字符串。"""


class TextFormatter:
    def format(self, record: dict[str, object]) -> str:
        return " ".join(f"{key}={value}" for key, value in record.items())


class CsvFormatter:
    def format(self, record: dict[str, object]) -> str:
        return ",".join(map(str, record.values()))


def export(record: dict[str, object], formatter: Formatter) -> str:
    return formatter.format(record)


def main() -> None:
    record = {"name": "Alice", "score": 95}
    for formatter in (TextFormatter(), CsvFormatter()):
        print(export(record, formatter))


if __name__ == "__main__":
    main()
