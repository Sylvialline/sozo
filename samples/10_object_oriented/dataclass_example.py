"""``dataclass`` 自动生成初始化、比较和表示方法。

示例输入：创建两个带标签的任务，并按 priority/name 排序。
示例输出：Task(priority=1, name='review', tags=['exam']) 排在 priority=2 前。
复杂度：创建 O(字段数)，排序 n 个对象为 O(n log n)。
常见陷阱：可变默认值必须用 ``field(default_factory=list)``，不能直接写 ``[]``。
"""

from dataclasses import dataclass, field


@dataclass(order=True)
class Task:
    priority: int
    name: str
    tags: list[str] = field(default_factory=list, compare=False)


def main() -> None:
    tasks = [
        Task(2, "practice"),
        Task(1, "review", ["exam"]),
    ]
    print("sorted:", sorted(tasks))
    copy_of_first = Task(2, "practice")
    print("value equality:", tasks[0] == copy_of_first)
    copy_of_first.tags.append("new")
    print("independent defaults:", tasks[0].tags, copy_of_first.tags)


if __name__ == "__main__":
    main()
