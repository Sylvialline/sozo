"""用途：回溯生成含重复元素序列的全部不重复排列。
示例输入：[1,1,2]。
示例输出：(1,1,2)、(1,2,1)、(2,1,1)。
复杂度：至多 O(n!×n) 时间（复制答案），used/path/递归栈 O(n)，答案空间另计。
常见陷阱：加入答案时必须复制 path；排序后跳过“同层重复”；规模稍大即组合爆炸。
"""


def unique_permutations(values: list[int]) -> list[tuple[int, ...]]:
    values = sorted(values)
    used = [False] * len(values)
    path: list[int] = []
    result: list[tuple[int, ...]] = []

    def search() -> None:
        if len(path) == len(values):
            result.append(tuple(path))
            return
        for index, value in enumerate(values):
            if used[index]:
                continue
            if index > 0 and values[index - 1] == value and not used[index - 1]:
                continue
            used[index] = True
            path.append(value)
            search()
            path.pop()
            used[index] = False

    search()
    return result


def main() -> None:
    for permutation in unique_permutations([1, 1, 2]):
        print(permutation)


if __name__ == "__main__":
    main()
