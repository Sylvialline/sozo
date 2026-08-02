"""把 tokenizer、parser 和结果对象分离的简洁解析器设计。

示例输入：``width=12\\nheight = 8\\n# comment``。
示例输出：Config(values={'width': 12, 'height': 8})，面积 96。
复杂度：对总长度 n 的文本解析为 O(n)，查找配置项平均 O(1)。
常见陷阱：不要让 tokenizer 同时执行求值；分层后错误位置和测试更清楚。
"""

from dataclasses import dataclass
import re

TOKEN_PATTERN = re.compile(r"\s*(?:(?P<name>[A-Za-z_]\w*)|(?P<int>-?\d+)|(?P<equal>=))")


class Tokenizer:
    def tokenize(self, line: str) -> list[tuple[str, str]]:
        tokens: list[tuple[str, str]] = []
        position = 0
        while position < len(line):
            match = TOKEN_PATTERN.match(line, position)
            if not match:
                raise ValueError(f"invalid token at column {position + 1}")
            kind = match.lastgroup
            if kind is None:
                raise ValueError("token has no kind")
            tokens.append((kind, match.group(kind)))
            position = match.end()
        return tokens


@dataclass
class Config:
    values: dict[str, int]

    def require(self, name: str) -> int:
        if name not in self.values:
            raise KeyError(f"missing setting: {name}")
        return self.values[name]


class ConfigParser:
    def __init__(self, tokenizer: Tokenizer) -> None:
        self.tokenizer = tokenizer

    def parse(self, text: str) -> Config:
        values: dict[str, int] = {}
        for line_number, raw_line in enumerate(text.splitlines(), 1):
            line = raw_line.split("#", 1)[0].strip()
            if not line:
                continue
            tokens = self.tokenizer.tokenize(line)
            if [kind for kind, _ in tokens] != ["name", "equal", "int"]:
                raise ValueError(f"invalid assignment on line {line_number}")
            values[tokens[0][1]] = int(tokens[2][1])
        return Config(values)


def main() -> None:
    text = "width=12\nheight = 8\n# comment"
    config = ConfigParser(Tokenizer()).parse(text)
    print(config)
    print("area:", config.require("width") * config.require("height"))


if __name__ == "__main__":
    main()
