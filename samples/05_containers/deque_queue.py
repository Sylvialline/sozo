"""用途：用 collections.deque 实现 O(1) 双端队列和 BFS 队列。
示例输入：依次入队 A、B，头部加入 START，再出队。
示例输出：START、A、B 的队列处理顺序及 rotate 效果。
复杂度：两端 append/pop/popleft 均 O(1)；中间索引 O(n)。
常见陷阱：list.pop(0) 是 O(n)，队列应使用 deque；deque 不支持切片。
"""

from collections import deque


def main() -> None:
    queue: deque[str] = deque()
    queue.append("A")
    queue.append("B")
    queue.appendleft("START")

    while queue:
        print("serve:", queue.popleft())

    values = deque([1, 2, 3, 4])
    values.rotate(1)                    # 右移一格
    print("rotate:", list(values))
    values.extendleft([8, 9])           # 逐个 appendleft，结果顺序为 9, 8, ...
    print("extendleft:", list(values))


if __name__ == "__main__":
    main()
