from __future__ import annotations

from collections.abc import Hashable, Iterable
from typing import Generic, TypeVar


K = TypeVar("K", bound=Hashable)


class DSU:
    """带路径压缩和按集合大小合并的并查集。

    元素编号必须位于 ``0 <= x < n``。``union`` 在两个集合原本分离时
    返回 True，已经连通时返回 False。
    """

    __slots__ = ("parent", "_size", "components")

    def __init__(self, n: int) -> None:
        if n < 0:
            raise ValueError("n 不能为负数")
        self.parent = list(range(n))
        self._size = [1] * n
        self.components = n

    def find(self, x: int) -> int:
        """返回 x 所在集合的代表元，并完整压缩访问路径。"""
        root = x
        while root != self.parent[root]:
            root = self.parent[root]

        while x != root:
            parent = self.parent[x]
            self.parent[x] = root
            x = parent

        return root

    def union(self, a: int, b: int) -> bool:
        """合并 a、b 所在集合；发生合并时返回 True。"""
        a = self.find(a)
        b = self.find(b)
        if a == b:
            return False

        if self._size[a] < self._size[b]:
            a, b = b, a

        self.parent[b] = a
        self._size[a] += self._size[b]
        self.components -= 1
        return True

    def same(self, a: int, b: int) -> bool:
        """返回 a 和 b 是否属于同一集合。"""
        return self.find(a) == self.find(b)

    def size(self, x: int) -> int:
        """返回 x 所在集合的元素数量。"""
        return self._size[self.find(x)]

    @property
    def component_count(self) -> int:
        """返回当前互不相交集合的数量。"""
        return self.components

    def roots(self) -> set[int]:
        """返回当前所有根的集合，并顺便压缩全部节点的路径。"""
        return {self.find(x) for x in range(len(self.parent))}

    def members(self, x: int) -> list[int]:
        """返回 x 所在集合的全部元素，结果按编号升序排列。"""
        root = self.find(x)
        return [node for node in range(len(self.parent)) if self.find(node) == root]

    def groups(self) -> dict[int, list[int]]:
        """按根返回所有集合；返回值是快照，修改它不会影响并查集。"""
        result: dict[int, list[int]] = {}
        for node in range(len(self.parent)):
            result.setdefault(self.find(node), []).append(node)
        return result


class KeyedDSU(Generic[K]):
    """以任意可哈希对象为键的并查集。

    支持初始化后通过 ``add`` 动态加入键；查询或合并未知键会抛出
    ``KeyError``，不会静默创建节点。``union`` 的返回约定与 ``DSU`` 相同。
    """

    __slots__ = ("parent", "_size", "components")

    def __init__(self, keys: Iterable[K] = ()) -> None:
        self.parent: dict[K, K] = {}
        self._size: dict[K, int] = {}
        self.components = 0

        for key in keys:
            self.add(key)

    def __contains__(self, key: object) -> bool:
        return key in self.parent

    def __len__(self) -> int:
        return len(self.parent)

    def add(self, key: K) -> bool:
        """加入一个独立键；实际新增时返回 True。"""
        if key in self.parent:
            return False

        self.parent[key] = key
        self._size[key] = 1
        self.components += 1
        return True

    def find(self, key: K) -> K:
        """返回 key 所在集合的代表键，并完整压缩访问路径。"""
        try:
            root = self.parent[key]
        except KeyError:
            raise KeyError(f"unknown key: {key!r}") from None

        while root != self.parent[root]:
            root = self.parent[root]

        while key != root:
            parent = self.parent[key]
            self.parent[key] = root
            key = parent

        return root

    def union(self, a: K, b: K) -> bool:
        """合并 a、b 所在集合；发生合并时返回 True。"""
        a = self.find(a)
        b = self.find(b)
        if a == b:
            return False

        if self._size[a] < self._size[b]:
            a, b = b, a

        self.parent[b] = a
        self._size[a] += self._size[b]
        self.components -= 1
        return True

    def same(self, a: K, b: K) -> bool:
        """返回 a 和 b 是否属于同一集合。"""
        return self.find(a) == self.find(b)

    def size(self, key: K) -> int:
        """返回 key 所在集合的元素数量。"""
        return self._size[self.find(key)]

    @property
    def component_count(self) -> int:
        """返回当前互不相交集合的数量。"""
        return self.components

    def roots(self) -> set[K]:
        """返回当前所有根的集合，并顺便压缩全部键的路径。"""
        return {self.find(key) for key in self.parent}

    def members(self, key: K) -> list[K]:
        """返回 key 所在集合的全部元素，保持键的加入顺序。"""
        root = self.find(key)
        return [item for item in self.parent if self.find(item) == root]

    def groups(self) -> dict[K, list[K]]:
        """按根返回所有集合；元素保持加入顺序，返回值是快照。"""
        result: dict[K, list[K]] = {}
        for key in self.parent:
            result.setdefault(self.find(key), []).append(key)
        return result
