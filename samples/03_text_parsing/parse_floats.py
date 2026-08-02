"""用途：解析普通小数、科学计数法和逗号分隔浮点数。

示例输入：``"1.5 -2e-3 4"``。
示例输出：``[1.5, -0.002, 4.0] mean=1.832667``。
复杂度：O(输入字符数)。
常见陷阱：浮点数不可用 ``==`` 判断计算结果；NaN/inf 需用 math.isfinite 检查。
"""

import math


def parse_finite_floats(text: str) -> list[float]:
    values = [float(token) for token in text.replace(",", " ").split()]
    if not all(math.isfinite(value) for value in values):
        raise ValueError("输入包含 NaN 或无穷大")
    return values


def main() -> None:
    values = parse_finite_floats("1.5 -2e-3 4")
    print(values)
    print(f"mean={sum(values) / len(values):.6f}")
    print("0.1+0.2 close to 0.3:", math.isclose(0.1 + 0.2, 0.3))


if __name__ == "__main__":
    main()
