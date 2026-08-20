from collections import Counter, deque
from copy import copy
from pathlib import Path
import math
import sys
from typing import Any, Iterable, NamedTuple


HERE, ROOT = Path(__file__).resolve().parents[:2]
sys.path.insert(0, str(ROOT))
DATA = HERE / "data"
OUTPUT = HERE / "output"
OUTPUT.mkdir(exist_ok=True)

from utils import Case, Exam, read_data

try:
    from itertools import batched
except ImportError:
    from utils.itertools_ext import batched

DEBUG = True
if DEBUG:
    log_file = Path("test.log").open("w", encoding="utf-8")
def logit(*s):
    if DEBUG:
        print(*s, file=log_file, flush=True)


def parse_space(data: str) -> list[int]:
    return list(map(int, data.split()))

Pixel = tuple[int, int, int]

WHITE = (255, 255, 255)

def parse_rgb(data: str) -> list[Pixel]:
    a = parse_space(data)
    return list(batched(a, 3)) # type: ignore

def factor_pairs(n: int):
    for i in range(1, math.isqrt(n) + 1):
        if n % i == 0:
            yield i, n // i

def factor_pairs_full(n: int):
    pairs = list(factor_pairs(n))
    if pairs[-1][0] == pairs[-1][1]:
        other = pairs[-2::-1]
    else:
        other = pairs[::-1]
    pairs.extend((b, a) for a, b in other)
    return pairs

exam = Exam(reader=read_data, parser=parse_rgb)

class IndexedPixel(NamedTuple):
    idx: int
    pixel: Pixel
    
