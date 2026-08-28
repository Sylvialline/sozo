from __future__ import annotations

import argparse
import json
from collections import deque
from itertools import combinations
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "edges.txt"
DEFAULT_OUTPUT_DIR = ROOT / "answers"
NODES = 100
INF = 10**9

Edge = tuple[int, int]


class DSU:
    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.size = [1] * n
        self.components = n

    def find(self, x: int) -> int:
        while x != self.parent[x]:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x: int, y: int) -> bool:
        x, y = self.find(x), self.find(y)
        if x == y:
            return False
        if self.size[x] < self.size[y]:
            x, y = y, x
        self.parent[y] = x
        self.size[x] += self.size[y]
        self.components -= 1
        return True


def read_edges(path: Path) -> list[Edge]:
    edges: list[Edge] = []
    for line_number, line in enumerate(path.read_text(encoding="ascii").splitlines(), 1):
        fields = line.split()
        if len(fields) != 2:
            raise ValueError(f"line {line_number}: expected two integers")
        u, v = map(int, fields)
        edges.append((u - 1, v - 1))
    return edges


def make_adjacency(edges: list[Edge], count: int) -> list[set[int]]:
    adjacency = [set() for _ in range(NODES)]
    for u, v in edges[:count]:
        adjacency[u].add(v)
        adjacency[v].add(u)
    return adjacency


def component_sizes(adjacency: list[set[int]]) -> list[int]:
    unseen = set(range(NODES))
    sizes: list[int] = []
    while unseen:
        start = unseen.pop()
        stack = [start]
        size = 0
        while stack:
            u = stack.pop()
            size += 1
            new_nodes = adjacency[u] & unseen
            unseen.difference_update(new_nodes)
            stack.extend(new_nodes)
        sizes.append(size)
    return sorted(sizes, reverse=True)


def cluster_coefficient(adjacency: list[set[int]], vertex: int) -> float:
    neighbors = adjacency[vertex]
    degree = len(neighbors)
    if degree <= 1:
        return 0.0
    neighbor_edges = sum(v in adjacency[u] for u, v in combinations(neighbors, 2))
    return neighbor_edges / (degree * (degree - 1) / 2)


def average_cluster_coefficient(adjacency: list[set[int]]) -> float:
    return sum(cluster_coefficient(adjacency, v) for v in range(NODES)) / NODES


def first_connected_prefix(edges: list[Edge]) -> int:
    dsu = DSU(NODES)
    for count, (u, v) in enumerate(edges, 1):
        dsu.union(u, v)
        if dsu.components == 1:
            return count
    raise ValueError("the complete edge sequence never becomes connected")


def all_pairs_distances(adjacency: list[set[int]]) -> list[list[int]]:
    distances: list[list[int]] = []
    for source in range(NODES):
        dist = [INF] * NODES
        dist[source] = 0
        queue = deque([source])
        while queue:
            u = queue.popleft()
            next_distance = dist[u] + 1
            for v in adjacency[u]:
                if dist[v] == INF:
                    dist[v] = next_distance
                    queue.append(v)
        if INF in dist:
            raise ValueError("all-pairs distances requested for a disconnected graph")
        distances.append(dist)
    return distances


def average_pair_distance(distances: list[list[int]]) -> float:
    total = sum(distances[u][v] for u in range(NODES) for v in range(u + 1, NODES))
    return total / (NODES * (NODES - 1) / 2)


def q4_diameter_events(edges: list[Edge], g3_count: int) -> list[list[int]]:
    distances = all_pairs_distances(make_adjacency(edges, g3_count))
    diameter = max(map(max, distances))
    events: list[list[int]] = []

    # For one inserted undirected edge (u, v), every newly shortest path uses
    # that edge at most once. Capturing the old u/v columns therefore permits
    # an O(n^2) exact APSP update.
    for count, (u, v) in enumerate(edges[g3_count:], g3_count + 1):
        to_u = [distances[x][u] for x in range(NODES)]
        to_v = [distances[x][v] for x in range(NODES)]
        from_u = distances[u][:]
        from_v = distances[v][:]

        new_diameter = 0
        for i in range(NODES):
            row = distances[i]
            via_uv_base = to_u[i] + 1
            via_vu_base = to_v[i] + 1
            for j in range(NODES):
                row[j] = min(row[j], via_uv_base + from_v[j], via_vu_base + from_u[j])
                if row[j] > new_diameter:
                    new_diameter = row[j]

        if new_diameter < diameter:
            events.append([count, new_diameter])
            diameter = new_diameter

    return events


