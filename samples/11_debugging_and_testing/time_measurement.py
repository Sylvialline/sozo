"""用 ``perf_counter`` 测整段耗时，用 ``timeit`` 比较短小代码。

示例输入：计算 0..99999 的平方和，并比较两种求和表达式。
示例输出：正确结果及毫秒耗时；具体时间随机器而变。
复杂度：被测平方和 O(n)；计时器读取本身为 O(1)。
常见陷阱：单次微基准噪声很大；先验证正确性，再多次重复并比较中位数。
"""

from statistics import median
from time import perf_counter
from timeit import repeat


def sum_of_squares(n: int) -> int:
    return sum(value * value for value in range(n))


def main() -> None:
    start = perf_counter()
    answer = sum_of_squares(100_000)
    elapsed_ms = (perf_counter() - start) * 1000
    print("answer:", answer)
    print(f"elapsed: {elapsed_ms:.3f} ms")

    timings = repeat("sum(range(1000))", repeat=5, number=1000)
    print(f"timeit median: {median(timings) * 1000:.3f} ms / 1000 runs")


if __name__ == "__main__":
    main()
