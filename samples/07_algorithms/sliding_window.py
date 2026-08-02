"""用途：滑动窗口求“全为非负数”时和至少 target 的最短连续子数组。
示例输入：target=7，values=[2,3,1,2,4,3]。
示例输出：最短长度 2（[4,3]）。
复杂度：左右指针各移动至多 n 次，时间 O(n)，额外空间 O(1)。
常见陷阱：该收缩逻辑依赖元素非负；含负数时窗口和不单调，应换前缀和等方法。
"""


def minimum_length_at_least(target: int, values: list[int]) -> int | None:
    if target <= 0:
        return 0
    if any(value < 0 for value in values):
        raise ValueError("此滑动窗口只适用于非负数")
    best = len(values) + 1
    total = 0
    left = 0
    for right, value in enumerate(values):
        total += value
        while total >= target:
            best = min(best, right - left + 1)
            total -= values[left]
            left += 1
    return best if best <= len(values) else None


def main() -> None:
    values = [2, 3, 1, 2, 4, 3]
    print("minimum length:", minimum_length_at_least(7, values))
    print("not found:", minimum_length_at_least(100, values))


if __name__ == "__main__":
    main()
