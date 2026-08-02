"""用途：一维 DP 求 0/1 背包在容量限制下的最大价值。
示例输入：物品 (重量,价值)=[(2,3),(3,4),(4,5)]，容量 5。
示例输出：最大价值 7（前两个物品）。
复杂度：O(物品数×容量) 时间，O(容量) 空间。
常见陷阱：0/1 背包容量必须倒序遍历；正序会让同一物品被重复使用成完全背包。
"""


def knapsack_01(items: list[tuple[int, int]], capacity: int) -> int:
    if capacity < 0 or any(weight <= 0 for weight, _ in items):
        raise ValueError("容量非负且物品重量必须为正")
    best = [0] * (capacity + 1)
    for weight, value in items:
        for current_capacity in range(capacity, weight - 1, -1):
            best[current_capacity] = max(
                best[current_capacity],
                best[current_capacity - weight] + value,
            )
    return best[capacity]


def main() -> None:
    items = [(2, 3), (3, 4), (4, 5)]
    print("best value:", knapsack_01(items, 5))
    print("zero capacity:", knapsack_01(items, 0))


if __name__ == "__main__":
    main()
