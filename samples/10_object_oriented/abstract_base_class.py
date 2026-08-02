"""用 ``ABC`` 和 ``abstractmethod`` 规定子类必须实现的接口。

示例输入：半径 2 的圆和宽 3、高 4 的矩形。
示例输出：面积约 12.566 和 12；直接实例化 Shape 会产生 TypeError。
复杂度：面积计算均为 O(1)。
常见陷阱：抽象方法可有函数体，但未完成所有抽象方法的类不能实例化。
"""

from abc import ABC, abstractmethod
from math import pi


class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        """返回面积。"""

    def describe(self) -> str:
        return f"{type(self).__name__}: area={self.area():.3f}"


class Circle(Shape):
    def __init__(self, radius: float) -> None:
        self.radius = radius

    def area(self) -> float:
        return pi * self.radius**2


class Rectangle(Shape):
    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height


def main() -> None:
    for shape in (Circle(2), Rectangle(3, 4)):
        print(shape.describe())
    try:
        Shape()
    except TypeError as error:
        print("cannot instantiate Shape:", type(error).__name__)


if __name__ == "__main__":
    main()
