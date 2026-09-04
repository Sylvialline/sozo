from pathlib import Path
import sys

from utils.data_io import read_data
from utils.exam import Case, Exam
HERE, ROOT = Path(__file__).resolve().parents[:2]
DATA = HERE / "data"
OUTPUT = HERE / "output"

sys.path.insert(0, str(ROOT))

exam = Exam(read_data)

N = 1000
M = 6
K = 3

def compress_bruteforce(s: str):
    j = 1
    res = [s[0]]
    while j <= len(s) - M:
        tar = s[j:j+M]
        for i in range(0, j):
            ind = s[i:i+M]
            if ind == tar:
                res.append(f"{i:03}")
                j += M
                break
        else:
            res.append(s[j])
            j += 1
    res.append(s[j:])
    return ''.join(res)

def indication_dict(s: str):
    d = {}
    for i in range(len(s)-M+1):
        sub = s[i:i+M]
        if sub not in d:
            d[sub] = i
    return d

def compress_by_dict(s: str):
    d = indication_dict(s)
    j = 1
    res = [s[0]]
    while j <= len(s) - M:
        tar = s[j:j+M]
        if (i := d[tar]) < j:
            res.append(f"{i:03}")
            j += M
        else:
            res.append(s[j])
            j += 1
    res.append(s[j:])
    return ''.join(res)


def compress(s: str):
    a = compress_by_dict(s)
    # b = compress_bruteforce(s)
    # assert a == b
    return a

def indication_count(s: str):
    cmp = compress(s)
    return sum(c.isdigit() for c in cmp) // 3

def decompress(s: str):
    n = len(s)
    res = []
    j = 0
    while j < n:
        if s[j].isdigit():
            i = int(s[j:j+K])
            j += K
            for p in range(i, i+M):
                res.append(res[p])
        else:
            res.append(s[j])
            j += 1
    return ''.join(res)

def test():
    src1 = "vwabcdefxyabcdefst"
    comp1 = "vwabcdefxy002st"
    src2 = "abababababababab"
    comp2 = "ab000000ab"
    assert compress(src1) == comp1, compress(src1)
    assert compress(src2) == comp2, compress(src2)
    assert decompress(comp1) == src1, decompress(comp1)
    assert decompress(comp2) == src2, decompress(comp2)

@exam.task(
    Case('q1')
)
def task1():
    return {
        '1.1': decompress("aabbba000c001008a"),
        '1.2': compress("aabbccddaabbccddbbccddaa")
    }

@exam.task(
    Case('q2.1', files=("c1.txt",)),
    Case('q2.2', files=("c2.txt",))
)
def task2(input: str):
    return indication_count(input)

@exam.task(
    Case('q3', files=("s1.txt",)),
)
def task3(input: str):
    d = indication_dict(input)
    return len(d)

@exam.task(
    Case('q4.1', files=("s1.txt",)),
    Case('q4.2', files=("s2.txt",)),
)
def task4(input: str):
    cmp = compress(input)
    return {
        "length": len(cmp),
        "last 10": cmp[-10:]
    }

@exam.task(
    Case('q5.1', files=("c1.txt",)),
    Case('q5.2', files=("c2.txt",)),
)
def task5(input: str):
    src = decompress(input)
    return {
        "length": len(src),
        "last 10": src[-10:]
    }

def blocked_compress(s: str):
    return ''.join(
        compress(s[i:i+N]) for i in range(0, len(s), N)
    )

def blocked_decompress(s: str):
    n = len(s)
    block = []
    res = []
    j = 0
    while j < n:
        if s[j].isdigit():
            i = int(s[j:j+K])
            j += K
            for p in range(i, i + M):
                block.append(block[p])
        else:
            block.append(s[j])
            j += 1
        if len(block) >= N:
            assert len(block) == N
            res.append(''.join(block))
            block.clear()
    res.append(''.join(block))
    return ''.join(res)

@exam.task(
    Case('q6', files=("s3.txt",))
)
def task6(input: str):
    cmp = blocked_compress(input)
    de = blocked_decompress(cmp)
    return {
        "source": input,
        "compressed": cmp,
        "decomp": de,
        "source == decomp": input == de
    }

test()
exam.execute(output=True)