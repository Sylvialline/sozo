"""用途：用显式栈进行 DFS，避免 Python 递归深度限制。
示例输入：图 0->[1,2]、1->[3]、2->[4]。
示例输出：访问顺序 [0,1,3,2,4]。
复杂度：O(V+E) 时间，visited 与栈 O(V) 空间。
常见陷阱：入栈时标记可防重复入栈；若想保持邻接表顺序，压栈时要 reversed。
"""


def dfs(graph: list[list[int]], start: int) -> list[int]:
    visited = [False] * len(graph)
    visited[start] = True
    stack = [start]
    order = []
    while stack:
        node = stack.pop()
        order.append(node)
        for neighbor in reversed(graph[node]):
            if not visited[neighbor]:
                visited[neighbor] = True
                stack.append(neighbor)
    return order


def main() -> None:
    graph = [[1, 2], [3], [4], [], []]
    print("order:", dfs(graph, 0))


if __name__ == "__main__":
    main()
