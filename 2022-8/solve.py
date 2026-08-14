from collections import deque
from itertools import batched, product
from pathlib import Path
import sys
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

log_file = Path("test.log").open("w", encoding="utf-8")
def debug(s):
    print(s, file=log_file)

from utils import Case, Exam, read_data, read_files
from utils import Graph

def parse_walls(data: str) -> set[tuple[int,int]]:
    return set(batched(map(int, data.split(',')), 2))

exam = Exam(reader=read_data, parser=parse_walls)


MOVES = {
    'U': (-1, 0),
    'L': (0, -1),
    'D': (1, 0),
    'R': (0, 1)
}

DIRS = "ULDR"

def neighbors(cell):
    x, y = cell
    for d, (dx, dy) in MOVES.items():
        yield d, (x+dx, y+dy)


def cell2wall(cell, direction):
    i, j = cell
    if direction=='U':
        return (2*i, 2*j+1)
    if direction=='D':
        return (2*i+2, 2*j+1)
    if direction=='L':
        return (2*i+1, 2*j)
    if direction=='R':
        return (2*i+1, 2*j+2)

def has_wall(cell, direction, walls: set):
    return cell2wall(cell, direction) in walls

def go(cell, direction):
    i, j = cell
    di, dj = MOVES[direction]
    return i + di, j + dj


def all_cells(n):
    return product(range(n), repeat=2)

def all_walls(n):
    k = n*2
    yield from product(range(0, k+1, 2), range(1, k, 2))
    yield from product(range(1, k, 2), range(0, k+1, 2))


class Maze:
    n: int
    walls: set[tuple[int,int]]
    cells: set[tuple[int,int]]
    graph: Graph

    def __init__(self, n: int, walls: set[tuple[int,int]]):
        self.n = n
        self.walls = walls
        self.cells = set(all_cells(self.n))
        self._make_graph()


    def _make_graph(self):
        self.graph = Graph.from_nodes(self.cells)
        for c in self.cells:
            for d, nc in neighbors(c):
                if d not in "LD" or nc not in self.cells:
                    continue
                wall = cell2wall(c, d)
                if wall not in self.walls:
                    self.graph.add_undirected_edge(c, nc)
                    # print(f"Add edge {c} -> {nc}")

    def count_deadend_cells(self):
        res = []
        for c in self.cells:
            count = sum((cell2wall(c, d) in self.walls) for d in MOVES)
            if count == 3:
                res.append(c)
        return {
            "count": len(res),
            "details": res
        }

    def shortest_path_length(self, start, goal):
        "start and goal included"
        dis = {start: 1}
        q = deque([start])
        while q:
            u = q.popleft()
            if u == goal:
                return dis[goal]
            for v in self.graph.neighbors(u):
                if v not in dis:
                    dis[v] = dis[u] + 1
                    q.append(v)


    def is_tree(self):
        ec = self.graph.edge_count(dedupe="undirected")
        nc = self.graph.node_count()
        if ec != nc - 1:
            return False
        
        vis = set([(0, 0)])
        q = deque([(0, 0)])
        while q:
            u = q.popleft()
            for v in self.graph.neighbors(u):
                if v not in vis:
                    vis.add(v)
                    q.append(v)

        return len(vis) == nc


@exam.task(
    Case("1.2", 40, files=("maze2.txt",))
)
def task1_2(n, walls):
    # with Path("test.out").open('w') as stream:
    #     print(f"1.2 {walls=}", file=stream)
    maze = Maze(n, walls)
    return maze.count_deadend_cells()

@exam.task(
    Case(
        "1.3",
        40, (0, 0), (39, 29),
        files=("maze3.txt",)
    )
)
def task1_3(n, start, goal, walls):
    maze = Maze(n, walls)
    return maze.shortest_path_length(start, goal)

@exam.task(
    Case("1.4", 40, files=("data/maze1[0-9].txt",),
         reader=read_files)
)
def task1_4(n, walls_dict: dict[str, set]):
    # print(walls_dict.keys())
    return [
        name
        for name, walls in walls_dict.items()
        if Maze(n, walls).is_tree()
    ]

def parse_list(data: str) -> list[int]:
    return list(map(int, data.split(',')))

@exam.task(
    Case("2.1", 216, files=("sequence.txt",), parser=parse_list)
)
def task2_1(n, seq: list[int]):
    return {
        f"seq[{n}]": seq[n],
        "maximum": max(seq)
    }

def outer_walls(n):
    k = 2*n
    for i in range(1,k,2):
        yield 0, i
        yield k, i
        yield i, 0
        yield i, k


def make_walls_from_p(n, p: list[int]) -> set:
    walls = set()
    walls.update(outer_walls(n))
    for i, j in product(range(1,40), repeat=2):
        s = i*40 + j
        match p[s]:
            case 0:
                wall = cell2wall((i,j), 'U')
            case 1:
                wall = cell2wall((i,j), 'L')
            case 2:
                wall = cell2wall((i-1,j-1), 'D')
            case 3:
                wall = cell2wall((i-1,j-1), "R")
        walls.add(wall)

    return walls

