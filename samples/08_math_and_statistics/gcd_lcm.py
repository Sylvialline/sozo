"""最大公约数、最小公倍数与扩展欧几里得算法。

示例输入：整数 84 和 30。
示例输出：gcd=6、lcm=420，并给出满足 84*x+30*y=6 的系数。
复杂度：``gcd`` 和扩展欧几里得均为 O(log(min(a, b)))。
常见陷阱：``math.gcd`` 总是返回非负数；``lcm(a, 0)`` 为 0。
"""

from math import gcd, lcm


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """返回 ``(g, x, y)``，使 ``a*x + b*y == g == gcd(a, b)``。"""
    old_r, r = abs(a), abs(b)
    old_x, x = 1, 0
    old_y, y = 0, 1
    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_x, x = x, old_x - q * x
        old_y, y = y, old_y - q * y
    return old_r, old_x * (1 if a >= 0 else -1), old_y * (1 if b >= 0 else -1)


def main() -> None:
    a, b = 84, 30
    g, x, y = extended_gcd(a, b)
    print("gcd:", gcd(a, b))
    print("lcm:", lcm(a, b))
    print("multiple gcd/lcm:", gcd(84, 30, 18), lcm(4, 6, 10))
    print("Bezout:", g, x, y, "check:", a * x + b * y)


if __name__ == "__main__":
    main()
