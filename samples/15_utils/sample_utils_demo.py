"""用途：组合演示 15_utils 中的筛选、解析、自然排序和计时工具。
示例输入：["case10.txt", "case2.txt"] 与 "x=10, y=-3"。
示例输出：自然排序后的文件名和解析出的整数。
复杂度：排序 O(n log n)，解析 O(文本长度)。
陷阱：本文件依赖同目录模块；应直接运行本文件或把该目录加入 sys.path。
"""

from pathlib import Path

from file_filters import filter_paths
from natural_sort import natural_key
from parsing import integers
from timing import Timer


def main() -> None:
    paths = [Path("case10.txt"), Path("note.md"), Path("case2.txt")]
    with Timer("filter + sort"):
        selected = filter_paths(paths, suffixes={".txt"}, substring="case")
        selected.sort(key=natural_key)

    print([path.name for path in selected])
    print(integers("x=10, y=-3"))


if __name__ == "__main__":
    main()
