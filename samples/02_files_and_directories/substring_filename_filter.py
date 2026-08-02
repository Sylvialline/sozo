"""用途：无需正则时，用普通子字符串和扩展名过滤文件。

示例输入：``trial_case.txt final_case.txt final.csv FINAL_NOTE.TXT``。
示例输出：``['FINAL_NOTE.TXT', 'final_case.txt']``。
复杂度：扫描 O(文件名总长度)，结果排序 O(k log k)。
常见陷阱：大小写规则要显式决定；``in`` 不理解正则元字符。
"""

from pathlib import Path
import tempfile


def filter_names(root: Path, needle: str, suffix: str) -> list[str]:
    folded_needle = needle.casefold()
    folded_suffix = suffix.casefold()
    return sorted(
        (
            path.name
            for path in root.iterdir()
            if path.is_file()
            and folded_needle in path.name.casefold()
            and path.suffix.casefold() == folded_suffix
        ),
        key=str.casefold,
    )


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        for name in ("trial_case.txt", "final_case.txt", "final.csv", "FINAL_NOTE.TXT"):
            (root / name).touch()
        print(filter_names(root, "final", ".txt"))


if __name__ == "__main__":
    main()
