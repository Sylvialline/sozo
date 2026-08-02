"""用途：用 csv.writer / DictWriter 正确生成 CSV 文本。
示例输入：[("Alice", 90, "fast, stable"), ("Bob", 85, "careful")]
示例输出：自动为含逗号字段加引号的 CSV。
复杂度：O(输出字符总数)，StringIO 占 O(输出大小) 空间。
常见陷阱：真实文件用 open(..., newline="", encoding="utf-8")，否则 Windows 可能出现空行。
"""

import csv
from io import StringIO


def make_csv(rows: list[tuple[str, int, str]]) -> str:
    output = StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["name", "score", "note"])
    writer.writerows(rows)
    return output.getvalue()


def make_dict_csv(rows: list[dict[str, object]]) -> str:
    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=["name", "score"], lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def main() -> None:
    print(make_csv([("Alice", 90, "fast, stable"), ("Bob", 85, "careful")]), end="")
    print(make_dict_csv([{"name": "Carol", "score": 88}]), end="")


if __name__ == "__main__":
    main()
