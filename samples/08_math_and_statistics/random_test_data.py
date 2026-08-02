"""可复现的随机测试数据生成：数组、排列和简单无向图。

示例输入：固定种子 2025，生成 6 个整数及 5 个点的 5 条边。
示例输出：每次运行得到完全相同的数据（具体值由 Python 版本实现决定）。
复杂度：生成 n 个数 O(n)；拒绝重复边在图接近完全图时可能明显变慢。
常见陷阱：测试必须固定种子；不要依赖随机数据替代边界用例和穷举校验。
"""

import random


def random_simple_graph(
    rng: random.Random, vertex_count: int, edge_count: int
) -> list[tuple[int, int]]:
    max_edges = vertex_count * (vertex_count - 1) // 2
    if not 0 <= edge_count <= max_edges:
        raise ValueError("invalid edge count")
    all_edges = [
        (u, v) for u in range(vertex_count) for v in range(u + 1, vertex_count)
    ]
    return sorted(rng.sample(all_edges, edge_count))


def main() -> None:
    rng = random.Random(2025)  # 局部 RNG 不会污染模块级随机状态。
    values = [rng.randint(-10, 10) for _ in range(6)]
    permutation = list(range(6))
    rng.shuffle(permutation)
    print("values:", values)
    print("permutation:", permutation)
    print("sample without replacement:", rng.sample(range(20), 4))
    print("graph edges:", random_simple_graph(rng, 5, 5))


if __name__ == "__main__":
    main()
