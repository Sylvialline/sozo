from __future__ import annotations

from collections import deque
from collections.abc import Hashable, Iterable, Iterator, KeysView, Mapping
from heapq import heappop, heappush
from itertools import count
from typing import Any, Generic, Literal, NamedTuple, TypeVar, overload


NodeT = TypeVar("NodeT", bound=Hashable)


class Condensation(NamedTuple, Generic[NodeT]):
    """强连通分量缩点结果。

    ``graph`` 是以 ``members`` 下标为节点的 DAG；``component_of[u]``
    给出原节点 u 所属分量的下标。
    """

    graph: Graph[int]
    members: tuple[tuple[NodeT, ...], ...]
    component_of: dict[NodeT, int]

    @property
    def components(self) -> tuple[tuple[NodeT, ...], ...]:
        """返回 ``members`` 的兼容别名。"""
        return self.members


class Graph(Generic[NodeT]):
    """节点集合显式且完整的有向图。

    ``adj`` 是节点集合的唯一真相来源，其全部 key 就是图的全部节点。查询
    邻接表永远不会创建节点；``add_edge`` 会按需创建边的两个端点。
    """

    def __init__(
        self,
        adj: Mapping[NodeT, Iterable[Any]] | None = None,
        *,
        weighted: bool = False,
    ) -> None:
        self.adj: dict[NodeT, list[Any]] = {}
        self.weighted = weighted

        if adj is None:
            return

        for u in adj:
            self.add_node(u)

        for u, edges in adj.items():
            for edge in edges:
                if weighted:
                    try:
                        v, w = edge
                    except (TypeError, ValueError) as error:
                        raise ValueError(
                            "weighted adjacency entries must be "
                            "(neighbor, weight) pairs"
                        ) from error
                    self.add_edge(u, v, w)
                else:
                    self.add_edge(u, edge)

    @classmethod
    def from_nodes(
        cls,
        nodes: Iterable[NodeT],
        *,
        weighted: bool = False,
    ) -> Graph[NodeT]:
        """从完整节点集合创建无边图。"""
        return cls({u: [] for u in nodes}, weighted=weighted)

    @classmethod
    @overload
    def from_edges(
        cls,
        edges: Iterable[tuple[NodeT, NodeT]],
        *,
        weighted: Literal[False] = False,
        undirected: bool = False,
    ) -> Graph[NodeT]: ...

    @classmethod
    @overload
    def from_edges(
        cls,
        edges: Iterable[tuple[NodeT, NodeT, Any]],
        *,
        weighted: Literal[True],
        undirected: bool = False,
    ) -> Graph[NodeT]: ...

    @classmethod
    @overload
    def from_edges(
        cls,
        edges: Iterable[tuple[NodeT, ...]],
        *,
        weighted: bool = False,
        undirected: bool = False,
    ) -> Graph[NodeT]: ...

    @classmethod
    def from_edges(
        cls,
        edges: Iterable[tuple[Any, ...]],
        *,
        weighted: bool = False,
        undirected: bool = False,
    ) -> Graph[NodeT]:
        """从边序列创建图，并在运行时校验每条边的长度。"""
        graph = cls(weighted=weighted)

        for edge in edges:
            if weighted:
                try:
                    u, v, w = edge
                except (TypeError, ValueError) as error:
                    raise ValueError(
                        "weighted edges must be "
                        "(source, target, weight) triples"
                    ) from error
                graph.add_edge(u, v, w)
                if undirected:
                    graph.add_edge(v, u, w)
            else:
                try:
                    u, v = edge
                except (TypeError, ValueError) as error:
                    raise ValueError(
                        "unweighted edges must be (source, target) pairs"
                    ) from error
                graph.add_edge(u, v)
                if undirected:
                    graph.add_edge(v, u)

        return graph

    def add_node(self, u: NodeT) -> None:
        """加入节点；节点已存在时不做任何操作。"""
        self.adj.setdefault(u, [])

    def add_edge(self, u: NodeT, v: NodeT, w: Any = None) -> None:
        """加入有向边，并按需创建两个端点。"""
        if not self.weighted and w is not None:
            raise ValueError("cannot add a weight to an unweighted graph")

        self.add_node(u)
        self.add_node(v)
        if self.weighted:
            self.adj[u].append((v, w))
        else:
            self.adj[u].append(v)

    def add_undirected_edge(self, u: NodeT, v: NodeT, w: Any = None) -> None:
        """加入一对方向相反的边。"""
        self.add_edge(u, v, w)
        self.add_edge(v, u, w)

    def __getitem__(self, u: NodeT) -> list[Any]:
        return self.adj[u]

    def __iter__(self) -> Iterator[NodeT]:
        return iter(self.adj)

    def __contains__(self, u: object) -> bool:
        return u in self.adj

    def __len__(self) -> int:
        return len(self.adj)

    def nodes(self) -> KeysView[NodeT]:
        """返回按插入顺序迭代的节点视图。"""
        return self.adj.keys()

    def neighbors(self, u: NodeT) -> Iterator[NodeT]:
        """迭代 u 的出邻居；带权图中忽略权值。"""
        if self.weighted:
            return (v for v, _ in self.adj[u])
        return iter(self.adj[u])

    def edges(self) -> Iterator[tuple[Any, ...]]:
        """按插入顺序迭代边；带权图返回三元组，否则返回二元组。"""
        if self.weighted:
            for u, edges in self.adj.items():
                for v, w in edges:
                    yield u, v, w
        else:
            for u, neighbors in self.adj.items():
                for v in neighbors:
                    yield u, v

    def indegrees(self) -> dict[NodeT, int]:
        """返回每个节点的入度。"""
        degrees = {u: 0 for u in self}
        for u in self:
            for v in self.neighbors(u):
                degrees[v] += 1
        return degrees

    def outdegrees(self) -> dict[NodeT, int]:
        """返回每个节点的出度。"""
        return {u: len(self.adj[u]) for u in self}

    def reverse(self) -> Graph[NodeT]:
        """返回所有边反向后的新图。"""
        graph = Graph.from_nodes(self, weighted=self.weighted)
        if self.weighted:
            for u, v, w in self.edges():
                graph.add_edge(v, u, w)
        else:
            for u, v in self.edges():
                graph.add_edge(v, u)
        return graph

    def node_count(self) -> int:
        """返回节点数。"""
        return len(self.adj)

    def edge_count(
        self,
        dedupe: Literal["none", "parallel", "undirected"] = "none",
    ) -> int:
        """返回边数，可选择去除平行边或进一步合并反向边。

        ``dedupe="none"`` 统计全部边；``"parallel"`` 去除同向平行边；
        ``"undirected"`` 还会把方向相反的边视为同一条边。
        """
        if dedupe == "none":
            return sum(len(neighbors) for neighbors in self.adj.values())

        if dedupe not in ("parallel", "undirected"):
            raise ValueError(f"unknown dedupe level: {dedupe}")

        seen = set()

        for edge in self.edges():
            u, v = edge[:2]

            if dedupe == "undirected":
                key = frozenset((u, v))
            else:
                key = (u, v)

            seen.add(key)

        return len(seen)

    def bfs_distances(self, start: NodeT) -> dict[NodeT, int]:
        """返回从起点出发的最少边数，带权图也忽略权值。

        起点距离约定为 0，不可达节点不会出现在结果中。若题目计算访问的节点
        数而不是经过的边数，由调用方自行加 1。
        """
        if start not in self:
            raise KeyError(start)

        distances = {start: 0}
        queue = deque([start])
        while queue:
            u = queue.popleft()
            for v in self.neighbors(u):
                if v not in distances:
                    distances[v] = distances[u] + 1
                    queue.append(v)
        return distances

    def dijkstra_distances(self, start: NodeT) -> dict[NodeT, Any]:
        """返回从起点出发的带权最短距离。

        图必须带权且所有可达边权非负。起点距离为 0，不可达节点不会出现在
        结果中。
        """
        if not self.weighted:
            raise ValueError("dijkstra_distances() requires a weighted graph")
        if start not in self:
            raise KeyError(start)

        distances: dict[NodeT, Any] = {start: 0}
        order = count()
        heap = [(0, next(order), start)]

        while heap:
            distance, _, u = heappop(heap)
            if distance != distances[u]:
                continue

            for v, weight in self.adj[u]:
                if weight < 0:
                    raise ValueError(
                        "Dijkstra does not support negative edge weights"
                    )
                candidate = distance + weight
                if v not in distances or candidate < distances[v]:
                    distances[v] = candidate
                    heappush(heap, (candidate, next(order), v))

        return distances

    def topological_sort(self, *, reverse: bool = False) -> list[NodeT]:
        """返回拓扑序；图中存在环时抛出 ``ValueError``。

        默认令每条边 ``u -> v`` 的 u 位于 v 前；``reverse=True`` 时汇点
        位于其前驱之前。
        """
        indegree = self.indegrees()
        ready = deque(u for u in self if indegree[u] == 0)
        order: list[NodeT] = []

        while ready:
            u = ready.popleft()
            order.append(u)
            for v in self.neighbors(u):
                indegree[v] -= 1
                if indegree[v] == 0:
                    ready.append(v)

        if len(order) != len(self):
            raise ValueError("graph contains a cycle; no topological order exists")

        if reverse:
            order.reverse()
        return order

    def strongly_connected_components(
        self,
    ) -> tuple[tuple[NodeT, ...], ...]:
        """按 Tarjan 出栈顺序返回强连通分量，汇分量通常在前。"""
        index: dict[NodeT, int] = {}
        lowlink: dict[NodeT, int] = {}
        stack: list[NodeT] = []
        on_stack: set[NodeT] = set()
        components: list[tuple[NodeT, ...]] = []
        next_index = 0

        for start in self:
            if start in index:
                continue

            index[start] = lowlink[start] = next_index
            next_index += 1
            stack.append(start)
            on_stack.add(start)
            frames: list[tuple[NodeT, Iterator[NodeT], NodeT | None]] = [
                (start, self.neighbors(start), None)
            ]

            while frames:
                u, neighbors, parent = frames[-1]
                try:
                    v = next(neighbors)
                except StopIteration:
                    frames.pop()
                    if parent is not None:
                        lowlink[parent] = min(lowlink[parent], lowlink[u])

                    if lowlink[u] == index[u]:
                        component: list[NodeT] = []
                        while True:
                            v = stack.pop()
                            on_stack.remove(v)
                            component.append(v)
                            if v == u:
                                break
                        components.append(tuple(component))
                    continue

                if v not in index:
                    index[v] = lowlink[v] = next_index
                    next_index += 1
                    stack.append(v)
                    on_stack.add(v)
                    frames.append((v, self.neighbors(v), u))
                elif v in on_stack:
                    lowlink[u] = min(lowlink[u], index[v])

        return tuple(components)

    def condensation(self) -> Condensation[NodeT]:
        """把强连通分量缩为 DAG，并保留所有跨分量边。"""
        components = self.strongly_connected_components()
        component_of = {
            u: component
            for component, members in enumerate(components)
            for u in members
        }
        graph = Graph.from_nodes(
            range(len(components)),
            weighted=self.weighted,
        )
        if self.weighted:
            for u, v, w in self.edges():
                source = component_of[u]
                target = component_of[v]
                if source != target:
                    graph.add_edge(source, target, w)
        else:
            for u, v in self.edges():
                source = component_of[u]
                target = component_of[v]
                if source != target:
                    graph.add_edge(source, target)

        return Condensation(graph, components, component_of)

    def condense(self) -> Condensation[NodeT]:
        """返回 ``condensation`` 的兼容别名。"""
        return self.condensation()
