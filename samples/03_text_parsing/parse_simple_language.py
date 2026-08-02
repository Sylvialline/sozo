"""用途：用 tokenizer + 递归下降解析含 +、-、* 和括号的整数表达式。

示例输入：``"2 + 3 * (4 - 1)"``。
示例输出：``11``。
复杂度：每个 token 读取常数次，时间 O(n)；空间 O(括号嵌套深度)。
常见陷阱：不要用 eval 处理不可信输入；极深括号可能触发 Python 递归限制。
"""

from dataclasses import dataclass
import re


TOKEN_PATTERN = re.compile(r"\s*(?:(\d+)|(.))")


def tokenize(text: str) -> list[int | str]:
    tokens: list[int | str] = []
    position = 0
    while position < len(text):
        if text[position:].isspace():
            break
        match = TOKEN_PATTERN.match(text, position)
        if match is None:
            raise ValueError(f"位置 {position} 无法解析")
        number, symbol = match.groups()
        position = match.end()
        if number is not None:
            tokens.append(int(number))
        elif symbol in "+-*()":
            tokens.append(symbol)
        else:
            raise ValueError(f"非法字符：{symbol!r}")
    return tokens


@dataclass
class Parser:
    tokens: list[int | str]
    index: int = 0

    def peek(self) -> int | str | None:
        return self.tokens[self.index] if self.index < len(self.tokens) else None

    def take(self) -> int | str:
        token = self.peek()
        if token is None:
            raise ValueError("表达式意外结束")
        self.index += 1
        return token

    def expression(self) -> int:
        value = self.term()
        while self.peek() in ("+", "-"):
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
        if isinstance(token, int):
            return token
        if token == "-":
            return -self.factor()
        if token == "(":
            value = self.expression()
            if self.take() != ")":
                raise ValueError("缺少右括号")
            return value
        raise ValueError(f"不应出现的 token：{token!r}")


def evaluate(text: str) -> int:
    parser = Parser(tokenize(text))
    value = parser.expression()
    if parser.peek() is not None:
        raise ValueError(f"末尾有多余 token：{parser.peek()!r}")
    return value


def main() -> None:
    expression = "2 + 3 * (4 - 1)"
    print(evaluate(expression))


if __name__ == "__main__":
    main()
