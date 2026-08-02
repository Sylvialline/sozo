"""用途：对比 map/filter 与通常更易读的推导式写法。
示例输入：字符串 ["1","-2","3","0"]。
示例输出：整数 [1,-2,3,0]、正数平方 [1,9]。
复杂度：完整遍历 O(n)；map/filter 本身惰性，转 list 后占 O(n)。
常见陷阱：Python 3 的 map/filter 返回一次性迭代器，不是 list；复杂 lambda 可读性差。
"""


def main() -> None:
    tokens = ["1", "-2", "3", "0"]
    mapped = map(int, tokens)
    numbers = list(mapped)
    print("numbers:", numbers)
    print("map exhausted:", list(mapped))

    positives = filter(lambda x: x > 0, numbers)
    print("positive squares with map/filter:", list(map(lambda x: x * x, positives)))
    print("same with comprehension:", [x * x for x in numbers if x > 0])


if __name__ == "__main__":
    main()
