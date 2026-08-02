"""用途：用 ``sys.stdin.buffer`` 一次读取大量空白分隔整数。

示例输入：``5`` 换行后 ``8 3 1 9 2``。
示例输出：``count=5 sum=23 max=9``。
复杂度：读取为 O(输入字节数)，解析前 n 个整数为 O(n)，保存为 O(n)。
常见陷阱：buffer 返回 bytes；只消费声明的 n 项，后续 token 可属于下一段输入。
"""

from io import BytesIO
import sys
from typing import BinaryIO


SAMPLE = b"5\n8 3 1 9 2\n"


def read_counted_integers(stream: BinaryIO) -> list[int]:
    tokens = iter(stream.read().split())
    first = next(tokens, None)
    if first is None:
        raise ValueError("输入为空")
    count = int(first)
    try:
        return [int(next(tokens)) for _ in range(count)]
    except StopIteration as error:
        raise ValueError(f"声明 {count} 个整数，但输入提前结束") from error


def main() -> None:
    data = SAMPLE if sys.stdin.isatty() else sys.stdin.buffer.read()
    values = read_counted_integers(BytesIO(data or SAMPLE))
    print(f"count={len(values)} sum={sum(values)} max={max(values, default=None)}")


if __name__ == "__main__":
    main()
