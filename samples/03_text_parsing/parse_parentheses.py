"""用途：用栈校验括号并找出每对括号的下标。

示例输入：``"a(b[c]{d})"``。
示例输出：``[(3, 5), (6, 8), (1, 9)]``（按闭合顺序）。
复杂度：时间 O(n)，最坏栈空间 O(n)。
常见陷阱：只统计左右括号数量不能发现 ``)(``；必须检查种类和嵌套顺序。
"""


OPEN_TO_CLOSE = {"(": ")", "[": "]", "{": "}"}
CLOSE_TO_OPEN = {close: open_ for open_, close in OPEN_TO_CLOSE.items()}


def matching_pairs(text: str) -> list[tuple[int, int]]:
    stack: list[tuple[str, int]] = []
    pairs: list[tuple[int, int]] = []
    for index, character in enumerate(text):
        if character in OPEN_TO_CLOSE:
            stack.append((character, index))
        elif character in CLOSE_TO_OPEN:
            if not stack or stack[-1][0] != CLOSE_TO_OPEN[character]:
                raise ValueError(f"位置 {index} 的 {character!r} 无匹配")
            _, opening_index = stack.pop()
            pairs.append((opening_index, index))
    if stack:
        opening, index = stack[-1]
        raise ValueError(f"位置 {index} 的 {opening!r} 未闭合")
    return pairs


def main() -> None:
    print(matching_pairs("a(b[c]{d})"))


if __name__ == "__main__":
    main()
