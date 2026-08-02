"""用途：用 csv.reader 读取带引号、逗号和表头的 CSV。
示例输入：name,score,note / Alice,90,"fast, stable"
示例输出：表头与两条类型转换后的记录。
复杂度：O(字符总数)，额外空间 O(单行长度)（本例为展示而收集到列表）。
常见陷阱：不要用 split(",") 解析 CSV；文件应以 newline="" 打开。
"""

import csv
from io import StringIO


def parse_csv(text: str) -> tuple[list[str], list[tuple[str, int, str]]]:
    rows = csv.reader(StringIO(text))
    header = next(rows)
    records = [(name, int(score), note) for name, score, note in rows]
    return header, records


def main() -> None:
    text = 'name,score,note\nAlice,90,"fast, stable"\nBob,85,careful\n'
    header, records = parse_csv(text)
    print("header:", header)
    for record in records:
        print(record)


if __name__ == "__main__":
    main()
