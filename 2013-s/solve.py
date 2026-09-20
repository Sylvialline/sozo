from __future__ import annotations
from enum import IntFlag, auto
from functools import partial
from fractions import Fraction
import math
from typing import SupportsIndex

from utils.exam import Exam, Batch, Rows

def A_d_R0(d: Fraction):
    """
        compute A(d, R0)
        where R0: 0 <= x,y <= 10
    """
    if d == 0:
        return 1
    d = abs(d)
    c = math.floor(10 / d) + 1
    return c * c

task1 = A_d_R0

def lp_circle_r(r: Fraction):
    """
        compute the number of lattice points in 
        (x-r)^2 + (y-r)^2 <= r^2
    """
    cnt = 0
    n, m = r.numerator, r.denominator
    for x in range(math.floor(2 * r) + 1):
        d = 2*n*m*x - x*x*m*m
        s = math.isqrt(d)
        # lo = math.ceil(Fraction(n - s, m))
        # hi = math.floor(Fraction(n + s, m))
        lo = -((s - n) // m)
        hi = (n + s) // m
        cnt += hi - lo + 1

    return cnt

# print(lp_circle_r(Fraction(5/0.0005)))

def A_d_R1(d: Fraction):
    if d == 0:
        return 0
    d = abs(d)
    return lp_circle_r(5 / d)

def task2(d: Fraction):
    return A_d_R1(d) / A_d_R0(d) / 4

sqrt_3 = math.sqrt(3)

def S_Kn(n: int, l: float = 10):
    s = l * l
    e = 3
    l /= 3
    a = l * l * e
    q = 4 / 9
    s += a * (1 - pow(q, n)) / (1 - q)
    s *= sqrt_3 / 4
    return s

task3 = partial(S_Kn, 2)
task4 = S_Kn

from Q3 import Q3, SQRT3

def lp_1d(lo: Q3, hi: Q3, inclusive=(True, True)):
    """Count integers between lo and hi."""
    l = math.ceil(lo) if inclusive[0] else math.floor(lo) + 1
    r = math.floor(hi) if inclusive[1] else math.ceil(hi) - 1
    c = r - l + 1
    # assert(c>=0)
    return c

HALF = Q3(Fraction(1, 2), 0)
THIRD = Q3(Fraction(1, 3), 0)
B6 = Q3(0, Fraction(1, 6))
C1 = Q3(0, Fraction(1, 9))
C2 = Q3(0, Fraction(2, 9))

class Side(IntFlag):
    D = auto() # down side
    R = auto() # right side
    L = auto() # left side
    ALL = D | R | L

def lp_triangle(x: Q3, y: Q3, l: Q3, including: Side):
    """
    Count lattice points in an equilateral triangle,
    centered at (x, y), with side length l.
    """
    left = x - HALF * l
    right =  x + HALF * l
    low = y - B6 * l
    cnt = 0

    lin = (Side.D in including, Side.L in including)
    rin = (Side.D in including, Side.R in including)

    for i in range(math.ceil(left), math.floor(right) + 1):
        qi = Q3(i, 0)
        lhigh = low + (qi - left) * SQRT3
        rhigh = low + (right - qi) * SQRT3
        cnt += min(lp_1d(low, lhigh, lin), lp_1d(low, rhigh, rin))
    return cnt

def lp_flake_n(
    n: int, x: Q3, y: Q3, l: Q3,
    including: Side,
    count_self: bool
) -> int:
    
    cnt = lp_triangle(x, y, l, including) if count_self else 0
    if n == 0:
        return cnt
    
    l0 = l * THIRD
    l1 = l * C1
    l2 = l * C2
    if Side.D in including:
        x0 = x
        y0 = y - l2
        cnt += lp_flake_n(n - 1, -x0, -y0, l0, ~Side.D, True)

    if Side.L in including:
        x0 = x - l0
        y0 = y + l1
        cnt += lp_flake_n(n - 1, -x0, -y0, l0, ~Side.L, True)
        
    if Side.R in including:
        x0 = x + l0
        y0 = y + l1
        cnt += lp_flake_n(n - 1, -x0, -y0, l0, ~Side.R, True)

    if (f := ~Side.D & including):
        x0 = x
        y0 = y + l2
        cnt += lp_flake_n(n - 1, x0, y0, l0, f, False)

    if (f := ~Side.L & including):
        x0 = x + l0
        y0 = y - l1
        cnt += lp_flake_n(n - 1, x0, y0, l0, f, False)

    if (f := ~Side.R & including):
        x0 = x - l0
        y0 = y - l1
        cnt += lp_flake_n(n - 1, x0, y0, l0, f, False)

    return cnt


def A_d_Kn(d: Fraction, n: int):
    if d == 0:
        return 1
    d = abs(d)
    scalar = Q3(d, 0)
    x = Q3(5, 0) / scalar
    y = Q3(0, Fraction(5, 3)) / scalar
    l = Q3(10, 0) / scalar
    return lp_flake_n(n, x, y, l, Side.ALL, True)

def task5(d: Fraction):
    return A_d_Kn(d, 2)

def task6(d: Fraction, n: int):
    return A_d_Kn(d, n)


exam = Exam(show_time=True)
exam.add(task1, Batch('1', "q1.txt", Rows(Fraction)))
exam.add(task2, Batch('2', "q2.txt", Rows(Fraction)))
exam.add(task3, Batch('3', "q3.txt", Rows()))
exam.add(task4, Batch('4', "q4.txt", Rows(int)))
exam.add(task5, Batch('5', "q5.txt", Rows(Fraction)))
exam.add(task6, Batch('6', "q6.txt", Rows(Fraction, int)))
# exam.add(task6, Case('6.1', Fraction('0.399035'), 4))
exam.execute(output=True, inline_simple_lists=False)