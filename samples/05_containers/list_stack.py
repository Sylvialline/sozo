"""用途：用 list 实现后进先出栈，并示范括号匹配。
示例输入："([{}])"。
示例输出：balanced: True。
复杂度：末尾 append/pop 摊还 O(1)，完整扫描 O(n)，最坏空间 O(n)。
常见陷阱：从 list 头部 insert/pop 是 O(n)；空栈 pop() 会 IndexError。
"""


def is_balanced(text: str) -> bool:
    opening = "([{"
    matching = {")": "(", "]": "[", "}": "{"}
    stack: list[str] = []
    for char in text:
        if char in opening:
            stack.append(char)
        elif char in matching:
            if not stack or stack.pop() != matching[char]:
                return False
    return not stack


def main() -> None:
    for text in ["([{}])", "([)]", "text"]:
        print(text, "balanced:", is_balanced(text))


if __name__ == "__main__":
    main()
