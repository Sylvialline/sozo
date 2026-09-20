from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import total_ordering
import math


@dataclass(frozen=True, slots=True, init=False)
class Q3:
    """
        a + b√3, where a and b are Fraction
    """
    a: Fraction
    b: Fraction

    def __init__(self, a: int | Fraction = 0, b: int | Fraction = 0):
        object.__setattr__(self, "a", Fraction(a))
        object.__setattr__(self, "b", Fraction(b))

    def __add__(self, other: Q3):
        return Q3(self.a + other.a, self.b + other.b)

    def __neg__(self):
        return Q3(-self.a, -self.b)

    def __sub__(self, other: Q3):
        return Q3(self.a - other.a, self.b - other.b)

    def __mul__(self, other: Q3):
        return Q3(
            self.a * other.a + 3 * self.b * other.b,
            self.a * other.b + self.b * other.a
        )

    def __truediv__(self, other: Q3):
        den = other.a * other.a - 3 * other.b * other.b
        return Q3(
            (self.a * other.a - 3 * self.b * other.b) / den,
            (- self.a * other.b + self.b * other.a) / den
        )

    def sign(self):
        if self.a == 0:
            return (self.b > 0) - (self.b < 0)
        if self.b == 0:
            return (self.a > 0) - (self.a < 0)
        if self.a > 0 and self.b > 0:
            return 1
        if self.a < 0 and self.b < 0:
            return -1

        aa = self.a * self.a
        bb3 = self.b * self.b * 3
        if self.a > 0:
            return (aa > bb3) - (aa < bb3)
        else:
            return (aa < bb3) - (aa > bb3)

    def __lt__(self, other: Q3):
        return (self - other).sign() < 0
    
    def __le__(self, other: Q3):
        return (self - other).sign() <= 0
    
    def __gt__(self, other: Q3):
        return (self - other).sign() > 0
    
    def __ge__(self, other: Q3):
        return (self - other).sign() >= 0

    def __floor__(self):
        if self.b == 0:
            return self.a.__floor__()
        d = math.lcm(self.a.denominator, self.b.denominator)
        a = self.a.numerator * (d // self.a.denominator)
        b = self.b.numerator * (d // self.b.denominator)
        t = math.isqrt(3*b*b)
        if b < 0:
            t = -t - 1
        return (a + t) // d

    def __ceil__(self):
        return -(-self).__floor__()

    def is_integer(self):
        return self.b == 0 and self.a.denominator == 1

SQRT3 = Q3(0, 1)