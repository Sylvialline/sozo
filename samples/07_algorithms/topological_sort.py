"""用途：用 Kahn 算法拓扑排序有向图，并检测环。
示例输入：0->2、1->2、1->3、2->4、3->4。
示例输出：一个合法顺序 [0,1,2,3,4]。
复杂度：O(V+E) 时间，入度、队列和结果 O(V) 空间。
常见陷阱：有多个合法答案；结果长度小于 V 表示有环；这里用最小堆固定输出顺序。
"""

import heapq


def topological_sort(graph: list[list[int]]) -> list[int]:
    indegree = [0] * len(graph)
    for neighbors in graph:
        for neighbor in neighbors:
            indegree[neighbor] += 1
    ready = [node for node, degree in enumerate(indegree) if degree == 0]
    heapq.heapify(ready)
    order = []
    while ready:
        node = heapq.heappop(ready)
        order.append(node)
        for neighbor in graph[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                heapq.heappush(ready, neighbor)
    if len(order) != len(graph):
        raise ValueError("图中存在有向环")
    return order


def main() -> None:
    graph = [[2], [2, 3], [4], [4], []]
    print("order:", topological_sort(graph))
    try:
        topological_sort([[1], [0]])
    except ValueError as error:
        print(type(error).__name__, str(error))


if __name__ == "__main__":
    main()
