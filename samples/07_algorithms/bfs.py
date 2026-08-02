"""用途：BFS 求无权图最短边数，并用 parent 还原一条最短路径。
示例输入：0-1、0-2、1-3、2-3、3-4，从 0 到 4。
示例输出：distance=3，path=[0,1,3,4]。
复杂度：邻接表上 O(V+E) 时间，O(V) 队列/距离/父节点空间。
常见陷阱：发现节点（入队）时立刻标记；用 deque.popleft，list.pop(0) 是 O(n)。
"""

from collections import deque


def shortest_path(graph: list[list[int]], start: int, goal: int) -> tuple[int, list[int]]:
    distance = [-1] * len(graph)
    parent = [-1] * len(graph)
    distance[start] = 0
    queue = deque([start])

    while queue:
        node = queue.popleft()
        if node == goal:
            break
        for neighbor in graph[node]:
            if distance[neighbor] != -1:
                continue
            distance[neighbor] = distance[node] + 1
            parent[neighbor] = node
            queue.append(neighbor)

    if distance[goal] == -1:
        return -1, []
    path = []
    node = goal
    while node != -1:
        path.append(node)
        node = parent[node]
    path.reverse()
    return distance[goal], path


def main() -> None:
    graph = [[1, 2], [0, 3], [0, 3], [1, 2, 4], [3]]
    print("distance, path:", shortest_path(graph, 0, 4))


if __name__ == "__main__":
    main()
