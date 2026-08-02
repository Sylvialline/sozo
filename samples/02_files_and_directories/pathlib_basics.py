"""用途：速查 pathlib 的路径拼接、属性、创建、读写和存在性检查。

示例输入：临时目录下的 ``data/input.txt``。
示例输出：打印文件名、stem、suffix、父目录和文本 ``42``。
复杂度：路径运算 O(路径长度)，文件读写 O(文件大小)。
常见陷阱：相对路径基于当前工作目录；不要手写 Windows 反斜杠。
"""

from pathlib import Path
import tempfile


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        path = root / "data" / "input.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("42\n", encoding="utf-8")

        print("name/stem/suffix:", path.name, path.stem, path.suffix)
        print("parent:", path.parent.name)
        print("exists/file/dir:", path.exists(), path.is_file(), path.parent.is_dir())
        print("content:", path.read_text(encoding="utf-8").strip())


if __name__ == "__main__":
    main()
