"""用 ``tempfile`` 创建会自动清理的测试目录和文件。

示例输入：在临时目录写入 ``input.txt``，内容为 3 行整数。
示例输出：读取到 [10,20,30]；退出上下文后目录不存在。
复杂度：读写 O(文件大小)；清理成本与临时目录内容量相关。
常见陷阱：Windows 上仍打开的文件可能阻止删除；应先关闭文件再重开。
"""

from pathlib import Path
from tempfile import TemporaryDirectory


def read_numbers(path: Path) -> list[int]:
    return [int(line) for line in path.read_text(encoding="utf-8").splitlines()]


def main() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        input_path = root / "input.txt"
        input_path.write_text("10\n20\n30\n", encoding="utf-8")
        print("numbers:", read_numbers(input_path))
        print("exists inside:", root.exists())
    print("exists after:", root.exists())


if __name__ == "__main__":
    main()
