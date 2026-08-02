"""用途：在通用 Python 3 中用负数把 heapq 最小堆转成数值最大堆。
示例输入：[3, 1, 4, 1, 5]。
示例输出：5 4 3 1 1。
复杂度：heapify O(n)，每次弹出 O(log n)，全部排序式弹出 O(n log n)。
常见陷阱：入堆和出堆都要取反；(负优先级, 序号, 对象) 可避免对象不可比较。
"""

import heapq
from itertools import count


def main() -> None:
    values = [3, 1, 4, 1, 5]
    heap = [-value for value in values]
    heapq.heapify(heap)
    print("descending:", [(-heapq.heappop(heap)) for _ in range(len(heap))])

    serial = count()
    jobs: list[tuple[int, int, dict[str, str]]] = []
    for priority, name in [(2, "compile"), (5, "answer"), (5, "check")]:
        heapq.heappush(jobs, (-priority, next(serial), {"name": name}))
    while jobs:
        negative_priority, _, job = heapq.heappop(jobs)
        print(-negative_priority, job["name"])


if __name__ == "__main__":
    main()
