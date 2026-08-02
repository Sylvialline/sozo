"""用途：记录每个任务和整批任务的 perf_counter 耗时。
示例输入：[10_000, 20_000, 30_000]
示例输出：case1: ... ms；total: ... ms
复杂度：计时 O(1)，示例求和总计 O(sum(n))。
陷阱：不要用 time.time 做精细耗时测量；短任务应多次重复。
"""

from time import perf_counter


def main() -> None:
    total_started = perf_counter()
    for index, n in enumerate([10_000, 20_000, 30_000], 1):
        started = perf_counter()
        result = sum(range(n))
        elapsed = perf_counter() - started
        print(f"case{index}: result={result}, {elapsed * 1000:.3f} ms")
    print(f"total: {(perf_counter() - total_started) * 1000:.3f} ms")


if __name__ == "__main__":
    main()
