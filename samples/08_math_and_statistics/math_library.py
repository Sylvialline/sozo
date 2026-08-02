"""常用 ``math`` 标准库速查。

示例输入：点 (3, 4)、角度 30°、数值 2.7。
示例输出：距离 5.0、sin(30°)=0.5、floor/ceil=2/3。
复杂度：本例各函数调用均为 O(1)。
常见陷阱：三角函数接收弧度；``//`` 对负数向下取整，和向零截断不同。
"""

import math


def main() -> None:
    x, y = 3.0, 4.0
    print("sqrt:", math.sqrt(x * x + y * y))
    print("hypot:", math.hypot(x, y))
    print("distance:", math.dist((0, 0), (x, y)))

    angle = math.radians(30)
    print("sin(30°):", round(math.sin(angle), 10))
    print("degrees:", math.degrees(angle))

    value = 2.7
    print("floor/ceil/trunc:", math.floor(value), math.ceil(value), math.trunc(value))
    print("negative // and trunc:", -7 // 3, math.trunc(-7 / 3))
    print("log2/exp:", math.log2(8), round(math.exp(1), 6))
    print("isfinite(inf):", math.isfinite(math.inf))


if __name__ == "__main__":
    main()
