"""用途：用命名正则组解析一行混合文本中的编号、标签和数值。

示例输入：``"id=17 name=alpha value=-3.25e2"``。
示例输出：``{'id': 17, 'name': 'alpha', 'value': -325.0}``。
复杂度：本模式对单行近似 O(行长度)。
常见陷阱：应使用 raw string；``search`` 允许前后杂字，严格格式用 ``fullmatch``。
"""

import re


LINE_PATTERN = re.compile(
    r"id=(?P<id>\d+)\s+"
    r"name=(?P<name>[A-Za-z_]\w*)\s+"
    r"value=(?P<value>[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)"
)


def parse_record(line: str) -> dict[str, int | float | str]:
    match = LINE_PATTERN.fullmatch(line.strip())
    if match is None:
        raise ValueError(f"格式错误：{line!r}")
    return {
        "id": int(match["id"]),
        "name": match["name"],
        "value": float(match["value"]),
    }


def main() -> None:
    print(parse_record("id=17 name=alpha value=-3.25e2"))


if __name__ == "__main__":
    main()
