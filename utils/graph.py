from __future__ import annotations

from collections import deque
from collections.abc import Hashable, Iterable, Iterator, Mapping
from heapq import heappop, heappush
from itertools import count
from typing import Any, Literal, NamedTuple


Node = Hashable


class Condensation(NamedTuple):
    """The SCC condensation of a graph.

    ``graph`` is a DAG whose nodes are the integer indices of ``members``.
    ``component_of[u]`` gives the index containing ``u``.
    """

    graph: Graph
    members: tuple[tuple[Node, ...], ...]
    component_of: dict[Node, int]

    @property
    def components(self) -> tuple[tuple[Node, ...], ...]:
        """Alias for ``members``."""
        return self.members


class Graph:
    """A directed graph with an explicit, complete node set.

    ``adj`` is the single source of truth for the node set: its keys are all
    nodes in the graph. Reading an adjacency list never creates a node.
    ``add_edge`` creates both endpoint nodes when necessary.
    """

    def __init__(
        self,
        adj: Mapping[Node, Iterable[Any]] | None = None,
        *,
        weighted: bool = False,
    ) -> None:
        self.adj: dict[Node, list[Any]] = {}
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
                            "weighted 图的边必须形如 (u, v, w) 中的 (v, w)"
                        ) from error
                    self.add_edge(u, v, w)
                else:
                    self.add_edge(u, edge)

    @classmethod
    def from_nodes(
        cls,
        nodes: Iterable[Node],
        *,
        weighted: bool = False,
    ) -> Graph:
        return cls({u: [] for u in nodes}, weighted=weighted)

    @classmethod
    def from_edges(
        cls,
        edges: Iterable[tuple[Any, ...]],
        *,
        weighted: bool = False,
        undirected: bool = False,
    ) -> Graph:
        graph = cls(weighted=weighted)

        for edge in edges:
            if weighted:
                try:
                    u, v, w = edge
                except (TypeError, ValueError) as error:
                    raise ValueError(
                        "weighted 图的边必须形如 (u, v, w)"
                    ) from error
                graph.add_edge(u, v, w)
                if undirected:
                    graph.add_edge(v, u, w)
            else:
                try:
                    u, v = edge
                except (TypeError, ValueError) as error:
                    raise ValueError(
                        "unweighted 图的边必须形如 (u, v)"
                    ) from error
                graph.add_edge(u, v)
                if undirected:
                    graph.add_edge(v, u)

        return graph

    def add_node(self, u: Node) -> None:
        self.adj.setdefault(u, [])

    def add_edge(self, u: Node, v: Node, w: Any = None) -> None:
        if not self.weighted and w is not None:
            raise ValueError("unweighted 图不能添加权重")

        self.add_node(u)
        self.add_node(v)
        if self.weighted:
            self.adj[u].append((v, w))
        else:
            self.adj[u].append(v)

    def add_undirected_edge(self, u: Node, v: Node, w: Any = None) -> None:
        self.add_edge(u, v, w)
        self.add_edge(v, u, w)

    def __getitem__(self, u: Node) -> list[Any]:
        return self.adj[u]

    def __iter__(self) -> Iterator[Node]:
        return iter(self.adj)

    def __contains__(self, u: object) -> bool:
        return u in self.adj

    def __len__(self) -> int:
        return len(self.adj)

    def nodes(self):
        return self.adj.keys()

    def neighbors(self, u: Node) -> Iterator[Node]:
        if self.weighted:
            return (v for v, _ in self.adj[u])
        return iter(self.adj[u])

    def edges(self) -> Iterator[tuple[Any, ...]]:
        if self.weighted:
            for u, edges in self.adj.items():
                for v, w in edges:
                    yield u, v, w
        else:
            for u, neighbors in self.adj.items():
                for v in neighbors:
                    yield u, v

    def indegrees(self) -> dict[Node, int]:
        degrees = {u: 0 for u in self}
        for u in self:
            for v in self.neighbors(u):
                degrees[v] += 1
        return degrees

    def outdegrees(self) -> dict[Node, int]:
        return {u: len(self.adj[u]) for u in self}

    def reverse(self) -> Graph:
        graph = Graph.from_nodes(self, weighted=self.weighted)
        if self.weighted:
            for u, v, w in self.edges():
                graph.add_edge(v, u, w)
        else:
            for u, v in self.edges():
                graph.add_edge(v, u)
        return graph

    def node_count(self) -> int:
        return len(self.adj)

    def edge_count(
        self,
        dedupe: Literal["none", "parallel", "undirected"] = "none",
    ) -> int:
        """
        dedupe:
            "none"       - count all edges
            "parallel"   - deduplicate edges with the same direction
            "undirected" - additionally merge opposite directions
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

    def bfs_distances(self, start: Node) -> dict[Node, int]:
        """Return minimum edge counts from ``start``, ignoring edge weights.

        The start node has distance 0. Unreachable nodes are omitted. If a
        problem counts visited nodes rather than traversed edges, add 1 at the
        call site. On a weighted graph, weights are intentionally ignored.
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

    def dijkstra_distances(self, start: Node) -> dict[Node, Any]:
        """Return weighted shortest-path distances from ``start``.

        The graph must be weighted and reachable edge weights must be
        nonnegative. The start node has distance 0; unreachable nodes are
        omitted.
        """
        if not self.weighted:
            raise ValueError("dijkstra_distances() 只适用于带权图")
        if start not in self:
            raise KeyError(start)

        distances: dict[Node, Any] = {start: 0}
        order = count()
        heap = [(0, next(order), start)]

        while heap:
            distance, _, u = heappop(heap)
            if distance != distances[u]:
                continue

            for v, weight in self.adj[u]:
                if weight < 0:
                    raise ValueError("Dijkstra 不支持负权边")
                candidate = distance + weight
                if v not in distances or candidate < distances[v]:
                    distances[v] = candidate
                    heappush(heap, (candidate, next(order), v))

        return distances

    def topological_sort(self, *, reverse: bool = False) -> list[Node]:
        """Return a topological order, or raise ``ValueError`` for a cycle.

        An edge ``u -> v`` puts ``u`` before ``v`` by default. With
        ``reverse=True``, sinks come before their predecessors.
        """
        indegree = self.indegrees()
        ready = deque(u for u in self if indegree[u] == 0)
        order: list[Node] = []

        while ready:
            u = ready.popleft()
            order.append(u)
            for v in self.neighbors(u):
                indegree[v] -= 1
                if indegree[v] == 0:
                    ready.append(v)

        if len(order) != len(self):
            raise ValueError("图包含环，无法进行拓扑排序")

        if reverse:
            order.reverse()
        return order

    def strongly_connected_components(self) -> tuple[tuple[Node, ...], ...]:
        """Return SCCs in Tarjan pop order (for edges, sink SCCs come first)."""
        index: dict[Node, int] = {}
        lowlink: dict[Node, int] = {}
        stack: list[Node] = []
        on_stack: set[Node] = set()
        components: list[tuple[Node, ...]] = []
        next_index = 0

        for start in self:
            if start in index:
                continue

            index[start] = lowlink[start] = next_index
            next_index += 1
            stack.append(start)
            on_stack.add(start)
            frames: list[tuple[Node, Iterator[Node], Node | None]] = [
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
                        component: list[Node] = []
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

    def condensation(self) -> Condensation:
        """Contract SCCs into a DAG while preserving cross-component edges."""
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

    def condense(self) -> Condensation:
        """Alias for :meth:`condensation`."""
        return self.condensation()
