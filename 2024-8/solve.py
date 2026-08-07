
from collections import defaultdict, Counter
from itertools import batched
import math
from typing import Iterable
from utils import Case, Exam, Series, read_data
import numpy as np

def rd(name: str) -> Iterable[int]:
    data = read_data(name)
    return map(int, data.split(','))


class Matrix:
    def __init__(self, n, m):
        self.n, self.m = n, m
        self.rows = defaultdict(list)
        self.cols = defaultdict(list)

    def display(self):
        mat = np.zeros((self.n, self.m)).astype(int)
        for x, l in self.rows.items():
            for y, w in l:
                mat[x-1, y-1] = w
        print(mat)

    def add_cell(self, x, y, w):
        self.rows[x].append((y, w))
        self.cols[y].append((x, w))

    def transpose(self):
        #fixed: 忘交换 n 和 m
        self.n, self.m = self.m, self.n
        self.rows, self.cols = self.cols, self.rows

    def cells(self):
        for x, v in self.rows.items():
            for y, w in v:
                yield x, y, w

    def _load_format1(self, data: Iterable[int]):
        for i, cell in enumerate(data):
            if cell != 0:
                x, y = divmod(i, self.m)
                self.add_cell(x+1, y+1, cell)

    def _load_format2(self, data: Iterable[int]):
        for batch in batched(data, 3):
            self.add_cell(*batch)

    def _load_format3(self, data: Iterable[int]):
        now = 0
        for batch in batched(data, 2):
            n, w = batch
            now += n
            x, y = divmod(now, self.m)
            self.add_cell(x+1, y+1, w)
            now += 1

    @classmethod
    def from_format(cls, n, m, data: Iterable[int], fmt):
        matrix = cls(n, m)
        if fmt == 1:
            matrix._load_format1(data)
        elif fmt == 2:
            matrix._load_format2(data)
        elif fmt == 3:
            matrix._load_format3(data)

        return matrix

    def max_row(self):
        #fixed: 漏了全零行
        def results():
            for x in range(1, self.n+1):
                yield sum(w for y,w in self.rows.get(x,())), x

        return max(results())

def op(A: Matrix, B: Matrix):
    cells = defaultdict(list)
    for k in A.cols.keys():
        if k not in B.rows:
            continue
        ap = A.cols[k]
        bp = B.rows[k]

        for i, w1 in ap:
            for j, w2 in bp:
                w = w1 * w2
                cells[i, j].append(w)
    result = [0]*(A.n+1)
    for pos, ws in cells.items():
        #fixed: 对每个(i,j)，如果k满了不能算0
        if len(ws) < A.m:
            ws.append(0)
        i, j = pos
        result[i] += max(ws) + min(ws)
    index = max(range(1, A.n+1), key=lambda x: result[x])
    return index, result[index]


class BlockArray:
    def __init__(self, n):
        self.n = n
        self.m = int(n**0.5)
        self.b = math.ceil(self.n / self.m)
        # print(self.n, self.m, self.b)
        self.arr = [0]*(n+1) # [1,n] 
        self.biases = [0]*(self.b+1)
        self.counters = [Counter() for _ in range(self.b+1)]
        for i in range(1, self.n+1):
            bi = (i-1) // self.m + 1
            self.counters[bi][0] += 1
        self.zeros = n

    def modify(self, x, d):
        x = min(x, self.n)
        for bi in range(1, x//self.m + 1):
            self.zeros -= self.counters[bi][-self.biases[bi]]
            self.biases[bi] += d
            self.zeros += self.counters[bi][-self.biases[bi]]

        bi = x//self.m + 1
        if bi > self.b:
            return
        
        counter = self.counters[bi]
        bias = self.biases[bi]
        
        for i in range(x//self.m*self.m+1, x+1):
            if self.arr[i] + bias == 0:
                self.zeros -= 1
            counter[self.arr[i]] -= 1
            self.arr[i] += d
            counter[self.arr[i]] += 1
            if self.arr[i] + bias == 0:
                self.zeros += 1

    def query(self):
        return self.zeros


def zero_count(A: Matrix, r, c):
    n, m = A.n, A.m
    rn, rm = A.n-r+1, A.m-c+1
    ops = defaultdict(list)
    def add(x, y, w):
        if 1<=x<=n and 1<=y<=m:
            ops[x].append((y, w))
    
    for x, y, w in A.cells():
        add(x, y, w)
        add(x-r, y, -w)
        add(x, y-c, -w)
        add(x-r, y-c, w)

    res = 0
    arr = BlockArray(rm)
    for x in range(n, 0, -1):
        for y, d in ops[x]:
            arr.modify(y, d)
            # print("M:", y, d, "| Q:", arr.query())
        if x <= rn:
            res += arr.query()

    return res

def task1(n, m, data: Iterable[int]):
    a = Matrix.from_format(n, m, data, 1)
    res = a.max_row()
    return {
        'row_number': res[1],
        'sum': res[0]
    }

def task2(n, m, data: Iterable[int]):
    a = Matrix.from_format(n, m, data, 2)
    res = a.max_row()
    return {
        'row_number': res[1],
        'sum': res[0]
    }

def task3(n, m, data: Iterable[int]):
    a = Matrix.from_format(n, m, data, 3)
    a.transpose()
    res = a.max_row()
    return {
        'row_number': res[1],
        'sum': res[0]
    }

def task4(A_n, A_m, B_n, B_m, A_data: Iterable[int], B_data: Iterable[int]):
    a = Matrix.from_format(A_n, A_m, A_data, 3)
    b = Matrix.from_format(B_n, B_m, B_data, 3)
    res = op(a, b)
    return {
        'row_number': res[0],
        'sum': res[1]
    }

def task5(n, m, r, c, data: Iterable[int]):
    a = Matrix.from_format(n, m, data, 3)
    # a.display()
    res = zero_count(a, r, c)
    return {
        'zero_count': res
    }


if __name__ == "__main__":
    exam = Exam(reader=rd)
    exam.add(
        task1,
        Series("1", {"a": (6, 4), "b": (100, 150)}, label_separator="."),
    )
    exam.add(
        task2,
        Series(
            "2",
            {"a": (6, 4), "b": (100, 150), "c": (10**6, 10**6)},
            label_separator=".",
        ),
    )
    exam.add(
        task3,
        Series(
            "3",
            {"a": (4, 6), "b": (100, 150), "c": (10**6, 10**6)},
            label_separator=".",
        ),
    )
    exam.add(
        task4,
        Case("4.a", 2, 4, 4, 3, files=("4a", "4b")),
        Case(
            "4.b",
            10**6,
            10**6,
            10**6,
            10**6,
            files=("4c", "4d"),
        ),
        Case(
            "4.c",
            10**6,
            10**6,
            10**6,
            10**6,
            files=("4e", "4f"),
        ),
    )
    exam.add(
        task5,
        Series(
            "5",
            {
                "a": (8, 6, 2, 3),
                "b": (10**6, 10**6, 10, 10),
                "c": (10**6, 10**6, 100, 100),
            },
            label_separator=".",
        ),
    )
    exam.execute()
