from collections import OrderedDict
from itertools import product
import math

class LRUSimulator:
    def __init__(self, cap: int) -> None:
        self.cap = cap
        self.cache = OrderedDict()
        self.main_count, self.cache_count = 0, 0

    def get(self, key):
        try:
            self.cache.move_to_end(key)
            self.cache_count += 1
        except KeyError:
            self.main_count += 1
            if len(self.cache) == self.cap:
                self.cache.popitem(last=False)
            self.cache[key] = None

def task4(m: int, n: int, s: int):
    lru = LRUSimulator(s)
    for i, j, k in product(range(m), range(m), range(n)):
        lru.get(('a', i, k))
        lru.get(('b', k, j))
    return {
        "main_count": lru.main_count,
        "cache_count": lru.cache_count
    }

def task6(m: int, n: int, p: int, s: int):
    lru = LRUSimulator(s)
    for u, v, w in product(range(0, m, p), range(0, m, p), range(0, n, p)):
        for i, j, k in product(range(u, u+p), range(v, v+p), range(w, w+p)):
            lru.get(('a', i, k))
            lru.get(('b', k, j))
    return {
        "main_count": lru.main_count,
        "cache_count": lru.cache_count
    }

def task6_pureloop(m: int, n: int, p: int, s: int):
    lru = LRUSimulator(s)
    for u in range(0, m, p):
        for v in range(0, m, p):
            for w in range(0, n, p):
                for i in range(u, u + p):
                    for j in range(v, v + p):
                        for k in range(w, w + p):
                            lru.get(('a', i, k))
                            lru.get(('b', k, j))
    return {
        "main_count": lru.main_count,
        "cache_count": lru.cache_count
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

def task7(m: int, n: int, s: int):
    res = min( (task6(m, n, p, s)["main_count"], -p) for p in divisors(math.gcd(m, n)))
    return {
        "min_main_count": res[0],
        "p": -res[1]
    }

if __name__ == "__main__":
    print(task7(200, 150, 600))
