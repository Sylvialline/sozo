"""用途：用 yield 逐项产生结果，并展示生成器的惰性与提前停止。
示例输入：文本 "1 2 bad 3"。
示例输出：1、2、跳过 bad、3；只取前两个时后续代码不会执行。
复杂度：完整消费 O(token 数)，生成器状态占 O(1)（不计输入文本）。
常见陷阱：调用生成器函数不会运行函数体；异常和副作用发生在迭代时；只能消费一次。
"""

from collections.abc import Iterator


def valid_integers(text: str) -> Iterator[int]:
    for token in text.split():
        try:
            yield int(token)
        except ValueError:
            print(f"skip: {token}")


def take(iterable: Iterator[int], count: int) -> list[int]:
    result = []
    for _ in range(count):
        try:
            result.append(next(iterable))
        except StopIteration:
            break
    return result


def main() -> None:
    print("all:", list(valid_integers("1 2 bad 3")))
    numbers = valid_integers("10 20 bad 30")
    print("first two:", take(numbers, 2))  # bad 尚未被处理
    print("remaining:", list(numbers))


if __name__ == "__main__":
    main()
