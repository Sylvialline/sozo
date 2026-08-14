from collections import defaultdict, deque
from dataclasses import dataclass
from functools import partial
from itertools import batched, chain, product, combinations
from pathlib import Path
import string
import sys
import math, numpy as np
from typing import NamedTuple
from scipy.signal import convolve

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
sys.path.insert(0, str(ROOT))

log_file = Path("test.log").open("w", encoding="utf-8")
def debug(s):
    print(s, file=log_file)

from utils import Case, Exam, read_data, read_files
from utils import Graph

def parse_space(data: str) -> list[int]:
    return list(map(int, data.split()))

exam = Exam(reader=read_data, parser=parse_space)

# @exam.task(
#     Case("1", files=("data1.txt",))
# )
def task1(data):
    bits = []
    chars = ''.join((
        string.ascii_uppercase,
        string.ascii_lowercase,
        string.digits,
        '@#'
    ))
    for ch in data:
        num = chars.index(ch)
        for i in range(5, -1, -1):
            bits.append(num >> i & 1)
    return ''.join(str(i) for i in bits[310:321])

def restore(compressed: bytes) -> bytes:
    restored = bytearray()
    it = iter(compressed)
    while True:
        try:
            b = next(it)
        except StopIteration:
            break

        if b != 0:
            restored.append(b)
            continue
        p, d = next(it), next(it)
        assert 0 <= d <= p < 256 and 0 < p
        if d == 0:
            restored.append(0)
            continue
        n = len(restored)
        restored.extend(restored[n-p:n-p+d])
    return bytes(restored)

def compress(raw: bytes) -> bytes:
    b = list(raw)
    n = len(b)
    f: list[int] = [0] * (n+1) # f[-1] = 0
    g: list[tuple] = [None] * n
    for i in range(n):
        if b[i] == 0:
            nf = f[i-1] + 3
            ng = (i-1, bytes([0, 0, 0]))
        else:
            nf = f[i-1] + 1
            ng = (i-1, bytes([b[i]]))
        for d in range(1, 256):
            if d > i-d+1:
                break
            bl = b[0 : i-d+1]
            br = b[i-d+1 : i+1]
            try:
                j = bl.index(br)
            except ValueError:
                continue
            p = (i-d) - (j+d-1) + 1
            if f[i-d] + 3 < nf:
                nf = f[i-d] + 3
                ng = (i-d, bytes([0, p, d]))
        f[i] = nf
        g[i] = ng

    bs = []
    cur = n - 1
    while cur >= 0:
        bs.append(g[cur][1])
        cur = g[cur][0]
    return b''.join(reversed(bs))


# @exam.task(
#     Case("2a", "data2a.bin", "data2a.txt"),
#     Case("2b", "data2b.bin", "data2b.tif"),
#     Case("2c", "data2c.bin", "data2c.txt")
# )
def task2(input: str, output: str):
    compressed = (DATA/input).read_bytes()
    restored = restore(compressed)
    (DATA/output).write_bytes(restored)
    return {
        "size": len(restored),
        "file": output
    }

# @exam.task(
#     Case("3a", "data3a.txt", "data3a.bin"),
#     Case("3b", "data3b.png", "data3b.bin"),
#     Case("3c", "data3c.txt", "data3c.bin")
# )
def task3(input: str, output: str):
    raw = (DATA/input).read_bytes()
    compressed = compress(raw)
    (DATA/output).write_bytes(compressed)
    return {
        "size": len(compressed),
        "file": output
    }

# @exam.task(
#     Case("4", files=("data4.txt", "data4dict.txt")),
# )
# def task4(text: str, dict_text: str):
#     pass

E = 551263368336670859257571
N = 3858843578360632069557337
D = 7

@exam.task(
    Case("5", files=("data5.txt",)),
)
def task5(data: list[int]):
    decrypted = bytearray()
    for c in data:
        m = c ** D % N
        decrypted.append(m >> 24 & 255)
        decrypted.append(m >> 16 & 255)
        decrypted.append(m >> 8 & 255)
        decrypted.append(m & 255)
    print(decrypted)
    return decrypted.decode()


if __name__ == "__main__":
    # print(task2("test2.bin", "test2.out"))
    # print(restore(b"\x41\x42\x43\x44\x45\x46\x47\x00\x06\x05\x48"))
    exam.execute(output=True)