"""用途：逐文件处理并记录成功/失败，使一个坏文件不影响其余文件。

示例输入：good1.txt=``10``、bad.txt=``oops``、good2.txt=``20``。
示例输出：两个 OK、一个 ERROR，最后 ``success=2 failure=1``。
复杂度：O(文件总大小 + n log n)；结果列表 O(n)。
常见陷阱：不要用裸 ``except``；错误消息必须包含文件名和异常类型。
"""

from dataclasses import dataclass
from pathlib import Path
import tempfile


@dataclass(frozen=True)
class Result:
    path: Path
    value: int | None
    error: Exception | None


def process_directory(root: Path) -> list[Result]:
    results: list[Result] = []
    for path in sorted(root.glob("*.txt"), key=lambda item: item.name.casefold()):
        try:
            value = int(path.read_text(encoding="utf-8").strip())
        except (OSError, UnicodeError, ValueError) as error:
            results.append(Result(path, None, error))
        else:
            results.append(Result(path, value * 2, None))
    return results


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        for name, text in (("good1.txt", "10"), ("bad.txt", "oops"), ("good2.txt", "20")):
            (root / name).write_text(text, encoding="utf-8")

        results = process_directory(root)
        for result in results:
            if result.error is None:
                print(f"OK {result.path.name}: {result.value}")
            else:
                print(f"ERROR {result.path.name}: {type(result.error).__name__}")
        success = sum(result.error is None for result in results)
        print(f"success={success} failure={len(results) - success}")


if __name__ == "__main__":
    main()
