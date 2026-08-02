"""用途：正则解析日志，并按等级和用户汇总。
示例输入：[2026-08-01 09:00:00] INFO user=alice message=login
示例输出：LEVEL INFO 2；USER alice 3。
复杂度：O(日志总长度 + K log K)。
陷阱：真实日志可能含空格和缺失字段；正则必须锚定并对坏行明确报错。
"""

import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LINE = re.compile(
    r"^\[(?P<time>[^\]]+)\] (?P<level>[A-Z]+) "
    r"user=(?P<user>\w+) message=(?P<message>.*)$"
)


@dataclass(frozen=True)
class Record:
    time: datetime
    level: str
    user: str
    message: str


def parse_line(line: str) -> Record:
    match = LINE.fullmatch(line)
    if match is None:
        raise ValueError(f"bad log line: {line!r}")
    return Record(
        datetime.fromisoformat(match["time"]),
        match["level"],
        match["user"],
        match["message"],
    )


def main() -> None:
    records = [
        parse_line(line)
        for line in (ROOT / "input" / "events.log")
        .read_text(encoding="utf-8")
        .splitlines()
        if line
    ]
    levels = Counter(record.level for record in records)
    users = Counter(record.user for record in records)

    for level in sorted(levels):
        print("LEVEL", level, levels[level])
    for user in sorted(users):
        print("USER", user, users[user])


if __name__ == "__main__":
    main()
