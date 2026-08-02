"""用途：让 solve(text) 用 yield 逐行产生答案，runner 再统一格式化。
示例输入："3 1 2"
示例输出：count=3、sum=6、sorted=[1, 2, 3]
复杂度：排序 O(n log n)。
陷阱：生成器是惰性的；只有被迭代时，yield 之间的代码才会执行。
"""

from collections.abc import Iterable


def solve(text: str) -> Iterable[str]:
    numbers = list(map(int, text.split()))
    yield f"count={len(numbers)}"
    yield f"sum={sum(numbers)}"
    yield f"sorted={sorted(numbers)}"


def main() -> None:
    print("\n".join(solve("3 1 2")))


if __name__ == "__main__":
    main()
