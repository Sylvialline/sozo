"""用途：区分当前工作目录与脚本目录，并定位脚本旁资源。

示例输入：无需输入。
示例输出：打印 ``cwd``、``script_dir`` 和脚本旁 ``data/input.txt`` 路径。
复杂度：路径解析通常可视为 O(路径长度)。
常见陷阱：``Path("data")`` 相对 Path.cwd()，不是相对当前 .py 文件。
"""

from pathlib import Path


def main() -> None:
    cwd = Path.cwd()
    script_dir = Path(__file__).resolve().parent
    resource = script_dir / "data" / "input.txt"
    print("cwd:", cwd)
    print("script_dir:", script_dir)
    print("script-relative resource:", resource)


if __name__ == "__main__":
    main()
