
from collections import defaultdict, Counter
from itertools import batched
import json
import math
from typing import Iterable
from utils import read_data as rd


class Matrix:
    def __init__(self, n, m):
        self.n, self.m = n, m
        self.rows = defaultdict(list)
        self.cols = defaultdict(list)

    def add_cell(self, x, y, w):
        self.rows[x].append((y, w))
        self.cols[y].append((x, w))

    def transpose(self):
        self.rows, self.cols = self.cols, self.rows

    def cells(self):
        for x, v in self.rows.items():
            for y, w in v:
                yield x, y, w

    def from_format1(self, data: Iterable[int]):
        for i, cell in enumerate(data):
            x, y = divmod(i, self.m)
            if cell > 0:
                self.add_cell(x+1, y+1, cell)

    def from_format2(self, data: Iterable[int]):
        for batch in batched(data, 3):
            self.add_cell(*batch)

    def from_format3(self, data: Iterable[int]):
        now = 0
        for batch in batched(data, 2):
            n, w = batch
            now += n
            x, y = divmod(now, self.m)
            self.add_cell(x+1, y+1, w)

    def max_row(self):
        res = []
        for row, cs in self.rows.items():
            res.append(sum(w for y,w in cs), row)
        return max(res)

def op(A: Matrix, B: Matrix):
    cells = {}
    for k in A.cols.keys():
        if k not in B.rows:
            continue
        ap = A.cols[k]
        bp = B.rows[k]
        for i, w1 in ap:
            for j, w2 in bp:
                w = w1 * w2
                if (i,j) not in cells:
                    cells[i, j] = w, w
                else:
                    minw, maxw = cells[i, j]
                    cells[i, j] = (
                        min(minw, w),
                        max(maxw, w)
                    )
    result = defaultdict(int)
    for pos, ws in cells.items():
        i, j = pos
        result[i] += ws[0] + ws[1]
    return max(result.items(), key=lambda item: item[1])


class BlockArray:
    def __init__(self, n):
        self.n = n
        self.m = int(n**0.5)
        self.b = math.ceil(self.n / self.m)
        self.arr = [0]*(n+1) # [1,n]
        self.counters = [Counter() for _ in range(self.b+1)]
        self.biases = [0]*(self.b+1)
        self.zeros = n

    def modify(self, x, d):
        for bi in range(1, x//self.m + 1):
            self.zeros -= self.counters[bi][-self.biases[bi]]
            self.biases[bi] += d
            self.zeros += self.counters[bi][-self.biases[bi]]

        counter = self.counters[bi+1]
        bias = self.biases[bi+1]
        
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
    rn, rm = A.n-r+1, A.m-c+1
    ops = defaultdict(list)
    def add(x, y, w):
        if 1<=x<=rn and 1<=y<=rm:
            ops[x].append(y, w)
    
    for x, y, w in A.cells():
        add(x, y, w)
        add(x-r, y, -w)
        add(x, y-c, -w)
        add(x-r, y-c, w)

    res = 0
    arr = BlockArray(rm)
    for x in range(1, rn+1):
        for y, d in ops[x]:
            arr.modify(y, d)
        res += arr.query()

    return res

def task1(n, m, data: str):
    a = Matrix(n, m)
    a.from_format1(data.split(','))
    res = a.max_row()
    return {
        'row_number': res[1],
        'sum': res[0]
    }

def task2(n, m, data: str):
    a = Matrix(n, m)
    a.from_format2(data.split(','))
    res = a.max_row()
    return {
        'row_number': res[1],
        'sum': res[0]
    }

def task3(n, m, data: str):
    a = Matrix(n, m)
    a.from_format3(data.split(','))
    a.transpose()
    res = a.max_row()
    return {
        'row_number': res[1],
        'sum': res[0]
    }

def task4(A_n, A_m, A_data: str, B_n, B_m, B_data: str):
    a = Matrix(A_n, A_m)
    a.from_format3(A_data.split(','))
    b = Matrix(B_n, B_m)
    b.from_format3(B_data.split(','))
    res = op(a, b)
    return {
        'row_number': res[0],
        'sum': res[1]
    }

def task5(n, m, r, c, data: str):
    a = Matrix(n, m)
    a.from_format3(data.split(','))
    res = zero_count(a, r, c)
    return {
        'zero_count': res
    }


if __name__ == "__main__":

    answer = {}
    answer['1.a'] = task1(6, 4, rd('1a'))
    answer['1.b'] = task1(100, 150, rd('1b'))
    
    answer['2.a'] = task2(6, 4, rd('2a'))
    answer['2.b'] = task2(100, 150, rd('2b'))
    answer['2.c'] = task2(10**6, 10**6, rd('2c'))

    answer['3.a'] = task3(4, 6, rd('3a'))
    answer['3.b'] = task3(100, 150, rd('3b'))
    answer['3.c'] = task3(10**6, 10**6, rd('3c'))

    answer['4.a'] = task4(2, 4, rd('4a'), 4, 3, rd('4b'))
    answer['4.b'] = task4(10**6, 10**6, rd('4c'), 10**6, 10**6, rd('4d'))
    answer['4.c'] = task4(10**6, 10**6, rd('4e'), 10**6, 10**6, rd('4f'))

    answer['5.a'] = task5(8, 6, 2, 3, rd('5a'))
    answer['5.b'] = task5(10**6, 10**6, 10, 10, rd('5b'))
    answer['5.c'] = task5(10**6, 10**6, 100, 100, rd('5c'))

    print(json.dumps(answer, indent=2))