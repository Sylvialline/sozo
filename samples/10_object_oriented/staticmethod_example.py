"""``staticmethod``：与类概念相关、但不需要 ``self`` 或 ``cls`` 的函数。

示例输入：三边 3、4、5，以及文本 "8,15,17"。
示例输出：两组边均构成三角形，后一组构成直角三角形。
复杂度：校验和计算均为 O(1)。
常见陷阱：静态方法不参与实例状态；若需要构造子类实例，应使用 classmethod。
"""


class Triangle:
    def __init__(self, a: float, b: float, c: float) -> None:
        if not self.is_valid(a, b, c):
            raise ValueError("invalid triangle")
        self.sides = (a, b, c)

    @staticmethod
    def is_valid(a: float, b: float, c: float) -> bool:
        x, y, z = sorted((a, b, c))
        return x > 0 and x + y > z

    @staticmethod
    def parse_sides(text: str) -> tuple[float, float, float]:
        values = tuple(map(float, text.split(",")))
        if len(values) != 3:
            raise ValueError("expected three sides")
        return values  # type: ignore[return-value]

    def is_right(self) -> bool:
        x, y, z = sorted(self.sides)
        return abs(x * x + y * y - z * z) < 1e-9


def main() -> None:
    print("3-4-5 valid:", Triangle.is_valid(3, 4, 5))
    triangle = Triangle(*Triangle.parse_sides("8,15,17"))
    print("8-15-17 right:", triangle.is_right())


if __name__ == "__main__":
    main()
