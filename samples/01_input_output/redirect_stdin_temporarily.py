"""用途：用上下文管理器临时替换 ``sys.stdin``，退出后自动恢复。

示例输入：临时文本 ``2 11 13``。
示例输出：``inside: 24`` 和 ``restored: True``。
复杂度：上下文切换 O(1)，示例解析 O(n)。
常见陷阱：手动赋值后遇到异常可能无法恢复；必须用 try/finally 或 contextmanager。
"""

from contextlib import contextmanager
from io import StringIO
import sys
from typing import Iterator, TextIO


@contextmanager
def redirected_stdin(stream: TextIO) -> Iterator[None]:
    original = sys.stdin
    try:
        sys.stdin = stream
        yield
    finally:
        sys.stdin = original


def main() -> None:
    original = sys.stdin
    with redirected_stdin(StringIO("2 11 13\n")):
        count, *values = map(int, input().split())
        assert count == len(values)
        print("inside:", sum(values))
    print("restored:", sys.stdin is original)


if __name__ == "__main__":
    main()
