"""二次实数域 a + b√n 的精确运算；用 partial(Qn, n) 固定根号参数。"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import total_ordering
from math import isqrt, lcm
from operator import index


def _fraction(value) -> Fraction:
    if not isinstance(value, (int, Fraction, str)):
        raise TypeError("coefficients must be int, Fraction or rational strings")
    return Fraction(value)


@total_ordering
@dataclass(frozen=True, slots=True, eq=False)
class Qn:
    """表示 a + b√n，n 为正的非完全平方整数，a、b 存为 Fraction。

    用 Qn(3, a, b) 构造；可用 partial(Qn, 3) 得到固定参数的 Q3 构造器。
    系数接受 int、Fraction、分数或十进制字符串，不隐式接收 float。
    支持精确四则运算、比较、abs、bool、hash 和 math.floor/ceil。
    int、Fraction 及 b=0 的 Qn 可混算；不同 n 的两个非有理数不混算或比较，
    也不自动化简根号中的平方因子。对象不可变，支持 deepcopy 和 pickle。
    """

    n: int
    a: Fraction = Fraction(0)
    b: Fraction = Fraction(0)

    def __post_init__(self):
        if isinstance(self.n, bool):
            raise TypeError("n must be an integer")
        n = index(self.n)
        if n <= 0 or isqrt(n) ** 2 == n:
            raise ValueError("n must be positive and not a perfect square")
        object.__setattr__(self, "n", n)
        object.__setattr__(self, "a", _fraction(self.a))
        object.__setattr__(self, "b", _fraction(self.b))

    def _pair(self, other):
        if isinstance(other, (int, Fraction)):
            other = Qn(self.n, other)
        if not isinstance(other, Qn):
            return NotImplemented
        if self.n == other.n:
            return self, other
        if not self.b:
            return Qn(other.n, self.a), other
        if not other.b:
            return self, Qn(self.n, other.a)
        raise TypeError("cannot mix irrational Qn values with different n")

    def __add__(self, other):
        pair = self._pair(other)
        if pair is NotImplemented:
            return NotImplemented
        x, y = pair
        return Qn(x.n, x.a + y.a, x.b + y.b)

    __radd__ = __add__

    def __neg__(self):
        return Qn(self.n, -self.a, -self.b)

    def __sub__(self, other):
        pair = self._pair(other)
        if pair is NotImplemented:
            return NotImplemented
        x, y = pair
        return Qn(x.n, x.a - y.a, x.b - y.b)

    def __rsub__(self, other):
        pair = self._pair(other)
        if pair is NotImplemented:
            return NotImplemented
        x, y = pair
        return y - x

    def __mul__(self, other):
        pair = self._pair(other)
        if pair is NotImplemented:
            return NotImplemented
        x, y = pair
        return Qn(x.n, x.a * y.a + x.n * x.b * y.b, x.a * y.b + x.b * y.a)

    __rmul__ = __mul__

    def __truediv__(self, other):
        pair = self._pair(other)
        if pair is NotImplemented:
            return NotImplemented
        x, y = pair
        denominator = y.a * y.a - x.n * y.b * y.b
        if not denominator:
            raise ZeroDivisionError("division by zero")
        return Qn(
            x.n,
            (x.a * y.a - x.n * x.b * y.b) / denominator,
            (x.b * y.a - x.a * y.b) / denominator,
        )

    def __rtruediv__(self, other):
        pair = self._pair(other)
        if pair is NotImplemented:
            return NotImplemented
        x, y = pair
        return y / x

    def sign(self) -> int:
        """精确返回符号 -1、0 或 1，不计算浮点平方根。"""
        sa = (self.a > 0) - (self.a < 0)
        sb = (self.b > 0) - (self.b < 0)
        if not sa:
            return sb
        if not sb or sa == sb:
            return sa
        delta = self.a * self.a - self.n * self.b * self.b
        return sa * ((delta > 0) - (delta < 0))

    def __eq__(self, other):
        pair = self._pair(other)
        if pair is NotImplemented:
            return NotImplemented
        x, y = pair
        return x.a == y.a and x.b == y.b

    def __lt__(self, other):
        pair = self._pair(other)
        if pair is NotImplemented:
            return NotImplemented
        x, y = pair
        return (x - y).sign() < 0

    def __hash__(self):
        return hash(self.a) if not self.b else hash((self.n, self.a, self.b))

    def __bool__(self):
        return bool(self.a or self.b)

    def __abs__(self):
        return -self if self.sign() < 0 else self

    def __floor__(self):
        if not self.b:
            return self.a.numerator // self.a.denominator
        denominator = lcm(self.a.denominator, self.b.denominator)
        a = self.a.numerator * (denominator // self.a.denominator)
        b = self.b.numerator * (denominator // self.b.denominator)
        root = isqrt(self.n * b * b)
        if b < 0:
            root = -root - 1
        return (a + root) // denominator

    def __ceil__(self):
        return -(-self).__floor__()

    def is_integer(self) -> bool:
        """判断是否恰为整数；非零有理数倍的 √n 不会成为有理数。"""
        return not self.b and self.a.denominator == 1
