"""用 ``classmethod`` 编写替代构造器，并通过 ``cls`` 支持子类。

示例输入："25.5 C" 和华氏 68。
示例输出：25.5°C 与 20.0°C；子类调用替代构造器仍返回子类实例。
复杂度：解析与构造均为 O(输入字符串长度)。
常见陷阱：类方法接收 ``cls``；若硬编码类名，会破坏继承时的构造行为。
"""


class Temperature:
    def __init__(self, celsius: float) -> None:
        self.celsius = celsius

    @classmethod
    def from_fahrenheit(cls, fahrenheit: float) -> "Temperature":
        return cls((fahrenheit - 32) * 5 / 9)

    @classmethod
    def from_text(cls, text: str) -> "Temperature":
        value_text, unit = text.split()
        value = float(value_text)
        if unit.upper() == "C":
            return cls(value)
        if unit.upper() == "F":
            return cls.from_fahrenheit(value)
        raise ValueError(f"unknown unit: {unit}")


class LoggedTemperature(Temperature):
    pass


def main() -> None:
    first = Temperature.from_text("25.5 C")
    second = Temperature.from_fahrenheit(68)
    child = LoggedTemperature.from_text("32 F")
    print(f"temperatures: {first.celsius:.1f}, {second.celsius:.1f}")
    print("subclass preserved:", type(child).__name__, f"{child.celsius:.1f}")


if __name__ == "__main__":
    main()
