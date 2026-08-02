"""用途：递归输出目录树，并统计扩展名、文件数和总大小。
示例输入：input/project 下的 data、src 和 README.md。
示例输出：缩进树、各扩展名数量、total files 与 total bytes。
复杂度：O(F log F)，排序成本取决于每个目录的条目数。
陷阱：符号链接可能形成循环；本例不跟随目录符号链接，并忽略指定目录名。
"""

from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def build_tree(
    root: Path,
    ignored: set[str],
) -> tuple[list[str], Counter[str], int, int]:
    lines = [root.name + "/"]
    extensions: Counter[str] = Counter()
    file_count = 0
    total_bytes = 0

    def visit(directory: Path, indent: str) -> None:
        nonlocal file_count, total_bytes
        entries = [
            path
            for path in directory.iterdir()
            if path.name not in ignored
        ]
        entries.sort(key=lambda path: (not path.is_dir(), path.name.casefold()))

        for path in entries:
            if path.is_dir() and not path.is_symlink():
                lines.append(f"{indent}{path.name}/")
                visit(path, indent + "  ")
            elif path.is_file():
                size = path.stat().st_size
                lines.append(f"{indent}{path.name} ({size} B)")
                extensions[path.suffix.casefold() or "<none>"] += 1
                file_count += 1
                total_bytes += size

    visit(root, "  ")
    return lines, extensions, file_count, total_bytes


def main() -> None:
    lines, extensions, count, total = build_tree(
        ROOT / "input" / "project",
        {".cache", ".git", "__pycache__"},
    )
    print(*lines, sep="\n")
    print("extensions:")
    for suffix in sorted(extensions):
        print(suffix, extensions[suffix])
    print("total files:", count)
    print("total bytes:", total)


if __name__ == "__main__":
    main()
