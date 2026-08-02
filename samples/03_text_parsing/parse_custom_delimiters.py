"""用途：按多种自定义分隔符（逗号、分号、竖线）切分字段。

示例输入：``"red, green;blue| yellow"``。
示例输出：``['red', 'green', 'blue', 'yellow']``。
复杂度：对本模式通常为 O(文本长度)。
常见陷阱：竖线在正则中表示“或”，匹配字面量必须写 ``\\|`` 或放字符类。
"""

import re


DELIMITER = re.compile(r"\s*[,;|]\s*")


def split_fields(text: str) -> list[str]:
    return [field for field in DELIMITER.split(text.strip()) if field]


def main() -> None:
    print(split_fields("red, green;blue| yellow"))


if __name__ == "__main__":
    main()
