from collections import OrderedDict, deque
from copy import copy
from itertools import chain, product
import math
from pathlib import Path
import numpy as np
from numpy.typing import NDArray
import sys
from typing import Any, Iterable, NamedTuple, Hashable

HERE, ROOT = Path(__file__).resolve().parents[:2]
sys.path.insert(0, str(ROOT))

from utils import Case, Exam, read_data

DEBUG = True
if DEBUG:
    log_file = Path("test.log").open("w", encoding="utf-8")
def logit(*s):
    if DEBUG:
        print(*s, file=log_file, flush=True)

Matrix = NDArray[np.int32]

def parse_matrix(data: str) -> Matrix:
    end = data.index('.')
    data = data[:end]
    matrix = [list(map(int, row.split())) for row in data.split(',')]
    return np.array(matrix, np.int32)

exam = Exam(reader=read_data, parser=parse_matrix)
@exam.task(
    Case(
        "2", files=("mat1.txt",)
    )
)
def task2(mat: Matrix):
    return mat.shape
@exam.task(
    Case(
        "3", files=("mat1.txt", "mat2.txt")
    )
)
def task3(mat1: Matrix, mat2: Matrix):
    product = mat1 @ mat2
    return {
        "trace": product.trace(),
        "product": product
    }

class LRUSimulator:
    def __init__(self, cap: int) -> None:
        self.cap = cap
        self.cache = OrderedDict()
        self.main_count, self.hit_count = 0, 0

    def access(self, key):
        try:
            self.cache.move_to_end(key)
            self.hit_count += 1
        except KeyError:
            self.main_count += 1
            if len(self.cache) == self.cap:
                self.cache.popitem(last=False)
            self.cache[key] = None


def task4(m: int, n: int, s: int):
    lru = LRUSimulator(s)
    for i, j, k in product(range(m), range(m), range(n)):
        lru.access(('a', i, k))
        lru.access(('b', k, j))
    return {
        "main_count": lru.main_count,
        "hit_count": lru.hit_count
    }

def task6(m: int, n: int, p: int, s: int):
    lru = LRUSimulator(s)
    for u, v, w in product(range(0, m, p), range(0, m, p), range(0, n, p)):
        for i, j, k in product(range(u, u+p), range(v, v+p), range(w, w+p)):
            lru.access(('a', i, k))
            lru.access(('b', k, j))
    return {
        "main_count": lru.main_count,
        "hit_count": lru.hit_count
    }

def divisors(n: int):
    l = []
    r = []
    for d in range(1, math.isqrt(n) + 1):
        if n % d == 0:
            l.append(d)
            r.append(n // d)
    if l[-1] != r[-1]:
        return l + r[::-1]
    return l + r[-2::-1]

@exam.task(
    Case(
        "7", 200, 150, 600
    )
)
def task7(m: int, n: int, s: int):
    res = min( (task6(m, n, p, s)["main_count"], -p) for p in divisors(math.gcd(m, n)))
    return {
        "min_main_count": res[0],
        "p": -res[1]
    }

if __name__ == "__main__":
    exam.execute(output=True)
