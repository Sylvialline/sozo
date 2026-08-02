"""浮点数比较、稳定求和和十进制定点数速查。

示例输入：0.1+0.2 与 0.3，以及 [1e16, 1, -1e16]。
示例输出：直接相等为 False，``isclose`` 为 True，``fsum`` 得到 1.0。
复杂度：比较 O(1)，``math.fsum`` 对 n 个数为 O(n)。
常见陷阱：不要用 ``==`` 比较计算所得浮点数；绝对误差和相对误差用途不同。
"""

import math
from decimal import Decimal


def almost_equal(a: float, b: float, eps: float = 1e-9) -> bool:
    """绝对/相对误差兼顾的常用比较。"""
    return math.isclose(a, b, rel_tol=eps, abs_tol=eps)


def main() -> None:
    a = 0.1 + 0.2
    b = 0.3
    print("raw:", a)
    print("==:", a == b)
    print("isclose:", almost_equal(a, b))
    print("stable sum:", math.fsum([1e16, 1.0, -1e16]))
    print("decimal:", Decimal("0.1") + Decimal("0.2") == Decimal("0.3"))
    print("near zero:", math.isclose(1e-12, 0.0, abs_tol=1e-9))


if __name__ == "__main__":
    main()