def solve(edges: list[Edge]) -> dict[str, Any]:
    if len(edges) != 4950:
        raise ValueError(f"expected 4950 edges, got {len(edges)}")

    g2 = make_adjacency(edges, 181)
    g3_count = first_connected_prefix(edges)
    g3 = make_adjacency(edges, g3_count)
    g4 = make_adjacency(edges, g3_count + 100)
    g3_distances = all_pairs_distances(g3)
    g4_distances = all_pairs_distances(g4)

    return {
        "q2_1_component_sizes": component_sizes(g2),
        "q2_2_cluster_coefficients_nodes_1_to_10": [
            cluster_coefficient(g2, v) for v in range(10)
        ],
        "q2_3_average_cluster_coefficient_g2": average_cluster_coefficient(g2),
        "q2_4_first_connected_edge_count": g3_count,
        "q2_4_average_cluster_coefficient_g3": average_cluster_coefficient(g3),
        "q2_5_average_cluster_coefficient_g4": average_cluster_coefficient(g4),
        "q3_distance_27_63_g3": g3_distances[26][62],
        "q3_distance_27_63_g4": g4_distances[26][62],
        "q3_average_diameter_g3": average_pair_distance(g3_distances),
        "q3_average_diameter_g4": average_pair_distance(g4_distances),
        "q4_diameter_decrease_events": q4_diameter_events(edges, g3_count),
    }


def format_float(value: float) -> str:
    result = f"{value:.9f}".rstrip("0").rstrip(".")
    return result if "." in result else result + ".0"


def render_markdown(answers: dict[str, Any]) -> str:
    q2_2 = " ".join(format_float(x) for x in answers["q2_2_cluster_coefficients_nodes_1_to_10"])
    q4 = "\n".join(f"{count} {diameter}" for count, diameter in answers["q4_diameter_decrease_events"])
    return f"""# 标准答案

所有小数均保留了足够的有效位。Q4 按日文原题所述的直径计算。

## Q1

下图给出一种无交叉画法；顶点的具体位置不唯一。

![Q1 的一种平面画法](q1_answer.svg)

## Q2

### Q2-1

```text
{' '.join(map(str, answers['q2_1_component_sizes']))}
```

### Q2-2

```text
{q2_2}
```

### Q2-3

```text
{format_float(answers['q2_3_average_cluster_coefficient_g2'])}
```

### Q2-4

最小边数 $N$ 与 $G_3$ 的平均聚类系数：

```text
{answers['q2_4_first_connected_edge_count']}
{format_float(answers['q2_4_average_cluster_coefficient_g3'])}
```

### Q2-5

```text
{format_float(answers['q2_5_average_cluster_coefficient_g4'])}
```

## Q3

依次为 $G_3$ 中 27 到 63 的距离、$G_4$ 中的距离、$G_3$ 的平均直径、$G_4$ 的平均直径：

```text
{answers['q3_distance_27_63_g3']}
{answers['q3_distance_27_63_g4']}
{format_float(answers['q3_average_diameter_g3'])}
{format_float(answers['q3_average_diameter_g4'])}
```

## Q4

```text
{q4}
```
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute all standard answers.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    answers = solve(read_edges(args.input))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "answers.json").write_text(
        json.dumps(answers, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.output_dir / "standard_answers.md").write_text(
        render_markdown(answers), encoding="utf-8"
    )
    print(f"wrote standard answers to {args.output_dir}")


if __name__ == "__main__":
    main()
