from collections import Counter
from itertools import combinations
from pathlib import Path
import string
import sys
from typing import Iterable

HERE, ROOT = Path(__file__).resolve().parents[:2]
sys.path.insert(0, str(ROOT))
DATA = HERE / "data"
OUTPUT = HERE / "output"
OUTPUT.mkdir(exist_ok=True)

from utils import Case, Exam, read_data

def parse_default(data: str) -> str | list[str]:
    s = data.strip().split('\n')
    # print(s)
    if len(s) == 1:
        s = s[0]
    return s

def parse_space(data: str) -> list[int]:
    return list(map(int, data.split()))

exam = Exam(reader=read_data, parser=parse_default)

@exam.task(
    Case("1", files=("data1.txt",))
)
def task1(data: str):
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits + '@#'
    bits = ''.join(f"{chars.index(ch):06b}" for ch in data) #note
    return bits[310:321]

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
        assert 0 <= d <= p < 256
        if d == 0:
            restored.append(0)
            continue
        assert p > 0
        n = len(restored)
        restored.extend(restored[n-p:n-p+d])
    return bytes(restored)

def compress(raw: bytes) -> bytes:
    n = len(raw)
    f: list[int] = [0] * (n+1) # f[-1] = 0
    g: list[tuple] = [None] * n
    for i in range(n):
        if raw[i] == 0:
            nf = f[i-1] + 3
            ng = (i-1, bytes([0, 0, 0]))
        else:
            nf = f[i-1] + 1
            ng = (i-1, bytes([raw[i]]))
        for d in range(1, 256):
            lim_l = max(i-d+1-255, 0)
            if d > i-d+1-lim_l:
                break
            bl = raw[lim_l : i-d+1]
            br = raw[i-d+1 : i+1]
            try:
                j = bl.index(br) + lim_l
            except ValueError:
                continue
            p = i - d - j + 1
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


@exam.task(
    Case("2a", "data2a.bin", "data2a.txt"),
    Case("2b", "data2b.bin", "data2b.tif"),
    Case("2c", "data2c.bin", "data2c.txt")
)
def task2(input: str, output: str):
    compressed = (DATA/input).read_bytes()
    restored = restore(compressed)
    (OUTPUT/output).write_bytes(restored)
    return {
        "size": len(restored),
        "file": output
    }

@exam.task(
    Case("3a", "data3a.txt", "data3a.bin"),
    Case("3b", "data3b.png", "data3b.bin"),
    Case("3c", "data3c.txt", "data3c.bin")
)
def task3(input: str, output: str):
    plain = (DATA/input).read_bytes()
    compressed = compress(plain)
    (OUTPUT/output).write_bytes(compressed)
    return {
        "size": len(compressed),
        "file": output
    }

class Map:
    def __init__(self, keys: str | list[str], values: str | list[str]):
        if(len(keys) != len(values)):
            raise ValueError
        self.d = dict.fromkeys(keys)
        self.used = dict.fromkeys(values, False)

    def inverse(self):
        return {v: k for k, v in self.d.items() if v is not None}

    def candidates(self):
        return [k for k, v in self.used.items() if v is False]

    def select_key(self, defined_chars: str = ''):
        max_count = 0
        key = None
        for k, v in self.d.items():
            if v is not None:
                continue
            undefined_count = sum(c not in defined_chars for c in k)
            if undefined_count > max_count:
                max_count = undefined_count
                key = k
        return key

    def choose(self, key, value):
        if self.d[key] is not None or self.used[value] is True:
            raise ValueError

        self.d[key] = value
        self.used[value] = True

    def undo(self, keys: Iterable[str]):
        for key in keys:
            value = self.d[key]
            if value is None or self.used[value] is False:
                raise ValueError

            self.d[key] = None
            self.used[value] = False

def dfs(m: Map, wordm: Map) -> bool:
    defined_chars = ''.join(k for k, v in m.d.items() if v is not None)
    key = wordm.select_key(defined_chars)
    if key is None:
        return True
    for value in wordm.candidates():
        if len(value) != len(key):
            continue
        modified = []
        for pchar, cchar in zip(key, value):
            if m.d[pchar] is not None:
                if m.d[pchar] == cchar:
                    continue
                else:
                    break

            if m.used[cchar] is True:
                break
            modified.append(pchar)
            m.choose(pchar, cchar)
        else:
            wordm.choose(key, value)
            if dfs(m, wordm) is True:
                return True
            wordm.undo([key])
        m.undo(modified)

    return False
    
def decrypt(m: Map, plain_words: list[str], cipher_words: list[str]) -> bool:
    if len(plain_words) != len(cipher_words):
        return False
    pc = Counter(map(len, plain_words))
    cc = Counter(map(len, cipher_words))
    if pc != cc:
        return False
    wordm = Map(plain_words, cipher_words)
    return dfs(m, wordm)
    

@exam.task(
    Case("4", files=("data4.txt", "data4dict.txt"))
)
def task4(text: str, dict_text: str):
    alphabet = string.ascii_lowercase + " ."
    m = Map(alphabet, alphabet)
    plain_words = dict_text.split(' ')
    plain_words = list(set(plain_words))
    for vs, vp in combinations(alphabet, 2):
        m.choose(' ', vs)
        m.choose('.', vp)
        trans = str.maketrans({vs: '#', vp: '#'})
        cipher_words = [x for x in text.translate(trans).split('#') if x]
        cipher_words = list(set(cipher_words))
        result = decrypt(m, plain_words, cipher_words)
        if result is True:
            break
        m.undo(' .')
    else:
        return None

    decrypted = text.translate(str.maketrans(m.inverse()))
    return decrypted


E = 551263368336670859257571
N = 3858843578360632069557337

def recover_d_by_relation(e: int, n: int) -> int:
    from math import isqrt

    for d in range(1, n // e + 1):
        total = n - e * d + 2
        delta = total * total - 4 * n
        if delta < 0:
            continue
        root = isqrt(delta)
        if root * root != delta:
            continue
        p = (total - root) // 2
        q = total - p
        if p * q == n and e * d == (p - 1) * (q - 1) + 1:
            return d
    raise ValueError("无法从 e*d=(p-1)*(q-1)+1 恢复 d")

def recover_d_by_factorization(e: int, n: int) -> int:
    from primefac import primefac

    p, q = sorted(primefac(n))
    d, remainder = divmod((p - 1) * (q - 1) + 1, e)
    if remainder:
        raise ValueError("分解结果不满足 e*d=(p-1)*(q-1)+1")
    return d

@exam.task(
    Case("5", files=("data5.txt",), parser=parse_space),
)
def task5(data: list[int]):
    # d = recover_d_by_relation(E, N) # d=7
    d = recover_d_by_factorization(E, N)
    decrypted = bytearray()
    for c in data:
        m = pow(c, d, N) #note
        decrypted.extend(m.to_bytes(4, "big")) #note
    return decrypted.decode()


if __name__ == "__main__":
    exam.execute(output=True)
