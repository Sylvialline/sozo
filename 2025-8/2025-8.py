import heapq
import sys
from typing import List

DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)]

class DSU:
    def __init__(self, n):
        self.fa = list(range(n))
        self.size = [1] * n

    def getfa(self, x):
        return x if x == self.fa[x] else self.getfa(self.fa[x])

    def join(self, x, y):
        fx = self.getfa(x)
        fy = self.getfa(y)
        if fx == fy: return
        if self.size[fx] < self.size[fy]:
            fx, fy = fy, fx
        
        self.fa[fy] = fx
        self.size[fx] += self.size[fy]

    def get_size(self, x):
        return self.size[self.getfa(x)]


class Canvas:

    def __init__(self, n, m):
        self.n, self.m = n, m
        self.grid = [[-1] * m for _ in range(n)]
        self.box = None

    def update_box(self, box):
        
        if self.box is None:
            self.box = box
        else:
            self.box = (
                (min(self.box[0][0], box[0][0]), min(self.box[0][1], box[0][1])),
                (max(self.box[1][0], box[1][0]), max(self.box[1][1], box[1][1]))
            )
    
    def count(self, c):
        return sum(l.count(c) for l in self.grid)

    
    def largest_component(self):
        def get_id(x, y):
                return y + x * self.m

        dsu = DSU(self.n * self.m)
        
        for x in range(self.n):
            for y in range(self.m):
                for dx, dy in DIRECTIONS:
                    nx, ny = x + dx, y + dy
                    if nx < 0 or nx >= self.n or ny < 0 or ny >= self.m:
                        continue
                    if self.grid[x][y] == self.grid[nx][ny]:
                        dsu.join(get_id(x, y), get_id(nx, ny))

        res = [0, 0]
        for x in range(self.n):
            for y in range(self.m):
                c = self.grid[x][y]
                if c >= 0:
                    res[c] = max(res[c], dsu.get_size(get_id(x, y)))
        return res

    def min_path(self):
        s, t = self.box
        t = t[0] - 1, t[1] - 1
        sx, sy = s
        d = {s: (0, 0)}
        h = [((0, 0), s)]
        while h:
            cost, u = heapq.heappop(h)
            x, y = u
            if d[u] < cost:
                continue
            if u == t:
                return cost
            for dx, dy in DIRECTIONS:
                v = nx, ny = x + dx, y + dy
                if nx < 0 or nx >= self.n or ny < 0 or ny >= self.m:
                    continue
                ncost = cost[0] + (self.grid[sx][sy] != self.grid[nx][ny]), cost[1] + 1
                if v not in d or d[v] > ncost:
                    d[v] = ncost
                    heapq.heappush(h, (ncost, v))
        return None

    
class Shape:

    def __init__(self, c):
        self.color = c
        self.cells = None

    def bounding_box(self):
        return ((0, 0), (0, 0)) # [upper left, lower right)
    
    def valid(self, x, y) -> bool:
        pass
        
    def get_cells(self):
        if self.cells is not None:
            return self.cells

        self.cells = []
        
        (x1, y1), (x2, y2) = self.bounding_box()
        
        for i in range(x1, x2):
            for j in range(y1, y2):
                if self.valid(i, j):
                    self.cells.append((i, j))
        return self.cells

    def paint(self, c: Canvas):
        c.update_box(self.bounding_box())
        cells = self.get_cells()
        for x, y in cells:
            c.grid[x][y] = self.color

class Rectangle(Shape):

    def __init__(self, c, x1, y1, x2, y2):
        super().__init__(c)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def bounding_box(self):
        return ((self.x1, self.y1), (self.x2+1, self.y2+1))
    
    def valid(self, x, y) -> bool:
        return True

class Circle(Shape):
    
    def __init__(self, c, x, y, r):
        super().__init__(c)
        self.x = x
        self.y = y
        self.r = r
    
    def bounding_box(self):
        return ((self.x-self.r, self.y-self.r), (self.x+self.r, self.y+self.r))

    def valid(self, x0, y0):
        len_x = min(abs(self.x-x0), abs(self.x-(x0+1)))
        len_y = min(abs(self.y-y0), abs(self.y-(y0+1)))
        return len_x**2 + len_y**2 < self.r**2

class LineSegment(Shape):

    def __init__(self, c, x1, y1, x2, y2):
        super().__init__(c)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

        
    def bounding_box(self):
        return ((min(self.x1, self.x2), min(self.y1, self.y2)), (max(self.x1, self.x2), max(self.y1, self.y2)))
    
    def valid(self, x, y):
        l = [(x, y), (x, y+1), (x+1, y), (x+1, y+1)]
        def is_in(cell):
            x0, y0 = cell
            cross = (self.x1-x0)*(self.y2-y0) - (self.y1-y0)*(self.x2-x0)
            if cross > 0: return 1
            if cross < 0: return -1
            return 0
        res = list(map(is_in, l))
        return max(res) == 1 and min(res) == -1

DEBUG = False

if not DEBUG:
    sys.stdin = open("input.txt", "r", encoding="utf-8")

readl = sys.stdin.readline

def solve():
    it = map(int, readl().split(','))
    shapes: List[Shape] = []
    canvas = Canvas(500, 500)
    cnt = [0, 0, 0]
    while True:
        x = next(it, None)
        if x is None: break
        cnt[x] += 1
        if x == 0:
            shapes.append(Rectangle(next(it), next(it), next(it), next(it), next(it)))
        elif x == 1:
            shapes.append(Circle(next(it), next(it), next(it), next(it)))
        else:
            shapes.append(LineSegment(next(it), next(it), next(it), next(it), next(it)))

    for shape in shapes:
        shape.paint(canvas)

    print(cnt)

    print(canvas.box)

    print(canvas.count(0), canvas.count(1))

    print(canvas.largest_component())

    print(canvas.min_path())

if __name__ == "__main__":
    solve()