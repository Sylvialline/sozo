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
