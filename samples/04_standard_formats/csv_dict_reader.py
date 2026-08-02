"""用途：用 csv.DictReader 按列名读取 CSV，避免手写列下标。
示例输入：city,temp / Tokyo,31.5 / Sendai,27.0
示例输出：Tokyo: 31.5，Sendai: 27.0，平均 29.25。
复杂度：O(字符总数)，本例保存记录需 O(行数) 空间。
常见陷阱：读出的值全是字符串；重复表头会覆盖同名字段。
"""

import csv
from io import StringIO


def read_temperatures(text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(StringIO(text)))


def main() -> None:
    text = "city,temp\nTokyo,31.5\nSendai,27.0\n"
    rows = read_temperatures(text)
    for row in rows:
        print(f"{row['city']}: {float(row['temp']):.1f}")
    mean = sum(float(row["temp"]) for row in rows) / len(rows)
    print(f"mean: {mean:.2f}")


if __name__ == "__main__":
    main()