def walls_existence(cells, walls):
    return {
        str(cell): {
            d: "present" if has_wall(cell, d, walls) else "absent"
            for d in DIRS
        }
        for cell in cells
    }

def L_shaped_count(n, walls):
    count = 0
    for c in product(range(n), repeat=2):
        mask = 0
        for i, d in enumerate(DIRS):
            if has_wall(c, d, walls):
                mask |= 1 << i
        if mask in (0b1100, 0b0110, 0b0011, 0b1001):
            count += 1
    return count

@exam.task(
    Case(
        "2.2",
        40,
        files=("p.txt",),
        parser=parse_list
    )
)
def task2_2(n, p: list[int]):
    walls = make_walls_from_p(n, p)

    return {
        'A': walls_existence(((5,25), (20,20), (30,33)), walls),
        'B': L_shaped_count(n, walls)
    }

def make_walls_from_n_c(m: int, start: tuple, n: list[int], c: list[int]):
    closed_cells = set(all_cells(m))
    valid_cells = frozenset(all_cells(m))
    walls = set(all_walls(m))

    now = start
    closed_cells.remove(now)
    while True:
        i, j = now
        for s in range(i+j, len(n)):
            d = DIRS[n[s]]
            nxt = go(now, d)
            if nxt in closed_cells:
                walls.remove(cell2wall(now, d))
                closed_cells.remove(nxt)
                now = nxt
                break
        else:
            for t in range(2*(i+j), len(c)-1, 2):
                cell = c[t], c[t+1]
                if cell not in valid_cells or cell in closed_cells:
                    continue
                if any(adj in closed_cells for _, adj in neighbors(cell)):
                    now = cell
                    break
            else:
                break

    return walls

def longest_straight_passages(n, walls):
    length = 0
    passages = []
    for i in range(n):
        passage = []
        for j in range(n):
            cell = i, j
            passage.append(cell)
            if has_wall(cell, 'R', walls):
                l = len(passage)
                if l == length:
                    passages.append(tuple(passage))
                elif l > length:
                    passages = [tuple(passage)]
                    length = l
                passage = []

    
    for j in range(n):
        passage = []
        for i in range(n):
            cell = i, j
            passage.append(cell)
            if has_wall(cell, 'D', walls):
                l = len(passage)
                if l == length:
                    passages.append(tuple(passage))
                elif l > length:
                    passages = [tuple(passage)]
                    length = l
                passage = []

    return {
        "length": length,
        "passages": passages
    }

# @dataclass(frozen=True, slots=True)
class Status(NamedTuple):
# class Status:

    cell: tuple[int, int]
    toward: str

    def go(self):
        return Status(go(self.cell, self.toward), self.toward)

    def turn(self, direction):
        i = DIRS.index(self.toward) + DIRS.index(direction)
        return Status(self.cell, DIRS[i%4])

    def has_wall(self, direction, walls):
        s = self.turn(direction)
        # debug(
        #     f"Status.has_wall({self=}, {direction=}) = \n"
        #     f"has_wall({s.cell=}, {self.toward=}) = {has_wall(s.cell, self.toward, walls)}"
        # )
        return has_wall(s.cell, s.toward, walls)

    def step(self, walls):
        if self.has_wall('U', walls):
            return self.turn('R')
        front = self.go()
        if front.has_wall('L', walls):
            return front
        return front.turn('L')

def navigate(start, goal, walls):
    assert has_wall(start, 'U', walls)
    now = Status(start, 'R')
    path = [now]
    status_vis = {now}
    while True:
        nxt = now.step(walls)
        assert nxt not in status_vis, "infinite loop"
        path.append(nxt)
        if nxt.cell == goal:
            break
        status_vis.add(nxt)
        now = nxt
        # print(path)

    visited = {s.cell for s in path}
    return {
        "number_visited": len(visited),
        "path": path
    }
        

@exam.task(
    Case(
        "2.3",
        40, (0, 0), (39, 27),
        files=("neighbor.txt", "cell.txt"),
        parser=parse_list,
    )
)
def task2_3(m: int, start: tuple, goal: tuple, n: list[int], c: list[int]):
    walls = make_walls_from_n_c(m, start, n, c)
    outer = set(outer_walls(m))
    # debug(
    #     f"{walls=}\n{outer=}\n"
    #     f"{walls.intersection(outer)=}"
    # )
    assert outer <= walls
    return {
        'A': walls_existence(((5,25), (20,20), (30,33)), walls),
        'B': L_shaped_count(m, walls),
        'C': longest_straight_passages(m, walls),
        'D': navigate(start, goal, walls)
    }


if __name__ == "__main__":
    exam.execute(output=True)