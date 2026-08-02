"""把调试信息写到 stderr，保持正式答案 stdout 干净。

示例输入：数字 [3,1,4]。
示例输出：stdout 为 ``answer: 8``；stderr 为带 ``[DEBUG]`` 的中间信息。
复杂度：求和 O(n)，打印成本与输出长度线性相关。
常见陷阱：stdout/stderr 缓冲策略不同，合并显示时先后顺序不一定等于调用顺序。
"""

import sys


def debug(*values: object) -> None:
    print("[DEBUG]", *values, file=sys.stderr, flush=True)


def main() -> None:
    values = [3, 1, 4]
    debug("values =", values)
    answer = sum(values)
    debug("count =", len(values), "answer =", answer)
    print("answer:", answer)


if __name__ == "__main__":
    main()
