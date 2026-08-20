from pathlib import Path
import math
import sys
from typing import NamedTuple

import numpy as np
from numpy.typing import NDArray


HERE, ROOT = Path(__file__).resolve().parents[:2]
sys.path.insert(0, str(ROOT))

OUTPUT = HERE / "output"
OUTPUT.mkdir(exist_ok=True)

from utils import Case, Exam, read_data


# ============================================================
# Types / parsing
# ============================================================

PixelArray = NDArray[np.uint8]
IndexArray = NDArray[np.int64]


class IndexedPixel(NamedTuple):
    idx: int
    pixel: tuple[int, int, int]


def parse_rgb(data: str) -> PixelArray:
    a = np.fromstring(data, sep=" ", dtype=np.uint8)
    if a.size % 3 != 0:
        raise ValueError("RGB data length must be divisible by 3")
    return a.reshape(-1, 3)


exam = Exam(reader=read_data, parser=parse_rgb)


# ============================================================
# Utilities
# ============================================================

WHITE = np.array((255, 255, 255), dtype=np.uint8)


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


# ============================================================
# RGB image
# ============================================================

class RGBImage:
    T_LIM = 10
    BLOCK_SIZE = 32768

    TIF_HEADER = (
        77, 77, 0, 42, 0, 0, 0, 8, 0, 7, 1, 0, 0, 4, 0, 0,
        0, 1, -1, -1, -1, -1, 1, 1, 0, 4, 0, 0, 0, 1, -1, -1,
        -1, -1, 1, 2, 0, 3, 0, 0, 0, 3, 0, 0, 0, 98, 1, 6,
        0, 3, 0, 0, 0, 1, 0, 2, 0, 0, 1, 17, 0, 4, 0, 0,
        0, 1, 0, 0, 0, 104, 1, 21, 0, 3, 0, 0, 0, 1, 0, 3,
        0, 0, 1, 23, 0, 4, 0, 0, 0, 1, -1, -1, -1, -1, 0, 0,
        0, 0, 0, 8, 0, 8, 0, 8,
    )

    def __init__(self, pixels: PixelArray):
        self.pixels = pixels
        self.rgb16 = pixels.astype(np.int16)

        self.tot = len(pixels)
        self.n, self.m = self._compute_n_m()

    # --------------------------------------------------------
    # Image dimensions
    # --------------------------------------------------------

    def _compute_n_m(self) -> tuple[int, int]:
        for m, n in factor_pairs_full(self.tot):
            # Original condition:
            #
            # pixels[i*m - 1] == WHITE
            #
            # for every row i.
            if np.all(self.pixels[m - 1::m] == WHITE):
                return n, m

        raise ValueError("Cannot determine image dimensions")

    # --------------------------------------------------------
    # Initial representatives
    # --------------------------------------------------------

    def pick_k(self, k: int) -> IndexArray:
        """
        Equivalent to sorting IndexedPixel by

            (brightness, -idx)

        and taking positions n*i//k.
        """

        x = self.pixels.astype(np.uint32)

        brightness = (
            x[:, 0] * x[:, 0]
            + x[:, 1] * x[:, 1]
            + x[:, 2] * x[:, 2]
        )

        idx = np.arange(self.tot, dtype=np.int64)

        # np.lexsort:
        # last key is primary.
        #
        # brightness ascending,
        # idx descending.
        order = np.lexsort((-idx, brightness))

        positions = (
            np.arange(k, dtype=np.int64)
            * self.tot
            // k
        )

        return order[positions]

    # --------------------------------------------------------
    # Cluster assignment
    # --------------------------------------------------------

    def assign_clusters(
        self,
        p: IndexArray,
        block_size: int = BLOCK_SIZE,
    ) -> NDArray[np.int32]:
        """
        owner[i] = j means pixel i belongs to cluster j.

        Distance:
            Manhattan / L1 distance.

        Tie breaking:
            larger representative pixel index wins.

        Additionally:
            representative p[j] is forcibly assigned to cluster j,
            matching the original make_clusters() semantics.
        """

        n = self.tot
        k = len(p)

        # np.argmin returns the FIRST minimum.
        #
        # Therefore put representatives with larger idx first,
        # reproducing:
        #
        #     min(..., key=(distance, -idx))
        #
        tie_order = np.argsort(-p)

        # centers[s] corresponds to cluster tie_order[s].
        centers = self.rgb16[p[tie_order]]

        owner = np.empty(n, dtype=np.int32)

        for left in range(0, n, block_size):
            right = min(left + block_size, n)

            x = self.rgb16[left:right]
            b = right - left

            # Max Manhattan RGB distance = 3 * 255 = 765,
            # so int16 is sufficient.
            d = np.empty((b, k), dtype=np.int16)
            tmp = np.empty((b, k), dtype=np.int16)

            # R
            np.subtract(
                x[:, None, 0],
                centers[None, :, 0],
                out=d,
            )
            np.abs(d, out=d)

            # G
            np.subtract(
                x[:, None, 1],
                centers[None, :, 1],
                out=tmp,
            )
            np.abs(tmp, out=tmp)
            d += tmp

            # B
            np.subtract(
                x[:, None, 2],
                centers[None, :, 2],
                out=tmp,
            )
            np.abs(tmp, out=tmp)
            d += tmp

            nearest_in_sorted_order = np.argmin(d, axis=1)

            owner[left:right] = (
                tie_order[nearest_in_sorted_order]
            )

        # Important:
        # each representative must belong to its own cluster.
        owner[p] = np.arange(k, dtype=np.int32)

        return owner

    # --------------------------------------------------------
    # Mean center of each cluster
    # --------------------------------------------------------

    def cluster_centers(
        self,
        owner: NDArray[np.int32],
        k: int,
    ) -> NDArray[np.int16]:

        count = np.bincount(owner, minlength=k)

        sum_r = np.bincount(
            owner,
            weights=self.pixels[:, 0],
            minlength=k,
        )
        sum_g = np.bincount(
            owner,
            weights=self.pixels[:, 1],
            minlength=k,
        )
        sum_b = np.bincount(
            owner,
            weights=self.pixels[:, 2],
            minlength=k,
        )

        centers = np.column_stack((
            sum_r // count,
            sum_g // count,
            sum_b // count,
        ))

        return centers.astype(np.int16)

    # --------------------------------------------------------
    # Representative nearest to mean center
    # --------------------------------------------------------

    def choose_representatives(
        self,
        owner: NDArray[np.int32],
        centers: NDArray[np.int16],
    ) -> IndexArray:
        """
        For every cluster, choose

            min(pixel, key=(distance_to_center, -idx))

        exactly as in the original implementation.
        """

        n = self.tot
        k = len(centers)

        # Center corresponding to every pixel.
        c = centers[owner]

        d = (
            np.abs(self.rgb16[:, 0] - c[:, 0])
            + np.abs(self.rgb16[:, 1] - c[:, 1])
            + np.abs(self.rgb16[:, 2] - c[:, 2])
        ).astype(np.int64)

        idx = np.arange(n, dtype=np.int64)

        # Encode lexicographic key:
        #
        #     (distance, -idx)
        #
        # into one non-negative integer.
        #
        # Smaller distance wins.
        # For equal distance, larger idx wins.
        score = d * n + (n - 1 - idx)

        best_score = np.full(
            k,
            np.iinfo(np.int64).max,
            dtype=np.int64,
        )

        np.minimum.at(
            best_score,
            owner,
            score,
        )

        best_idx = n - 1 - best_score % n

        return best_idx.astype(np.int64)

    # --------------------------------------------------------
    # Lloyd iteration
    # --------------------------------------------------------

    def k_clusters(
        self,
        k: int,
        t_lim: int = T_LIM,
    ) -> IndexArray:

        p = self.pick_k(k)

        for _ in range(t_lim):
            owner = self.assign_clusters(p)

            centers = self.cluster_centers(
                owner,
                k,
            )

            next_p = self.choose_representatives(
                owner,
                centers,
            )

            # Exact fixed point:
            # all later iterations would be identical.
            if np.array_equal(next_p, p):
                break

            p = next_p

        return p

    # --------------------------------------------------------
    # Compression
    # --------------------------------------------------------

    def compress(self, k: int) -> IndexArray:
        p = self.k_clusters(k)

        # Original code performs one final make_clusters(p_t)
        # after the iterations.
        owner = self.assign_clusters(p)

        # representative color of each cluster
        colors = self.pixels[p]

        # Replace every pixel with its representative.
        self.pixels[:] = colors[owner]

        # Keep the int16 view consistent if the object is reused.
        self.rgb16 = self.pixels.astype(np.int16)

        return p

    # --------------------------------------------------------
    # Output helpers
    # --------------------------------------------------------

    def indexed_pixel(self, idx: int) -> IndexedPixel:
        r, g, b = self.pixels[idx]

        return IndexedPixel(
            idx,
            (int(r), int(g), int(b)),
        )

    def to_tif(self) -> bytes:
        header = bytearray(
            x & 0xFF
            for x in self.TIF_HEADER
        )

        header[18:22] = self.m.to_bytes(4, "big")
        header[30:34] = self.n.to_bytes(4, "big")

        size = self.m * self.n * 3
        header[90:94] = size.to_bytes(4, "big")

        # pixels is C-contiguous (N, 3), so this produces
        # RGBRGBRGB... directly without a Python loop.
        return bytes(header) + self.pixels.tobytes()


# ============================================================
# Task 5
# ============================================================

@exam.task(
    Case(
        "5.1",
        128,
        (40, 80, 120),
        files=("image2.txt",),
    ),
    Case(
        "5.2",
        8,
        (2, 4, 6),
        files=("image3.txt",),
    ),
)
def task5(
    k: int,
    arr_i: tuple[int, ...],
    pixels: PixelArray,
):
    img = RGBImage(pixels)

    p = img.k_clusters(k)

    return [
        img.indexed_pixel(int(p[i]))
        for i in arr_i
    ]


# ============================================================
# Task 6
# ============================================================

@exam.task(
    Case(
        "6",
        32,
        "image.tif",
        files=("image2.txt",),
    ),
)
def task6(
    k: int,
    output_name: str,
    pixels: PixelArray,
):
    img = RGBImage(pixels)

    original = img.to_tif()
    (OUTPUT / "original.tif").write_bytes(original)

    img.compress(k)

    compressed = img.to_tif()
    (OUTPUT / output_name).write_bytes(compressed)

    return {
        "byte_count": len(compressed),
        "output_file": output_name,
    }


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    exam.execute(
        output=True,
        only=task5,
        # only=task6,
    )