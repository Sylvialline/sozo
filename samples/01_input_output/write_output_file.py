"""用途：创建父目录并把结果安全写入 UTF-8 输出文件。

示例输入：结果行 ``["answer=42", "status=ok"]``。
示例输出：文件包含两行，并打印 ``answer=42 | status=ok``。
复杂度：时间 O(总字符数)，join 会额外构造同量级字符串。
常见陷阱：write_text 会覆盖已有文件；追加应使用 open(mode="a")。
"""

from pathlib import Path
import tempfile


def write_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        output = Path(temporary) / "results" / "answer.txt"
        write_lines(output, ["answer=42", "status=ok"])
        print(output.read_text(encoding="utf-8").strip().replace("\n", " | "))


if __name__ == "__main__":
    main()
