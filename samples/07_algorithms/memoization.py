"""用途：用 functools.cache 记忆化自顶向下动态规划。
示例输入：计算 fib(10)。
示例输出：55，并显示每个状态只真正计算一次的缓存统计。
复杂度：fib(n) 因缓存变为 O(n) 时间、O(n) 缓存与递归栈。
常见陷阱：参数必须可哈希；缓存跨调用保留；递归仍受深度限制，超大 n 改迭代。
"""

from functools import cache


@cache
def fibonacci(number: int) -> int:
    if number < 0:
        raise ValueError("number 不能为负")
    if number < 2:
        return number
    return fibonacci(number - 1) + fibonacci(number - 2)


def main() -> None:
    fibonacci.cache_clear()
    print("fib(10):", fibonacci(10))
    print("cache:", fibonacci.cache_info())
    print("fib(9):", fibonacci(9))
    print("cache after reuse:", fibonacci.cache_info())


if __name__ == "__main__":
    main()
