from collections import defaultdict
from functools import partial
from itertools import accumulate, combinations
from pathlib import Path
import sys
import math, numpy as np
from scipy.signal import convolve

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OFFICIAL_DATA = HERE / "official_data"
sys.path.insert(0, str(ROOT))

from utils import Case, Exam, read_data, read_files

def parse(data: str) -> list[int]:
    return list(map(int, data.split(':')))

read_official_files = partial(
    read_files,
    base_dir=OFFICIAL_DATA
)

read_official_data = partial(
    read_data,
    base_dir=OFFICIAL_DATA
)

exam = Exam(reader=read_data, parser=parse)

@exam.task(
    Case(
        "1.1",
        files=("infections.txt",),
        reader=read_official_files
    )
)
def task1_1(data: list[int]):
    return sorted(set(data), reverse=True)[9]

@exam.task(
    Case(
        "1.2",
        files=("",),
        reader=read_official_data
    )
)
def task1_2(data: dict[str, list[int]]):
    return sum(
        sorted(set(d), reverse=True)[9]
        for d in data.values()
    )

@exam.task(
    Case(
        "1.3",
        files=("infections.txt",),
        reader=read_official_files
    )
)
def task1_3(a: list[int]):
    res = []
    prev = 0
    for x in a:
        res.append(f"{x - prev:+}")
        prev = x
    seq = ''.join(res)
    return {
        "len": len(seq),
        "sequence": seq
    }

@exam.task(
    Case(
        "1.4",
        files=("infections.txt",),
        reader=read_official_files
    )
)
def task1_4(a: list[int]):
    p = (0, 0)
    buc = defaultdict(lambda: defaultdict(list))
    for i, d in enumerate(a, start=1):
        buc[d-p[1]][i-p[0]].append((p[0]+1, i))
        if d <= p[1]:
            p = (i, d)

    max_v = max(buc.keys())
    bucv = buc[max_v]
    min_span = min(bucv.keys())
    l = bucv[min_span]

    return{
        "sum": max_v,
        "periods": [f"From Day {i} to {j}" for i,j in l]
    }


@exam.task(
    Case(
        "2.1",
        files=("infections.txt",),
        reader=read_official_files
    )
)
def task2_1(a: list[int]):
    n = len(a)
    pre = [0] + list(accumulate(a))
    res = [(pre[i]-pre[i-7])/7 for i in range(7, n+1)]
    return {
        "min": f"{min(res):.4f}",
        "max": f"{max(res):.4f}",
        "sum": f"{sum(res):.4f}"
    }

def compute_similarity(a: list[int], b: list[int]):
    if len(a) < len(b):
        a, b = b, a
    m, n = len(a), len(b)
    a_sqr_pre = list(accumulate(x*x for x in a)) + [0]
    b_sqr = sum(x*x for x in b)
    #fixed: b.reverse() 原地修改会影响到外部的 data.items()！
    bp = b[::-1]
    ab = convolve(a, bp, mode="valid")
    res = max(2*int(x) - b_sqr - (a_sqr_pre[i+n-1] - a_sqr_pre[i-1]) for i, x in enumerate(ab))
    return res

@exam.task(
    Case(
        "2.2",
        files=("",),
        reader=read_official_data
    )
)
def task2_2(data: dict[str, list[int]]):
    book = defaultdict(list)
    for (name_a, a), (name_a, b) in combinations(data.items(), 2):
        sim = compute_similarity(a, b)
        book[sim].append((name_a, name_a))

    max_sim = max(book.keys())
    return {
        "similarity_score": max_sim,
        "file_pairs": book[max_sim],
        "all_results": {
            k:book[k] for k in sorted(book, reverse=True)
        }
    }


@exam.task(
    Case(
        "2.3",
        files=("infections2.txt",),
        reader=read_official_files
    )
)
def task2_3(x: list[int]):
    n = len(x)
    sum_x = sum(x)
    sum_ix = sum(i*xi for i, xi in enumerate(x))
    sum_i = n*(n-1)/2
    sum_i_2 = n*(n-1)*(2*n-1)/6
    den = n*sum_i_2 - sum_i**2
    a = (n*sum_ix - sum_i*sum_x) / den
    k = (sum_i_2*sum_x - sum_ix*sum_i) / den
    return {
        'a': f"{a:.4f}",
        'k': f"{k:.4f}"
    }

def exp_approx(x: list[int]):
    y = [math.log1p(xi) for xi in x]
    n = len(x)
    a11, a12, b1 = n, n*(n-1)/2, sum(y)
    a21, a22, b2 = n*(n-1)/2, n*(n-1)*(2*n-1)/6, sum(i*xi for i, xi in enumerate(y))
    A = np.array([[a11, a12], [a21, a22]])
    b = np.array([b1, b2])
    log_k, log_a = np.linalg.solve(A, b)
    return math.exp(log_k), math.exp(log_a)

@exam.task(
    Case(
        "2.4",
        files=("infections2.txt",),
        reader=read_official_files
    )
)
def task2_4(x: list[int]):
    n = len(x)
    book = defaultdict(list)
    for s in range(n-30):
        k, a = exp_approx(x[s:s+31])
        book[a].append((s,f"{a:.4f}",f"{k:.4f}"))

    max_a = max(book.keys())
    return book[max_a]
        

if __name__ == "__main__":
    exam.execute(output=True)