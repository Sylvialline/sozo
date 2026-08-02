"""二维向量、叉积、方向判断与线段相交速查。

示例输入：向量 (3,4)、点 A(0,0)、B(4,0)、C(2,1)。
示例输出：向量长度 5，C 位于有向边 AB 左侧，两条线段相交。
复杂度：每个几何运算均为 O(1)。
常见陷阱：浮点几何要使用 epsilon；叉积正负依赖坐标系和点的顺序。
"""

from math import hypot

Point = tuple[float, float]
EPS = 1e-9


def sub(a: Point, b: Point) -> Point:
    return a[0] - b[0], a[1] - b[1]


def dot(a: Point, b: Point) -> float:
    return a[0] * b[0] + a[1] * b[1]


def cross(a: Point, b: Point) -> float:
    return a[0] * b[1] - a[1] * b[0]


def orientation(a: Point, b: Point, c: Point) -> float:
    return cross(sub(b, a), sub(c, a))


def on_segment(a: Point, b: Point, p: Point) -> bool:
    return (
        abs(orientation(a, b, p)) <= EPS
        and min(a[0], b[0]) - EPS <= p[0] <= max(a[0], b[0]) + EPS
        and min(a[1], b[1]) - EPS <= p[1] <= max(a[1], b[1]) + EPS
    )


def segments_intersect(a: Point, b: Point, c: Point, d: Point) -> bool:
    o1, o2 = orientation(a, b, c), orientation(a, b, d)
    o3, o4 = orientation(c, d, a), orientation(c, d, b)
    if ((o1 > EPS and o2 < -EPS) or (o1 < -EPS and o2 > EPS)) and (
        (o3 > EPS and o4 < -EPS) or (o3 < -EPS and o4 > EPS)
    ):
        return True
    return any(
        (
            on_segment(a, b, c),
            on_segment(a, b, d),
            on_segment(c, d, a),
            on_segment(c, d, b),
        )
    )


def main() -> None:
    vector = (3.0, 4.0)
    a, b, c = (0.0, 0.0), (4.0, 0.0), (2.0, 1.0)
    print("length:", hypot(*vector))
    print("dot with x-axis:", dot(vector, (1.0, 0.0)))
    print("orientation:", orientation(a, b, c), "(positive = left)")
    print("intersect:", segments_intersect(a, (4, 4), (0, 4), (4, 0)))


if __name__ == "__main__":
    main()
