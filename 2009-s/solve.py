from collections import defaultdict
from itertools import chain, product
from pathlib import Path
import sys

HERE, ROOT = Path(__file__).resolve().parents[:2]
DATA = HERE / "data"
OUTPUT = HERE / "output"

sys.path.insert(0, str(ROOT))
from utils.answer_book import AnswerBook
from utils.dsu import DSU

N = 1000

def is_overlapped(l1, r1, l2, r2):
    return l1 <= r2 and l2 <= r1

def is_touched(l1, r1, l2, r2):
    return l1 == r2 or l2 == r1

def is_connected(rec1, rec2):
    x1, y1, w1, h1 = rec1
    x2, y2, w2, h2 = rec2
    return (
        is_overlapped(x1, x1 + w1, x2, x2 + w2) and
        is_overlapped(y1, y1 + h1, y2, y2 + h2) and
        not (is_touched(x1, x1 + w1, x2, x2 + w2) and is_touched(y1, y1 + h1, y2, y2 + h2))
    )

class Plane:
    def __init__(self) -> None:
        self.n = self.m = N
        self.grid = [[0] * self.m for _ in range(self.n)]
        self.rectangles = []  # (x, y, w, h)
        self.dsu = DSU(N)
        self.cluster_areas = [0] * N
        self.max_thickness = 0
        self.max_cluster_area = 0

    def roots(self):
        return {self.dsu.find(u) for u in range(len(self.rectangles))}

    @property
    def num_clusters(self):
        return len(self.roots())

    @property
    def max_cluster_size(self):
        return max(self.dsu.size(root) for root in self.roots())

    def compute_component_of(self):
        """将每个矩形覆盖的区域标记为其所属的并查集根"""
        self.component_of = [[-1] * self.m for _ in range(self.n)]
        for i, (x, y, w, h) in enumerate(self.rectangles):
            root = self.dsu.find(i)
            for r in range(x, x + w):
                for c in range(y, y + h):
                    self.component_of[r][c] = root

    def dry_add(self, rec):
        """模拟添加矩形，返回 (新厚度, 新最大簇面积)"""
        x, y, w, h = rec

        max_val = 0
        non_zero = 0
        for r in range(x, x + w):
            for c in range(y, y + h):
                val = self.grid[r][c]
                if val > max_val:
                    max_val = val
                if val != 0:
                    non_zero += 1

        new_thickness = max(self.max_thickness, max_val + 1)

        # 找出所有会与新增矩形连通的根（包括内部和外部边界）
        try:
            comp = self.component_of
            will_connected_roots = set()
            # 扫描扩展边界框 [x-1, x+w] x [y-1, y+h]，但跳过四角
            for i in range(max(x - 1, 0), min(x + w + 1, self.n)):
                for j in range(max(y - 1, 0), min(y + h + 1, self.m)):
                    # 跳过四个角点
                    #fixed: 错判成 i==x+w+1
                    if (i == x - 1 or i == x + w) and (j == y - 1 or j == y + h):
                        continue
                    root = comp[i][j]
                    if root != -1:
                        will_connected_roots.add(root)
        except AttributeError:
            # component_of 尚未计算，回退到矩形连通性判断
            will_connected_roots = {
                self.dsu.find(i)
                for i, r in enumerate(self.rectangles)
                if is_connected(r, rec)
            }

        expanded_area = w * h - non_zero
        cluster_area = sum(self.cluster_areas[root] for root in will_connected_roots) + expanded_area
        new_max_area = max(self.max_cluster_area, cluster_area)

        return new_thickness, new_max_area

    def add(self, rec):
        """真正添加一个矩形"""
        id = len(self.rectangles)

        will_connected_roots = {
            self.dsu.find(i)
            for i, r in enumerate(self.rectangles)
            if is_connected(r, rec)
        }

        self.rectangles.append(rec)
        x, y, w, h = rec

        max_val = 0
        non_zero = 0
        for r in range(x, x + w):
            for c in range(y, y + h):
                val = self.grid[r][c]
                if val > max_val:
                    max_val = val
                if val != 0:
                    non_zero += 1
                self.grid[r][c] += 1

        self.max_thickness = max(self.max_thickness, max_val + 1)

        expanded_area = w * h - non_zero
        cluster_area = sum(self.cluster_areas[root] for root in will_connected_roots) + expanded_area
        self.max_cluster_area = max(self.max_cluster_area, cluster_area)

        # 合并并查集
        for root in will_connected_roots:
            self.dsu.union(root, id)
        root = self.dsu.find(id)
        self.cluster_areas[root] = cluster_area

    @classmethod
    def from_rectangles(cls, recs):
        plane = cls()
        for rec in recs:
            plane.add(rec)
        return plane

    def clusters_info(self):
        info = {}
        for root in self.roots():
            info[root] = {
                "size": self.dsu.size(root),
                "members": self.dsu.members(root),
                "area": self.cluster_areas[root]
            }
        return info

    def info(self):
        return {
            "max thickness": self.max_thickness,
            "max cluster area": self.max_cluster_area,
            "clusters": self.clusters_info()
        }


