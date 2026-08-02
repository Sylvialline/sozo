"""用途：用 heapq 实现最小优先队列（C++ priority_queue 默认恰好相反）。
示例输入：(优先级, 名称) = (3,C)、(1,A)、(2,B)。
示例输出：按 1:A、2:B、3:C 弹出。
复杂度：heapify O(n)，heappush/heappop O(log n)，查看 heap[0] O(1)。
常见陷阱：heap 列表整体并非有序；元组首项相同会继续比较后项，后项须可比较。
"""

import heapq


def main() -> None:
    heap = [(3, "C"), (1, "A"), (2, "B")]
    heapq.heapify(heap)
    heapq.heappush(heap, (0, "urgent"))
    print("minimum:", heap[0])

    while heap:
        priority, name = heapq.heappop(heap)
        print(priority, name)

    values = [9, 1, 8, 2, 7]
    print("three smallest:", heapq.nsmallest(3, values))


if __name__ == "__main__":
    main()
