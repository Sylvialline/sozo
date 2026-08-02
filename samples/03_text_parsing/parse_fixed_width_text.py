"""用途：按固定列宽解析无分隔符的表格文本。

示例输入：``ALICE     093OK`` 与 ``BOB       087NG``。
示例输出：姓名、整数分数和状态组成的字典列表。
复杂度：O(行数 × 行宽)。
常见陷阱：切片下标按字符而非显示宽度；全角字符会让视觉列宽与索引不一致。
"""


def parse_row(line: str) -> dict[str, object]:
    if len(line) < 15:
        raise ValueError(f"固定宽度行过短：{line!r}")
    return {
        "name": line[0:10].strip(),
        "score": int(line[10:13]),
        "status": line[13:15],
    }


def main() -> None:
    text = "ALICE     093OK\nBOB       087NG\n"
    records = [parse_row(line) for line in text.splitlines()]
    print(records)


if __name__ == "__main__":
    main()