def read_rectangles(filename: str):
    with (DATA / filename).open() as f:
        return [tuple(map(int, line.split())) for line in f]


def task1():
    plane = Plane.from_rectangles(read_rectangles("10.txt"))
    return {
        "max thickness": plane.max_thickness,
        "num of clusters": plane.num_clusters,
        "max number of elements": plane.max_cluster_size,
        "max cluster area": plane.max_cluster_area
    }


def task2():
    return sum(w * h for _, _, w, h in read_rectangles("1000.txt"))


def task3():
    plane = Plane.from_rectangles(read_rectangles("1000.txt"))
    return {
        "max thickness": plane.max_thickness,
        "num clusters": plane.num_clusters,
        "max number of elements": plane.max_cluster_size,
        "max cluster area": plane.max_cluster_area
    }


def task4():
    plane = Plane.from_rectangles(read_rectangles("1000.txt"))
    w, h = 5, 10
    c1, c2 = 0, 0
    th = plane.max_thickness
    max_area = plane.max_cluster_area
    plane.compute_component_of()

    for x, y in product(range(N - w), range(N - h)):
        rec = (x, y, w, h)
        nth, narea = plane.dry_add(rec)

        if nth > th:
            c1 += 1

        if narea == max_area:
            c2 += 1
        elif narea > max_area:
            max_area = narea
            c2 = 1

    return {
        "thickness increased count": c1,
        "area maximized count": c2
    }

class SegmentTree:
    """区间加，询问全局最大值。标记永久化。"""
    def __init__(self, n) -> None:
        self.n = n # [0, n)
        self.lim = n << 2
        self.val = [0] * self.lim
        self.lazy = [0] * self.lim

    def _add(self, p, l, r, x, y, d):
        if x <= l and r <= y:
            self.val[p] += d
            self.lazy[p] += d
            return
        mid = l+r>>1
        if mid >= x:
            self._add(p<<1, l, mid, x, y, d)
        if mid < y:
            self._add(p<<1|1, mid+1, r, x, y, d)
        self.val[p] = self.lazy[p] + max(self.val[p<<1], self.val[p<<1|1])

    def add(self, x, y, d):
        self._add(1, 0, self.n - 1, x, y, d)

    def get(self):
        return self.val[1]

def task5():
    recs = [(x, y, x + w, y + h) for x, y, w, h in read_rectangles("q5.txt")]
    y_cords = sorted(set(chain.from_iterable((y1, y2) for x1, y1, x2, y2 in recs)))
    y_index = {y:idx for idx, y in enumerate(y_cords)}
    events = defaultdict(list)
    for x1, y1, x2, y2 in recs:
        y1 = y_index[y1]
        y2 = y_index[y2]
        events[x1].append((y1, y2, 1))
        events[x2].append((y1, y2, -1))

    tree = SegmentTree(len(y_cords))
    res = 0
    for x, qs in sorted(events.items()):
        for y1, y2, d in qs:
            tree.add(y1, y2, d)
        res = max(res, tree.get())
    return res
        


if __name__ == "__main__":
    book = AnswerBook()
    book.run('1', task1)
    book.run('2', task2)
    book.run('3', task3)
    book.run('4', task4)
    book.run('5', task5)
    book.write_json()