"""用 ``repr``、``vars``、``pprint`` 和 ``inspect.signature`` 检查状态。

示例输入：Point(2,3) 及函数 ``scale(point, factor=2)``。
示例输出：对象字段字典、可读嵌套数据和函数签名。
复杂度：检查/格式化成本与对象中可见数据量线性相关。
常见陷阱：调试打印可能泄露大对象或敏感数据；``vars`` 只适用于有 ``__dict__`` 的对象。
"""

from dataclasses import dataclass
import inspect
from pprint import pprint


@dataclass
class Point:
    x: int
    y: int


def scale(point: Point, factor: int = 2) -> Point:
    return Point(point.x * factor, point.y * factor)


def main() -> None:
    point = Point(2, 3)
    nested = {"point": point, "neighbors": [Point(1, 3), Point(3, 3)]}
    print("repr:", repr(point))
    print("vars:", vars(point))
    print("pprint:")
    pprint(nested, sort_dicts=False)
    print("signature:", inspect.signature(scale))
    print("annotations:", inspect.get_annotations(scale))


if __name__ == "__main__":
    main()
