#!/usr/bin/env python3
"""Exact arithmetic and lattice-point algorithms for the Koch snowflake task."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal, ROUND_FLOOR, localcontext
from fractions import Fraction
from functools import lru_cache, total_ordering
from math import isqrt


@total_ordering
@dataclass(frozen=True)
class Qsqrt3:
    """The exact algebraic number a + b*sqrt(3), with rational a and b."""

    a: Fraction = Fraction(0)
    b: Fraction = Fraction(0)

    @staticmethod
    def coerce(value: object) -> "Qsqrt3":
        if isinstance(value, Qsqrt3):
            return value
        return Qsqrt3(Fraction(value))

    def __add__(self, other: object) -> "Qsqrt3":
        rhs = self.coerce(other)
        return Qsqrt3(self.a + rhs.a, self.b + rhs.b)

    __radd__ = __add__

    def __neg__(self) -> "Qsqrt3":
        return Qsqrt3(-self.a, -self.b)

    def __sub__(self, other: object) -> "Qsqrt3":
        return self + (-self.coerce(other))

    def __rsub__(self, other: object) -> "Qsqrt3":
        return self.coerce(other) - self

    def __mul__(self, other: object) -> "Qsqrt3":
        rhs = self.coerce(other)
        return Qsqrt3(
            self.a * rhs.a + 3 * self.b * rhs.b,
            self.a * rhs.b + self.b * rhs.a,
        )

    __rmul__ = __mul__

    def __truediv__(self, other: object) -> "Qsqrt3":
        rhs = self.coerce(other)
        denominator = rhs.a * rhs.a - 3 * rhs.b * rhs.b
        if denominator == 0:
            raise ZeroDivisionError
        return Qsqrt3(
            (self.a * rhs.a - 3 * self.b * rhs.b) / denominator,
            (self.b * rhs.a - self.a * rhs.b) / denominator,
        )

    def sign(self) -> int:
        a, b = self.a, self.b
        if a == 0:
            return (b > 0) - (b < 0)
        if b == 0 or (a > 0) == (b > 0):
            return (a > 0) - (a < 0)
        left = a * a
        right = 3 * b * b
        if left == right:
            raise AssertionError("sqrt(3) would be rational")
        if a > 0:
            return 1 if left > right else -1
        return 1 if right > left else -1

    def __eq__(self, other: object) -> bool:
        try:
            rhs = self.coerce(other)
        except (TypeError, ValueError):
            return False
        return self.a == rhs.a and self.b == rhs.b

    def __lt__(self, other: object) -> bool:
        return (self - self.coerce(other)).sign() < 0

    def decimal(self, precision: int = 100) -> Decimal:
        with localcontext() as ctx:
            ctx.prec = precision
            da = Decimal(self.a.numerator) / Decimal(self.a.denominator)
            db = Decimal(self.b.numerator) / Decimal(self.b.denominator)
            return +(da + db * _sqrt3(precision))


Point = tuple[Fraction, Fraction]  # (x, y/sqrt(3))
Edge = tuple[Point, Point]


def parse_decimal_exact(token: str) -> Fraction:
    """Parse a decimal token exactly, never through binary float."""
    numerator, denominator = Decimal(token).as_integer_ratio()
    return Fraction(numerator, denominator)


def floor_qsqrt3(value: Qsqrt3) -> int:
    approximate = int(value.decimal(120).to_integral_value(rounding=ROUND_FLOOR))
    while Qsqrt3(Fraction(approximate + 1)) <= value:
        approximate += 1
    while Qsqrt3(Fraction(approximate)) > value:
        approximate -= 1
    return approximate


def ceil_qsqrt3(value: Qsqrt3) -> int:
    return -floor_qsqrt3(-value)


def rotate_clockwise_60(vector: Point) -> Point:
    dx, dy = vector
    return (dx / 2 + 3 * dy / 2, -dx / 2 + dy / 2)


@lru_cache(maxsize=None)
def koch_vertices(n: int) -> tuple[Point, ...]:
    if n < 0:
        raise ValueError("n must be nonnegative")
    vertices: list[Point] = [
        (Fraction(0), Fraction(0)),
        (Fraction(10), Fraction(0)),
        (Fraction(5), Fraction(5)),
    ]
    for _ in range(n):
        refined: list[Point] = []
        for start, end in zip(vertices, vertices[1:] + vertices[:1]):
            dx = (end[0] - start[0]) / 3
            dy = (end[1] - start[1]) / 3
            one_third = (start[0] + dx, start[1] + dy)
            two_thirds = (start[0] + 2 * dx, start[1] + 2 * dy)
            rx, ry = rotate_clockwise_60((dx, dy))
            peak = (one_third[0] + rx, one_third[1] + ry)
            refined.extend((start, one_third, peak, two_thirds))
        vertices = refined
    return tuple(vertices)


def count_r0(d: Fraction) -> int:
    if d == 0:
        return 1
    step = abs(d)
    axis_count = (Fraction(10) // step) + 1
    return axis_count * axis_count


def ceil_div(a: int, b: int) -> int:
    return -((-a) // b)


def count_r1(d: Fraction) -> int:
    """Count lattice points in the closed radius-5 circle using integers only."""
    if d == 0:
        return 0
    step = abs(d)
    a, b = step.numerator, step.denominator
    center = 5 * b
    radius = 5 * b
    total = 0
    for p in range((10 * b) // a + 1):
        dx = a * p - center
        remaining = radius * radius - dx * dx
        if remaining < 0:
            continue
        vertical = isqrt(remaining)
        q_min = ceil_div(center - vertical, a)
        q_max = (center + vertical) // a
        total += max(0, q_max - q_min + 1)
    return total


def _edge_crossing_x(edge: Edge, row_y: Fraction) -> Qsqrt3:
    (x1, y1), (x2, y2) = edge
    dx = x2 - x1
    dy = y2 - y1
    if dy == 0:
        raise ValueError("horizontal edge has no unique crossing")
    # x = x1 + dx * ((row_y - y1*sqrt(3)) / (dy*sqrt(3)))
    return Qsqrt3(x1 - dx * y1 / dy, dx * row_y / (3 * dy))


def _p_interval(left: Qsqrt3, right: Qsqrt3, step: Fraction) -> tuple[int, int] | None:
    lo = ceil_qsqrt3(left / step)
    hi = floor_qsqrt3(right / step)
    return None if lo > hi else (lo, hi)


def _merged_size(intervals: list[tuple[int, int]]) -> int:
    if not intervals:
        return 0
    intervals.sort()
    total = 0
    left, right = intervals[0]
    for next_left, next_right in intervals[1:]:
        if next_left <= right + 1:
            right = max(right, next_right)
        else:
            total += right - left + 1
            left, right = next_left, next_right
    return total + right - left + 1


@lru_cache(maxsize=None)
def count_koch(step: Fraction, n: int) -> int:
    """Count d-points in closed K_n by an exact edge-bucketed scanline."""
    if step == 0:
        return 1
    step = abs(step)
    vertices = list(koch_vertices(n))
    edges: list[Edge] = list(zip(vertices, vertices[1:] + vertices[:1]))
    rows: dict[int, list[Edge]] = defaultdict(list)
    zero_boundary: list[tuple[Qsqrt3, Qsqrt3]] = []

    for edge in edges:
        (x1, y1), (x2, y2) = edge
        if y1 == y2:
            if y1 == 0:
                zero_boundary.append((Qsqrt3(min(x1, x2)), Qsqrt3(max(x1, x2))))
            continue

        low_y, high_y = sorted((y1, y2))
        low = Qsqrt3(Fraction(0), low_y) / step
        high = Qsqrt3(Fraction(0), high_y) / step
        q_min = ceil_qsqrt3(low)
        q_max = ceil_qsqrt3(high) - 1  # half-open: low <= y < high
        for q in range(q_min, q_max + 1):
            rows[q].append(edge)

        if min(y1, y2) <= 0 <= max(y1, y2):
            x = _edge_crossing_x(edge, Fraction(0))
            zero_boundary.append((x, x))

    total = 0
    for q, active_edges in rows.items():
        row_y = step * q
        crossings = sorted(_edge_crossing_x(edge, row_y) for edge in active_edges)
        if len(crossings) % 2:
            raise AssertionError(f"odd number of crossings on row {q}")
        intervals: list[tuple[int, int]] = []
        for i in range(0, len(crossings), 2):
            interval = _p_interval(crossings[i], crossings[i + 1], step)
            if interval is not None:
                intervals.append(interval)
        if q == 0:
            for left, right in zero_boundary:
                interval = _p_interval(left, right, step)
                if interval is not None:
                    intervals.append(interval)
        total += _merged_size(intervals)
    return total


def _orientation(edge: Edge, point: tuple[Fraction, Fraction]) -> Qsqrt3:
    (x1, y1), (x2, y2) = edge
    px, py = point
    dx, dy = x2 - x1, y2 - y1
    return Qsqrt3(dx * py, -dx * y1 - dy * (px - x1))


def point_in_closed_koch(point: tuple[Fraction, Fraction], n: int) -> bool:
    """Independent exact winding-number membership test, used for validation."""
    vertices = list(koch_vertices(n))
    edges: list[Edge] = list(zip(vertices, vertices[1:] + vertices[:1]))
    px, py = point
    py_alg = Qsqrt3(py)
    winding = 0
    for edge in edges:
        (x1, y1), (x2, y2) = edge
        y1_alg, y2_alg = Qsqrt3(Fraction(0), y1), Qsqrt3(Fraction(0), y2)
        orient = _orientation(edge, point)
        if orient == 0 and min(x1, x2) <= px <= max(x1, x2) and min(y1_alg, y2_alg) <= py_alg <= max(y1_alg, y2_alg):
            return True
        if y1_alg <= py_alg < y2_alg and orient.sign() > 0:
            winding += 1
        elif y2_alg <= py_alg < y1_alg and orient.sign() < 0:
            winding -= 1
    return winding != 0


def count_koch_slow(step: Fraction, n: int) -> int:
    """Independent O(grid points * edges) validator for small instances."""
    if step == 0:
        return 1
    step = abs(step)
    vertices = koch_vertices(n)
    min_x, max_x = min(x for x, _ in vertices), max(x for x, _ in vertices)
    min_y = min(Qsqrt3(Fraction(0), y) for _, y in vertices)
    max_y = max(Qsqrt3(Fraction(0), y) for _, y in vertices)
    p_min = ceil_qsqrt3(Qsqrt3(min_x) / step)
    p_max = floor_qsqrt3(Qsqrt3(max_x) / step)
    q_min = ceil_qsqrt3(min_y / step)
    q_max = floor_qsqrt3(max_y / step)
    return sum(
        point_in_closed_koch((step * p, step * q), n)
        for q in range(q_min, q_max + 1)
        for p in range(p_min, p_max + 1)
    )


@lru_cache(maxsize=None)
def _sqrt3(precision: int) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = precision
        return +Decimal(3).sqrt()


@lru_cache(maxsize=None)
def _limit_area_text(places: int) -> str:
    with localcontext() as ctx:
        ctx.prec = places + 100
        quantum = Decimal(1).scaleb(-places)
        return format((Decimal(40) * _sqrt3(ctx.prec)).quantize(quantum), "f")


@lru_cache(maxsize=None)
def area_text(n: int, places: int = 20) -> str:
    """Correctly rounded fixed-point area of K_n using Decimal arithmetic."""
    if n < 0:
        raise ValueError("n must be nonnegative")
    if n > 1000:
        # The omitted positive term is below 1e-347, far below the 20-place quantum.
        return _limit_area_text(places)
    with localcontext() as ctx:
        ctx.prec = places + 100
        # area(K_n) = (40 - 15*(4/9)^n) * sqrt(3)
        tail = (Decimal(4) / Decimal(9)) ** n
        area = (Decimal(40) - Decimal(15) * tail) * _sqrt3(ctx.prec)
        quantum = Decimal(1).scaleb(-places)
        return format(area.quantize(quantum), "f")
