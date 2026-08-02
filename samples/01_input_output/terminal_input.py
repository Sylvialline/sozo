"""用途：从终端/标准输入读取“数量 + n 个整数”。

示例输入：第一行 ``5``，第二行 ``8 3 1 9 2``。
示例输出：``count=5 sum=23 min=1 max=9``。
复杂度：读取全部文本为 O(输入大小)，保存 n 个整数为 O(n)。
常见陷阱：``input()`` 会去掉行末换行但不去掉其他空白；只消费格式声明的数据。
"""

from io import StringIO
import sys
from typing import TextIO


SAMPLE = "5\n8 3 1 9 2\n"


def read_counted_integers(stream: TextIO) -> list[int]:
    count_line = stream.readline()
    if not count_line:
        raise ValueError("缺少整数数量")
    count = int(count_line)
    tokens = iter(stream.read().split())
    try:
        return [int(next(tokens)) for _ in range(count)]
    except StopIteration as error:
        raise ValueError(f"声明 {count} 个整数，但输入提前结束") from error


def main() -> None:
    # 直接运行时使用内置样例；重定向/管道输入时读取 sys.stdin。
    text = SAMPLE if sys.stdin.isatty() else sys.stdin.read()
    values = read_counted_integers(StringIO(text or SAMPLE))
    print(
        f"count={len(values)} sum={sum(values)} "
        f"min={min(values, default=None)} max={max(values, default=None)}"
    )


if __name__ == "__main__":
    main()
