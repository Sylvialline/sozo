
from collections import deque
import json


Per = tuple[int, ...]

I_STR = "URFDLB"
I: Per = (0, 1, 2, 3, 4, 5)
X: Per = (2, 1, 3, 5, 4, 0)
Y: Per = (0, 5, 1, 3, 2, 4)
Z: Per = (4, 0, 2, 1, 3, 5)

def mul(p1: Per, p2: Per):
    return tuple(p1[p2[i]] for i in range(6))

def inv(p: Per):
    return tuple(p.index(i) for i in range(6))

def to_str(p: Per):
    return I_STR[p[0]] + I_STR[p[1]]

def all_pers_by_XY():
    path_book: dict[Per, list[Per]] = {I:[]}
    q = deque([I])
    while q:
        u = q.popleft()
        pathu = path_book[u]
        for w in X, Y:
            v = mul(u, w)
            if v not in path_book:
                path_book[v] = pathu + [w]
                q.append(v)

    return path_book


per_pathes = all_pers_by_XY()
pers = set(per_pathes.keys())

def task31():
    print(len(pers))

    for k, v in per_pathes.items():
        print(to_str(k), [to_str(x) for x in v])

def task32():
    for p in pers:
        print(to_str(p), to_str(inv(p)))

print("3.1")
task31()
print("3.2")
task32()