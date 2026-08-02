"""用途：把输入目录的相对结构镜像到输出目录。
示例输入：input/group/a.txt
示例输出：output/group/a.out
复杂度：路径计算 O(路径长度)。
陷阱：relative_to 要求输入确实位于基准目录内，否则抛 ValueError。
"""

import tempfile
from pathlib import Path


def output_path(
    input_path: Path,
    input_root: Path,
    output_root: Path,
) -> Path:
    relative = input_path.relative_to(input_root)
    return output_root / relative.with_suffix(".out")


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        source = root / "input" / "group" / "a.txt"
        source.parent.mkdir(parents=True)
        source.write_text("sample", encoding="utf-8")

        target = output_path(source, root / "input", root / "output")
        target.parent.mkdir(parents=True)
        target.write_text("answer", encoding="utf-8")
        print(target.relative_to(root).as_posix())


if __name__ == "__main__":
    main()
