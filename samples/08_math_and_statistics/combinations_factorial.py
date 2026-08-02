"""阶乘、排列数和组合数的标准库写法。

示例输入：从 5 个互异元素中选择或排列 2 个。
示例输出：C(5,2)=10、P(5,2)=20、5!=120。
复杂度：整数运算成本随结果位数增长；不要把这些调用笼统视为严格 O(1)。
常见陷阱：``comb`` 不取模；大规模取模组合数通常要预处理阶乘与逆元。
"""

from math import comb, factorial, perm


def binomial_row(n: int) -> list[int]:
    """返回二项式系数第 n 行。"""
    return [comb(n, k) for k in range(n + 1)]


def main() -> None:
    n, r = 5, 2
    print("factorial:", factorial(n))
    print("combination:", comb(n, r))
    print("permutation:", perm(n, r))
    print("row 5:", binomial_row(5))
    print("all permutations:", perm(n))  # 等同于 n!


if __name__ == "__main__":
    main()
