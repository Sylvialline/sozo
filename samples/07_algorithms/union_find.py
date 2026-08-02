"""用途：并查集（DSU）维护动态连通性、集合大小和连通分量数。
示例输入：合并 (0,1)、(1,2)、(3,4)。
示例输出：0 与 2 连通、0 所在集合大小 3、共 2 个分量。
复杂度：按大小合并 + 完整路径压缩，单次操作均摊 O(alpha(n))，空间 O(n)。
常见陷阱：find 必须返回根；本实现两遍遍历，一次 find 后访问路径全部直指根。
"""


class UnionFind:
    def __init__(self, n: int) -> None:
        if n < 0:
            raise ValueError("n 不能为负")
        self.parent = list(range(n))
        self._size = [1] * n
        self.components = n

    def find(self, node: int) -> int:
        root = node
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[node] != node:
            parent = self.parent[node]
            self.parent[node] = root
            node = parent
        return root

    def union(self, first: int, second: int) -> bool:
        first_root = self.find(first)
        second_root = self.find(second)
        if first_root == second_root:
            return False
        if self._size[first_root] < self._size[second_root]:
            first_root, second_root = second_root, first_root
        self.parent[second_root] = first_root
        self._size[first_root] += self._size[second_root]
        self.components -= 1
        return True

    def same(self, first: int, second: int) -> bool:
        return self.find(first) == self.find(second)

    def size(self, node: int) -> int:
        return self._size[self.find(node)]


def main() -> None:
    dsu = UnionFind(5)
    for edge in [(0, 1), (1, 2), (3, 4)]:
        print("merged:", edge, dsu.union(*edge))
    print("same(0, 2):", dsu.same(0, 2))
    print("size(0):", dsu.size(0))
    print("components:", dsu.components)


if __name__ == "__main__":
    main()
