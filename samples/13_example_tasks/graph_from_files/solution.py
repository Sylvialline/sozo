"""用途：读取无向图边表并求各连通分量大小。
示例输入：第一行 n m，后续 m 行为 u v。
示例输出：components: 3；sizes: 3 2 2。
复杂度：O(V + E) 时间和 O(V + E) 空间。
陷阱：节点编号为 0..n-1；递归 DFS 可能超过 Python 递归深度限制。
"""

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read_graph(path: Path) -> list[list[int]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    n, m = map(int, lines[0].split())
    graph = [[] for _ in range(n)]
    if len(lines) - 1 != m:
        raise ValueError("edge count does not match header")
    for line in lines[1:]:
        u, v = map(int, line.split())
        graph[u].append(v)
        graph[v].append(u)
    return graph


def component_sizes(graph: list[list[int]]) -> list[int]:
    seen = bytearray(len(graph))
    sizes = []
    for start in range(len(graph)):
        if seen[start]:
            continue
        seen[start] = 1
        stack = [start]
        size = 0
        while stack:
            node = stack.pop()
            size += 1
            for neighbor in graph[node]:
                if not seen[neighbor]:
                    seen[neighbor] = 1
                    stack.append(neighbor)
        sizes.append(size)
    return sorted(sizes, reverse=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        default=ROOT / "input" / "graph1.txt",
    )
    args = parser.parse_args()
    sizes = component_sizes(read_graph(args.input))
    print(f"components: {len(sizes)}")
    print("sizes:", *sizes)


if __name__ == "__main__":
    main()
