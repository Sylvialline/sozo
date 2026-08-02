"""用途：解释简单整数赋值语言，展示 tokenizer、递归下降 parser 和对象设计。
示例输入：y = x * 3 + 2
示例输出：y = 14
复杂度：每行 O(token 数)，变量查询平均 O(1)。
陷阱：不要对不可信输入使用 eval；解析结束后必须确认没有剩余 token。
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOKEN = re.compile(r"\d+|[A-Za-z_]\w*|[=()+*-]")


def tokenize(line: str) -> list[str]:
    tokens = TOKEN.findall(line)
    if "".join(tokens) != re.sub(r"\s+", "", line):
        raise SyntaxError(f"unknown token in {line!r}")
    return tokens


@dataclass
class Interpreter:
    variables: dict[str, int] = field(default_factory=dict)
    tokens: list[str] = field(init=False, default_factory=list)
    position: int = field(init=False, default=0)

    def execute(self, line: str) -> tuple[str, int]:
        self.tokens = tokenize(line)
        self.position = 0
        name = self.take()
        if not name.isidentifier():
            raise SyntaxError("assignment must start with a variable")
        self.expect("=")
        value = self.expression()
        if self.position != len(self.tokens):
            raise SyntaxError(f"unexpected token: {self.peek()}")
        self.variables[name] = value
        return name, value

    def expression(self) -> int:
        value = self.term()
        while self.peek() in {"+", "-"}:
            operator = self.take()
            right = self.term()
            value = value + right if operator == "+" else value - right
        return value

    def term(self) -> int:
        value = self.factor()
        while self.peek() == "*":
            self.take()
            value *= self.factor()
        return value

    def factor(self) -> int:
        token = self.take()
        if token == "-":
            return -self.factor()
        if token == "(":
            value = self.expression()
            self.expect(")")
            return value
        if token.isdigit():
            return int(token)
        if token.isidentifier():
            if token not in self.variables:
                raise NameError(token)
            return self.variables[token]
        raise SyntaxError(f"expected value, got {token!r}")

    def peek(self) -> str | None:
        return self.tokens[self.position] if self.position < len(self.tokens) else None

    def take(self) -> str:
        token = self.peek()
        if token is None:
            raise SyntaxError("unexpected end of line")
        self.position += 1
        return token

    def expect(self, expected: str) -> None:
        actual = self.take()
        if actual != expected:
            raise SyntaxError(f"expected {expected!r}, got {actual!r}")


def main() -> None:
    interpreter = Interpreter()
    lines = (ROOT / "input" / "program.txt").read_text(encoding="utf-8").splitlines()
    for line in lines:
        if line.strip():
            name, value = interpreter.execute(line)
            print(f"{name} = {value}")


if __name__ == "__main__":
    main()
