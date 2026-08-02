"""用途：用 enumerate 取得下标，用 zip 同时遍历多个可迭代对象。
示例输入：names=[A,B,C]，scores=[90,80]。
示例输出：从 1 开始的下标；zip 只产生 (A,90)、(B,80)。
复杂度：遍历 O(min(n,m))，额外空间 O(1)（不转 list 时）。
常见陷阱：zip 默认在最短输入结束；需检查等长时用 zip(..., strict=True)（Python 3.10+）。
"""


def main() -> None:
    names = ["A", "B", "C"]
    scores = [90, 80]

    for rank, name in enumerate(names, start=1):
        print(rank, name)

    for name, score in zip(names, scores):
        print(name, score)

    try:
        list(zip(names, scores, strict=True))
    except ValueError as error:
        print("length mismatch:", type(error).__name__)


if __name__ == "__main__":
    main()