class RGBImage:
    indexed_pixels: list[IndexedPixel]

    def __init__(self, pixels: list[Pixel]) -> None:
        self.pixels = pixels
        self._make_index()
        self.tot = len(pixels)
        self.n, self.m = self._compute_n_m()

    def _compute_n_m(self):
        p = self.tot
        for m, n in factor_pairs_full(p):
            if all(self.pixels[i*m-1] == WHITE for i in range(1, n+1)):
                return n, m
            
        raise ValueError

    def _make_index(self):
        self.indexed_pixels = [IndexedPixel._make(x) for x in enumerate(self.pixels)]

    def sort_with_index(self):
        def key(x):
            brightness = x[1][0]**2 + x[1][1]**2 + x[1][2]**2
            return brightness, -x[0]

        a = sorted(self.indexed_pixels, key=key)
        return a

    def pick_k(self, k: int):
        s = self.sort_with_index()
        n = self.tot
        return [s[n*i//k] for i in range(k)]
    
    def make_clusters(self, p: list[IndexedPixel]):
        #fixed: 没有确保 p_i 一定属于 C_i
        clusters: dict[IndexedPixel, list[IndexedPixel]] = {k:[k] for k in p}
        # memory: dict[Pixel, IndexedPixel] = {}
        cs = sorted(p, key=lambda x: -x.idx)
        print('#in')
        for ip in self.indexed_pixels:
            if ip in clusters:
                continue
            #optimized: 相同的颜色归属于相同的聚类；复杂度 unique count * k
            # if (x := memory.get(ip.pixel)) is not None:
            #     clusters[x].append(ip)
            #     continue
            r, g, b = ip.pixel
            best_p = cs[0]; pr, pg, pb = best_p.pixel
            best_d = abs(pr-r) + abs(pg-g) + abs(pb-b)
            #optimized: min(,key=) 慢，手写比较
            for px in cs[1:]:
                pr, pg, pb = px.pixel
                #optimized: hot loop 不使用自定义 python function dist
                d = abs(pr-r) + abs(pg-g) + abs(pb-b)
                if d < best_d:
                    best_p = px
                    best_d = d
            clusters[best_p].append(ip)
            # memory[ip.pixel] = best_p
        print('#out')
        return clusters

    def make_clusters_bfs(self, p: list[IndexedPixel]):
        SIZE = 1 << 24
        def id(px: Pixel):
            return px[0] | px[1]<<8 | px[2]<<16
        clusters: dict[IndexedPixel, list[IndexedPixel]] = {k:[k] for k in p}
        #fixed: 不要修改外部可变对象的值
        p = sorted(p, key=lambda x: -x.idx)
        pixels = [x.pixel for x in p]
        q = deque(pixels)
        dis: list[Any] = [None] * SIZE
        for x in p:
            #fixed: pixel 相同，idx 不同，保留 idx 更大的
            if dis[id(x.pixel)] is None:
                dis[id(x.pixel)] = (0, x)
        print("in")
        while q:
            u = q.popleft()
            d, f = dis[id(u)]
            for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
                v = (u[0]+dx, u[1]+dy, u[2]+dz)
                if not (0 <= v[0] < 256 and 0 <= v[1] < 256 and 0 <= v[2] < 256):
                    continue
                i = id(v)
                if dis[i] is not None:
                    continue
                dis[i] = (d+1, f)
                q.append(v)
        print("out")

        for ip in self.indexed_pixels:
            if ip in clusters:
                continue
            nearest_p = dis[id(ip.pixel)][1]
            clusters[nearest_p].append(ip)
        return clusters


    T_LIM = 10

    def k_clusters(self, k: int, t_lim: int = T_LIM):
        p = self.pick_k(k)
        logit(0, p)
        for t in range(t_lim):
            clusters = self.make_clusters(p)
            # clusters = self.make_clusters_bfs(p)
            next_p = []
            for key, cs in clusters.items():
                c = center([x.pixel for x in cs])
                nearest = min(cs, key=lambda x: (dist(x.pixel, c), -x.idx))
                next_p.append(nearest)
            p = next_p
            logit(t+1, p)
        return p

    def compress(self, k: int):
        p_t = self.k_clusters(k)
        clusters_t = self.make_clusters(p_t)
        for key, cs in clusters_t.items():
            for idx, pixel in cs:
                self.pixels[idx] = key.pixel
        self._make_index()

    TIF_HEADER = (77, 77, 0, 42, 0, 0, 0, 8, 0, 7, 1, 0, 0, 4, 0, 0,
                  0, 1, -1, -1, -1, -1, 1, 1, 0, 4, 0, 0, 0, 1, -1, -1,
                  -1, -1, 1, 2, 0, 3, 0, 0, 0, 3, 0, 0, 0, 98, 1, 6,
                  0, 3, 0, 0, 0, 1, 0, 2, 0, 0, 1, 17, 0, 4, 0, 0,
                  0, 1, 0, 0, 0, 104, 1, 21, 0, 3, 0, 0, 0, 1, 0, 3,
                  0, 0, 1, 23, 0, 4, 0, 0, 0, 1, -1, -1, -1, -1, 0, 0,
                  0, 0, 0, 8, 0, 8, 0, 8)

    def to_tif(self) -> bytes:
        w = self.m.to_bytes(4, "big")
        h = self.n.to_bytes(4, "big")
        s = (self.m*self.n*3).to_bytes(4, "big")
        tif: list[int] = list(self.TIF_HEADER)
        tif[18: 18+4] = list(w)
        tif[30: 30+4] = list(h)
        tif[90: 90+4] = list(s)
        for pixel in self.pixels:
            tif.extend(pixel)
        return bytes(tif)


@exam.task(
    Case("1~3", files=("image1.txt",)),
)
def task1_3(pixels: list[Pixel]):
    img = RGBImage(pixels)
    assert img.tot % 2 == 0
    s = img.sort_with_index()
    idx, p = s[img.tot // 2]
    return {
        'total_count': img.tot,
        'n, m': (img.n, img.m),
        'idx, median': (idx, p)
    }

@exam.task(
    Case("4", 4, files=("image2.txt",)),
)
def task4(k: int, pixels: list[Pixel]):
    img = RGBImage(pixels)
    assert img.tot % k == 0
    return img.pick_k(k)

def dist(px: Pixel, py: Pixel):
    return abs(px[0]-py[0]) + abs(px[1]-py[1]) + abs(px[2]-py[2])

def center(pixels: list[Pixel]):
    n = len(pixels)
    r, g, b = 0, 0, 0
    for x in pixels:
        r += x[0]
        g += x[1]
        b += x[2]
    return r//n, g//n, b//n

@exam.task(
    Case("5.1", 128, (40, 80, 120), files=("image2.txt",)),
    # Case("5.2", 8, (2, 4, 6), files=("image3.txt",)),
    # Case("5.t", 8, (2, 4, 6), files=("image1.txt",)),
)
def task5(k: int, arr_i: tuple[int], pixels: list[Pixel]):
    img = RGBImage(pixels)
    p = img.k_clusters(k)
    return [p[i] for i in arr_i]

@exam.task(
    Case("6", 32, "image.tif", files=("image2.txt",))
)
def task6(k: int, output_name: str, pixels: list[Pixel]):
    img = RGBImage(pixels)
    tif_bytes = img.to_tif()
    (OUTPUT/"original.tif").write_bytes(tif_bytes)
    logit(img.pixels)
    img.compress(k)
    logit(img.pixels)
    tif_bytes = img.to_tif()
    (OUTPUT/output_name).write_bytes(tif_bytes)
    return {
        "byte_count": len(tif_bytes),
        "output_file": output_name
    }

# @exam.task(
#     Case("test1", files=("image1.txt",)),
#     Case("test2", files=("image2.txt",)),
#     Case("test3", files=("image3.txt",))
# )
def testtask(pixels: list[Pixel]):
    img = RGBImage(pixels)

    print(len(set(pixels)), len(pixels))
    print(img.n, img.m)

if __name__ == "__main__":
    exam.execute(output=True, only=task5)
