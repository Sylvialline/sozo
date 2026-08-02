"""用途：集中保存常见的整数、键值行和分段文本解析函数。
示例输入："1, -2, 30"；"name = Alice"
示例输出：[1, -2, 30]；{"name": "Alice"}
复杂度：均为 O(输入文本长度)。
陷阱：split 适合规则格式；格式不固定时应先校验，避免静默吞掉坏数据。
"""

import re


def integers(text: str) -> list[int]:
    """提取带正负号的十进制整数。"""
    return list(map(int, re.findall(r"[+-]?\d+", text)))


def key_values(text: str, separator: str = "=") -> dict[str, str]:
    result = {}
    for line_number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if separator not in line:
            raise ValueError(f"第 {line_number} 行缺少 {separator!r}")
        key, value = line.split(separator, 1)
        result[key.strip()] = value.strip()
    return result


def sections(text: str) -> dict[str, list[str]]:
    """解析形如 [section] 的简单分段文本。"""
    result: dict[str, list[str]] = {}
    current: str | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("[") and line.endswith("]"):
            current = line[1:-1].strip()
            result[current] = []
        elif line:
            if current is None:
                raise ValueError("内容出现在第一个分段标题之前")
            result[current].append(line)
    return result


def main() -> None:
    print(integers("x=1, y=-2, z=+30"))
    print(key_values("name = Alice\nscore = 95"))
    print(sections("[A]\none\ntwo\n[B]\nthree"))


if __name__ == "__main__":
    main()
