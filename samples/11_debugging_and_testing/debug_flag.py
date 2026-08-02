"""用命令行 ``--debug`` 开关控制调试输出。

示例输入：``python debug_flag.py --debug``。
示例输出：stderr 显示每步累计值，stdout 显示 ``sum: 10``。
复杂度：求和 O(n)；关闭调试时仅有一次布尔判断/循环。
常见陷阱：不要把调试文字混入需要精确复制或比较的正式输出。
"""

import argparse
import sys


def running_sum(values: list[int], debug: bool = False) -> int:
    total = 0
    for index, value in enumerate(values):
        total += value
        if debug:
            print(f"[DEBUG] i={index} value={value} total={total}", file=sys.stderr)
    return total


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    print("sum:", running_sum([1, 2, 3, 4], args.debug))


if __name__ == "__main__":
    main()
