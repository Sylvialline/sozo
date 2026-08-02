"""用途：在无向图中枚举全部连通分量，并返回每个分量的节点。
示例输入：边 (0,1)、(1,2)、(3,4)，共 6 个节点。
示例输出：[[0,1,2],[3,4],[5]]，大小 [3,2,1]。
复杂度：O(V+E) 时间，visited、栈和结果 O(V) 空间。
常见陷阱：无向边必须双向加入邻接表；孤立点也是大小为 1 的分量。
"""


def components(graph: list[list[int]]) -> list[list[int]]:
    visited = [False] * len(graph)
    result = []
    for start in range(len(graph)):
        if visited[start]:
            continue
        visited[start] = True
        stack = [start]
        component = []
        while stack:
            node = stack.pop()
            component.append(node)
            for neighbor in graph[node]:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    stack.append(neighbor)
        component.sort()
        result.append(component)
    return result


def main() -> None:
    graph = [[] for _ in range(6)]
    for first, second in [(0, 1), (1, 2), (3, 4)]:
        graph[first].append(second)
        graph[second].append(first)
    result = components(graph)
    print("components:", result)
    print("sizes:", [len(component) for component in result])


if __name__ == "__main__":
    main()
