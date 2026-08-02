"""用途：批处理时记录单文件异常，并选择继续或停止。
示例输入：["10", "bad", "20"]
示例输出：成功 10；ERROR ValueError；成功 20
复杂度：O(文件数 + 求解成本)。
陷阱：不要用裸 except；至少打印文件名和异常类型，调试时再输出 traceback。
"""

import traceback


def process(values: list[str], *, keep_going: bool, debug: bool) -> None:
    for index, text in enumerate(values, 1):
        try:
            print(f"case{index}: {int(text)}")
        except ValueError as error:
            print(f"case{index}: {type(error).__name__}: {error}")
            if debug:
                traceback.print_exc()
            if not keep_going:
                break


def main() -> None:
    process(["10", "bad", "20"], keep_going=True, debug=False)


if __name__ == "__main__":
    main()
