"""用途：显式控制 UTF-8 编码和跨平台文本换行。

示例输入：``東京\\r\\n大学\\r\\n``。
示例输出：读取后打印 ``['東京', '大学']``，写出的原始字节使用 LF。
复杂度：规范化和读写均为 O(文本长度)。
常见陷阱：Windows 默认编码并非始终 UTF-8；字节模式不会自动转换换行。
"""

from pathlib import Path
import tempfile


def normalize_to_lf(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "utf8.txt"
        text = normalize_to_lf("東京\r\n大学\r\n")
        path.write_text(text, encoding="utf-8", newline="\n")
        loaded = path.read_text(encoding="utf-8")
        raw = path.read_bytes()
        print(loaded.splitlines())
        print("LF bytes:", raw.count(b"\n"), "CR bytes:", raw.count(b"\r"))


if __name__ == "__main__":
    main()
