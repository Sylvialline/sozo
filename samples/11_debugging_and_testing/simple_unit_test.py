"""标准库 ``unittest`` 的最小测试文件，可直接运行。

示例输入：为 ``normalize`` 提供普通、空白和空列表用例。
示例输出：3 个测试均显示 ``ok``，最后输出 ``successful: True``。
复杂度：每个测试处理 n 个数为 O(n)。
常见陷阱：浮点结果用 ``assertAlmostEqual``；测试之间不应共享可变状态。
"""

import unittest


def normalize(values: list[float]) -> list[float]:
    if not values:
        return []
    total = sum(values)
    if total == 0:
        raise ValueError("sum must not be zero")
    return [value / total for value in values]


class NormalizeTests(unittest.TestCase):
    def test_regular_values(self) -> None:
        result = normalize([1, 1, 2])
        self.assertEqual(len(result), 3)
        self.assertAlmostEqual(sum(result), 1.0)
        self.assertEqual(result, [0.25, 0.25, 0.5])

    def test_empty(self) -> None:
        self.assertEqual(normalize([]), [])

    def test_zero_sum_rejected(self) -> None:
        with self.assertRaises(ValueError):
            normalize([-1, 1])


def main() -> None:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(NormalizeTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("successful:", result.wasSuccessful())


if __name__ == "__main__":
    main()
