"""用途：用递归 DFS 演示最简图遍历与进入/退出时机。
示例输入：图 0->[1,2]、1->[3]、2->[4]。
示例输出：preorder=[0,1,3,2,4]，postorder=[3,1,4,2,0]。
复杂度：O(V+E) 时间，visited 与递归栈 O(V) 空间。
常见陷阱：Python 默认递归深度约千层；大图优先改迭代 DFS，不要盲目调高限制。
"""


def dfs_orders(graph: list[list[int]], start: int) -> tuple[list[int], list[int]]:
    visited = [False] * len(graph)
    preorder: list[int] = []
    postorder: list[int] = []

    def visit(node: int) -> None:
        visited[node] = True
        preorder.append(node)
        for neighbor in graph[node]:
            if not visited[neighbor]:
                visit(neighbor)
        postorder.append(node)

    visit(start)
    return preorder, postorder


def main() -> None:
    graph = [[1, 2], [3], [4], [], []]
    preorder, postorder = dfs_orders(graph, 0)
    print("preorder:", preorder)
    print("postorder:", postorder)


if __name__ == "__main__":
    main()
