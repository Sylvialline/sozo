"""用途：解析 ``key=value`` 配置行，支持空行和 # 注释。

示例输入：``name = Taro``、``limit = 20``、``path = a=b.txt``。
示例输出：``{'name': 'Taro', 'limit': '20', 'path': 'a=b.txt'}``。
复杂度：O(文本长度)，字典占 O(键值总长度)。
常见陷阱：只在第一个等号处分割；重复键应明确覆盖还是报错。
"""


def parse_key_values(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"第 {line_number} 行缺少 =")
        key, value = (part.strip() for part in line.split("=", 1))
        if not key:
            raise ValueError(f"第 {line_number} 行键为空")
        if key in result:
            raise ValueError(f"第 {line_number} 行重复键：{key}")
        result[key] = value
    return result


def main() -> None:
    text = """\
# exam settings
name = Taro
limit = 20
path = a=b.txt
"""
    print(parse_key_values(text))


if __name__ == "__main__":
    main()
