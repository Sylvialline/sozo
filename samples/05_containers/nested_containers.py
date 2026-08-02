"""用途：安全创建二维表、邻接表以及 dict 内嵌容器。
示例输入：2×3 零矩阵；边 (0,1)、(1,2)。
示例输出：仅修改一个矩阵格；邻接表 [[1], [0, 2], [1]]。
复杂度：矩阵初始化 O(nm)，建无向图 O(V+E) 空间。
常见陷阱：[[0] * m] * n 会让每一行引用同一个 list，修改一格会改多行。
"""


def main() -> None:
    rows, columns = 2, 3
    matrix = [[0] * columns for _ in range(rows)]  # 每轮新建一行
    matrix[0][1] = 7
    print("matrix:", matrix)

    graph = [[] for _ in range(3)]
    for u, v in [(0, 1), (1, 2)]:
        graph[u].append(v)
        graph[v].append(u)
    print("graph:", graph)

    table: dict[str, dict[str, int]] = {}
    table.setdefault("Tokyo", {})["A"] = 3
    print("nested dict:", table)


if __name__ == "__main__":
    main()
