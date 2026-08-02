"""``__repr__`` 面向调试，``__str__`` 面向用户显示。

示例输入：Student("Alice", [90,80,100])。
示例输出：repr 显示可辨认字段，str 显示 Alice (average=90.0)。
复杂度：计算平均分 O(n)，格式化分数字段 O(n)。
常见陷阱：容器打印元素时主要使用 ``repr``；不要在 ``repr`` 中隐藏关键状态。
"""


class Student:
    def __init__(self, name: str, scores: list[int]) -> None:
        self.name = name
        self.scores = scores[:]

    def average(self) -> float:
        return sum(self.scores) / len(self.scores) if self.scores else 0.0

    def __repr__(self) -> str:
        return f"Student(name={self.name!r}, scores={self.scores!r})"

    def __str__(self) -> str:
        return f"{self.name} (average={self.average():.1f})"


def main() -> None:
    student = Student("Alice", [90, 80, 100])
    print("repr:", repr(student))
    print("str:", str(student))
    print("inside list:", [student])


if __name__ == "__main__":
    main()
