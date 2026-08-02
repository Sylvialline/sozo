"""用途：用 bytes、BytesIO 和 struct 读写固定格式二进制整数。
示例输入：魔数 b"SOZO"，版本 2，三个有符号整数 [10, -3, 25]。
示例输出：magic=b'SOZO' version=2 values=[10, -3, 25]。
复杂度：打包/解包 n 个整数为 O(n)，缓冲区占 O(n)。
常见陷阱：必须明确字节序和宽度；"<" 表示小端，"i" 通常为 4 字节有符号整数。
"""

import struct
from io import BytesIO


HEADER = struct.Struct("<4sBH")  # magic、1 字节版本、2 字节元素数
INT32 = struct.Struct("<i")


def encode(values: list[int], version: int = 2) -> bytes:
    stream = BytesIO()
    stream.write(HEADER.pack(b"SOZO", version, len(values)))
    for value in values:
        stream.write(INT32.pack(value))
    return stream.getvalue()


def decode(data: bytes) -> tuple[bytes, int, list[int]]:
    stream = BytesIO(data)
    header = stream.read(HEADER.size)
    if len(header) != HEADER.size:
        raise ValueError("文件头不完整")
    magic, version, count = HEADER.unpack(header)
    values = []
    for _ in range(count):
        chunk = stream.read(INT32.size)
        if len(chunk) != INT32.size:
            raise ValueError("整数数据不完整")
        values.append(INT32.unpack(chunk)[0])
    return magic, version, values


def main() -> None:
    data = encode([10, -3, 25])
    magic, version, values = decode(data)
    print(f"magic={magic!r} version={version} values={values}")


if __name__ == "__main__":
    main()
