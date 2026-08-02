"""批量读取 ``.in``/``.out`` 文件并对同一个函数做回归测试。

示例输入：临时生成 case1.in/case1.out 与一个故意错误的 case2.out。
示例输出：case1 PASS、case2 FAIL、summary: 1/2 passed，并打印 diff。
复杂度：O(所有输入和输出的总字符数 + solve 成本)。
常见陷阱：自然排序与字典序不同；失败时必须同时打印文件名和可读差异。
"""

from collections.abc import Callable
from difflib import unified_diff
from pathlib import Path
import re
from tempfile import TemporaryDirectory


def natural_key(path: Path) -> list[int | str]:
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", path.name)
    ]


def run_cases(directory: Path, solver: Callable[[str], str]) -> tuple[int, int]:
    input_paths = sorted(directory.glob("*.in"), key=natural_key)
    passed = 0
    for input_path in input_paths:
        expected_path = input_path.with_suffix(".out")
        if not expected_path.exists():
            print(input_path.name, "MISSING EXPECTED")
            continue
        actual = solver(input_path.read_text(encoding="utf-8"))
        expected = expected_path.read_text(encoding="utf-8")
        if actual == expected:
            passed += 1
            print(input_path.name, "PASS")
        else:
            print(input_path.name, "FAIL")
            print(
                "".join(
                    unified_diff(
                        expected.splitlines(keepends=True),
                        actual.splitlines(keepends=True),
                        fromfile=expected_path.name,
                        tofile="actual",
                    )
                ),
                end="",
            )
    return passed, len(input_paths)


def sum_solver(text: str) -> str:
    return f"{sum(map(int, text.split()))}\n"


def main() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "case1.in").write_text("1 2 3\n", encoding="utf-8")
        (root / "case1.out").write_text("6\n", encoding="utf-8")
        (root / "case2.in").write_text("10 20\n", encoding="utf-8")
        (root / "case2.out").write_text("31\n", encoding="utf-8")
        passed, total = run_cases(root, sum_solver)
        print(f"summary: {passed}/{total} passed")


if __name__ == "__main__":
    main()
