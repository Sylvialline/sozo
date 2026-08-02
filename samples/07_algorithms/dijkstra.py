"""用途：Dijkstra 求非负权图的单源最短路，并还原路径。
示例输入：0->1(4)、0->2(1)、2->1(2)、1->3(1)、2->3(5)。
示例输出：到各点距离 [0,3,1,4]，到 3 路径 [0,2,1,3]。
复杂度：邻接表 + 二叉堆为 O((V+E) log V)，空间 O(V+E)。
常见陷阱：不能处理负权边；heapq 是最小堆；必须跳过堆中的陈旧距离。
"""

import heapq
from math import inf


def dijkstra(
    graph: list[list[tuple[int, int]]], start: int
) -> tuple[list[float], list[int]]:
    distances = [inf] * len(graph)
    parent = [-1] * len(graph)
    distances[start] = 0
    heap: list[tuple[float, int]] = [(0, start)]

    while heap:
        distance, node = heapq.heappop(heap)
        if distance != distances[node]:
            continue
        for neighbor, weight in graph[node]:
            if weight < 0:
                raise ValueError("Dijkstra 不允许负权边")
            candidate = distance + weight
            if candidate < distances[neighbor]:
                distances[neighbor] = candidate
                parent[neighbor] = node
                heapq.heappush(heap, (candidate, neighbor))
    return distances, parent


def restore_path(parent: list[int], start: int, goal: int) -> list[int]:
    path = []
    node = goal
    while node != -1:
        path.append(node)
        if node == start:
            return path[::-1]
        node = parent[node]
    return []  # goal 不可达


def main() -> None:
    graph = [[(1, 4), (2, 1)], [(3, 1)], [(1, 2), (3, 5)], []]
    distances, parent = dijkstra(graph, 0)
    print("distances:", distances)
    print("path to 3:", restore_path(parent, 0, 3))


if __name__ == "__main__":
    main()
