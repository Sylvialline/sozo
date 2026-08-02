"""用 ``__lt__`` 排对象，以及更常用、更灵活的 ``key=`` 排序。

示例输入：三个 Record(score, name) 对象。
示例输出：默认按 score/name 升序；key 可按 score 降序、name 升序。
复杂度：排序 n 个对象为 O(n log n)。
常见陷阱：``list.sort()`` 原地修改并返回 None；只为排序时通常优先写 key。
"""


class Record:
    def __init__(self, name: str, score: int) -> None:
        self.name = name
        self.score = score

    def __lt__(self, other: "Record") -> bool:
        return (self.score, self.name) < (other.score, other.name)

    def __repr__(self) -> str:
        return f"Record({self.name!r}, {self.score})"


def main() -> None:
    records = [Record("Bob", 80), Record("Alice", 90), Record("Carol", 80)]
    print("by __lt__:", sorted(records))
    print("custom key:", sorted(records, key=lambda item: (-item.score, item.name)))

    copied = records[:]
    result = copied.sort()
    print("sort return:", result)
    print("sort mutated:", copied)


if __name__ == "__main__":
    main()
