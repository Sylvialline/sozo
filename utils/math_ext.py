"""常用整数因数工具。"""

import math
from numbers import Integral


def _positive_int(n: int) -> int:
    if isinstance(n, bool) or not isinstance(n, Integral):
        raise TypeError("n 必须是整数")
    if n < 1:
        raise ValueError("n 必须是正整数")
    return int(n)


def factor_pairs(
    n: int,
    *,
    include_swapped: bool = False,
) -> list[tuple[int, int]]:
    """返回 n 的正因子对；可选包含交换后的因子对。"""
    n = _positive_int(n)
    pairs = [
        (d, n // d)
        for d in range(1, math.isqrt(n) + 1)
        if n % d == 0
    ]

    if include_swapped:
        pairs += [
            (b, a)
            for a, b in reversed(pairs)
            if a != b
        ]

    return pairs


def divisors(n: int) -> list[int]:
    """返回 n 的全部正因子，结果按升序排列。"""
    pairs = factor_pairs(n)
    return (
        [a for a, _ in pairs]
        + [
            b
            for a, b in reversed(pairs)
            if a != b
        ]
    )
