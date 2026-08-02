"""用途：逐行读写 JSON Lines（JSONL），适合大量独立记录。
示例输入：每行一个对象：{"id":1,"value":4} 等。
示例输出：value >= 5 的对象，并再次编码为一行一个 JSON。
复杂度：流式处理 O(字符总数)，若用生成器额外空间 O(单条记录)。
常见陷阱：JSONL 不是一个 JSON 数组；空行要显式跳过或报错。
"""

import json
from collections.abc import Iterable, Iterator


def read_jsonl(lines: Iterable[str]) -> Iterator[dict[str, object]]:
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"第 {line_number} 行不是合法 JSON") from error


def write_jsonl(records: Iterable[dict[str, object]]) -> str:
    return "\n".join(json.dumps(row, ensure_ascii=False) for row in records) + "\n"


def main() -> None:
    lines = ['{"id":1,"value":4}\n', '{"id":2,"value":7}\n', "\n"]
    selected = [row for row in read_jsonl(lines) if int(row["value"]) >= 5]
    print(write_jsonl(selected), end="")


if __name__ == "__main__":
    main()
