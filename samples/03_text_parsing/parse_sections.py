"""用途：解析 ``[section]`` 标题下的多行内容。

示例输入：``[red]`` 下有 apple/berry，``[blue]`` 下有 sky。
示例输出：``{'red': ['apple', 'berry'], 'blue': ['sky']}``。
复杂度：O(文本长度)，结果占 O(有效内容大小)。
常见陷阱：标题前的内容和重复标题需定义行为；本例都会显式报错。
"""


def parse_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current: list[str] | None = None
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            name = line[1:-1].strip()
            if not name or name in sections:
                raise ValueError(f"第 {line_number} 行标题为空或重复")
            current = sections[name] = []
        elif current is None:
            raise ValueError(f"第 {line_number} 行出现在任何 section 之前")
        else:
            current.append(line)
    return sections


def main() -> None:
    text = "[red]\napple\nberry\n\n[blue]\nsky\n"
    print(parse_sections(text))


if __name__ == "__main__":
    main()
