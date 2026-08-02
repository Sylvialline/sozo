"""用 ``pathlib`` 从文件读取整数网格或字符网格。

示例输入：整数文件 ``1 2 3\\n4 5 6``、字符文件 ``.#.\\n###``。
示例输出：[[1,2,3],[4,5,6]] 与 [['.','#','.'],['#','#','#']]。
复杂度：读取和解析均为 O(文件字符数)。
常见陷阱：相对路径基于当前工作目录；网格不等宽时应立即报错。
"""

from pathlib import Path
from tempfile import TemporaryDirectory


def _validate_rectangular(grid: list[list[object]]) -> None:
    if grid and any(len(row) != len(grid[0]) for row in grid):
        raise ValueError("ragged grid")


def read_integer_grid(path: Path) -> list[list[int]]:
    grid = [
        [int(token) for token in line.split()]
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    _validate_rectangular(grid)
    return grid


def read_character_grid(path: Path) -> list[list[str]]:
    grid = [
        list(line.rstrip("\r\n"))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    _validate_rectangular(grid)
    return grid


def main() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        number_path = root / "numbers.txt"
        character_path = root / "grid.txt"
        number_path.write_text("1 2 3\n4 5 6\n", encoding="utf-8")
        character_path.write_text(".#.\n###\n", encoding="utf-8")
        print("integers:", read_integer_grid(number_path))
        print("characters:", read_character_grid(character_path))


if __name__ == "__main__":
    main()
