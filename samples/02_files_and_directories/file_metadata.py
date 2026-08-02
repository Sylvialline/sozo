"""用途：读取文件大小、修改时间和扩展名等元数据。

示例输入：一个内容为 ``hello`` 的 sample.txt。
示例输出：打印 ``name=sample.txt bytes=5 suffix=.txt`` 及本地修改时间。
复杂度：单文件 stat 通常 O(1)；批量 n 个文件为 O(n) 次系统调用。
常见陷阱：文件可能在扫描后被删除；时间戳精度和语义因文件系统而异。
"""

from datetime import datetime
from pathlib import Path
import tempfile


def describe(path: Path) -> dict[str, object]:
    stat = path.stat()
    return {
        "name": path.name,
        "bytes": stat.st_size,
        "suffix": path.suffix,
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
    }


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "sample.txt"
        path.write_bytes(b"hello")
        info = describe(path)
        print(
            f"name={info['name']} bytes={info['bytes']} suffix={info['suffix']} "
            f"modified={info['modified']}"
        )


if __name__ == "__main__":
    main()
