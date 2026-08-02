"""用途：在输出目录中保留输入文件的相对子目录结构。

示例输入：输入 ``region/a.txt``，输出根目录为 results。
示例输出：目标相对路径 ``region/a.out.txt``。
复杂度：路径计算 O(路径长度)，创建目录取决于目录深度。
常见陷阱：先确认 input_path 位于 input_root；``relative_to`` 否则会 ValueError。
"""

from pathlib import Path
import tempfile


def mirrored_output_path(
    input_path: Path,
    input_root: Path,
    output_root: Path,
) -> Path:
    relative = input_path.resolve().relative_to(input_root.resolve())
    target = output_root / relative
    return target.with_name(f"{target.stem}.out{target.suffix}")


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        input_root = base / "input"
        output_root = base / "results"
        source = input_root / "region" / "a.txt"
        source.parent.mkdir(parents=True)
        source.write_text("42", encoding="utf-8")

        target = mirrored_output_path(source, input_root, output_root)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("answer=42\n", encoding="utf-8")
        print(target.relative_to(output_root).as_posix())


if __name__ == "__main__":
    main()
