from itertools import product
from pathlib import Path

import numpy as np

HERE, ROOT = Path(__file__).resolve().parents[:2]
DATA = HERE/"data"
OUTPUT = HERE/"output"

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
        is_overlapped(x1, x1+w1, x2, x2+w2) and
        is_overlapped(y1, y1+h1, y2, y2+h2) and
        not (is_touched(x1, x1+w1, x2, x2+w2) and is_touched(y1, y1+h1, y2, y2+h2))
    )


class Plane:
    def __init__(self, size = N) -> None:
        self.size = size
        self.n = self.m = self.size
        self.grid = np.zeros([self.n, self.m], np.int16)
        self.rectangles = [] # (x, y, w, h)
        self.dsu = DSU(self.size)
        self.cluster_areas = [0] * self.size
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

    def view(self, rec):
        x, y, w, h = rec
        return self.grid[x:x+w, y:y+h]

    def compute_component_of(self):
        self.component_of = np.full([self.n, self.m], -1, np.int16)
        for i, (x, y, w, h) in enumerate(self.rectangles):
            self.component_of[x:x+w, y:y+h] = self.dsu.find(i)

    def dry_add(self, rec):
        x, y, w, h = rec
        view = self.grid[x:x+w, y:y+h]
        new_thickness = max(self.max_thickness, int(view.max()) + 1)
        try:
            component_of = self.component_of
            will_connected_roots = set()
            for i in range(max(x-1, 0), min(x+w+1, self.n)):
                for j in range(max(y-1, 0), min(y+h+1, self.m)):
                    if (i == x-1 or i == x+w+1) and (j == y-1 or j == y+h+1):
                        continue
                    root = int(component_of[i][j])
                    if root != -1:
                        will_connected_roots.add(root)
            
        except AttributeError:
            will_connected_roots = {self.dsu.find(i) for i, r in enumerate(self.rectangles) if is_connected(r, rec)}

        expanded_area = w * h - int(np.count_nonzero(view))
        cluster_area = sum(self.cluster_areas[root] for root in will_connected_roots) + expanded_area
        new_max_area = max(self.max_cluster_area, cluster_area)
        return new_thickness, new_max_area
        

    def add(self, rec):
        id = len(self.rectangles)
        # for i, r in enumerate(self.rectangles):
        #     if is_connected(r, rec):
        #         print(f"connected: {i}:{r} and {id}:{rec}")
        will_connected_roots = {self.dsu.find(i) for i, r in enumerate(self.rectangles) if is_connected(r, rec)}
        self.rectangles.append(rec)

        view = self.view(rec)
        self.max_thickness = max(self.max_thickness, int(view.max()) + 1)
        x, y, w, h = rec
        expanded_area = w * h - int(np.count_nonzero(view))
        view += 1

        cluster_area = sum(self.cluster_areas[root] for root in will_connected_roots) + expanded_area
        self.max_cluster_area = max(self.max_cluster_area, cluster_area)
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
        info = {
            "max thickness": self.max_thickness,
            "max cluster area": self.max_cluster_area,
            "clusters": self.clusters_info()
        }
        return info


def read_rectangles(filename: str):
    with (DATA/filename).open() as f:
        recs = [tuple(map(int, line.split())) for line in f.readlines()]
    return recs

def test0():
    plane = Plane.from_rectangles(read_rectangles("10.txt"))
    print(plane.info())

def task1():
    plane = Plane.from_rectangles(read_rectangles("10.txt"))
    return {
        "max thickness": plane.max_thickness,
        "num of clusters": plane.num_clusters,
        "max number of elements": plane.max_cluster_size,
        "max cluster area": plane.max_cluster_area
    }

def task2():
    return sum(
        w * h
        for x, y, w, h
        in read_rectangles("1000.txt")
    )

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
    with (OUTPUT/"array.txt").open('w') as f:
        for l in plane.component_of.tolist():
            print(l, file=f)
    for x, y in product(range(N-w), range(N-h)):
        if x % 100 == 0 and y == 0: print(x, y)
        rec = (x, y, w, h)
        nth, narea = plane.dry_add(rec)
        # print(f"{th=}, {nth=}")
        if nth > th:
            assert nth == th + 1
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

# test0()

book = AnswerBook()
book.run('1', task1)
book.run('2', task2)
book.run('3', task3)
book.run('4', task4)

book.write_json()



