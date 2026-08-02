"""用途：用“当前优先级字典 + 堆”实现可更新、可删除的优先队列。
示例输入：A=5、B=2，随后把 A 更新为 1 并删除 B。
示例输出：只弹出 (1, "A")，旧 A 和 B 条目被惰性跳过。
复杂度：更新 O(log n)，弹出摊还 O(log n)；堆可能暂存 O(更新次数) 个旧条目。
常见陷阱：heapq 不支持任意删除；判断陈旧条目时必须同时核对任务与当前优先级。
"""

import heapq


class MutableMinQueue:
    def __init__(self) -> None:
        self.heap: list[tuple[int, str]] = []
        self.priority: dict[str, int] = {}

    def set(self, task: str, priority: int) -> None:
        self.priority[task] = priority
        heapq.heappush(self.heap, (priority, task))

    def remove(self, task: str) -> None:
        if task not in self.priority:
            raise KeyError(task)
        del self.priority[task]

    def pop(self) -> tuple[int, str]:
        while self.heap:
            priority, task = heapq.heappop(self.heap)
            if self.priority.get(task) == priority:
                del self.priority[task]
                return priority, task
        raise IndexError("pop from empty priority queue")


def main() -> None:
    queue = MutableMinQueue()
    queue.set("A", 5)
    queue.set("B", 2)
    queue.set("A", 1)
    queue.remove("B")
    print(queue.pop())
    try:
        queue.pop()
    except IndexError as error:
        print(type(error).__name__)


if __name__ == "__main__":
    main()
