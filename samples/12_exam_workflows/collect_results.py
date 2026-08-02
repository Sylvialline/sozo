"""用途：收集多文件结果，并写成一个带文件名标题的总输出。
示例输入：{"a.txt": "10", "b.txt": "20"}
示例输出：[a.txt]\\n10\\n\\n[b.txt]\\n20
复杂度：O(结果总长度)。
陷阱：dict 保持插入顺序但不自动排序；需要固定顺序时显式 sorted。
"""

import tempfile
from pathlib import Path


def merge(results: dict[str, str]) -> str:
    return "\n\n".join(f"[{name}]\n{results[name]}" for name in sorted(results))


def main() -> None:
    text = merge({"b.txt": "20", "a.txt": "10"})
    with tempfile.TemporaryDirectory() as temporary:
        output = Path(temporary) / "all_results.txt"
        output.write_text(text, encoding="utf-8")
        print(output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
