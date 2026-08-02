import unittest

from utils import BatchIO, DSU


class BatchIOAnswerTests(unittest.TestCase):
    def test_selects_answer_without_running_later_code(self):
        events = []

        def answers():
            events.append("first")
            yield [1, 2, 3]
            events.append("second")
            yield (4, 5)
            events.append("must not run")
            yield 6

        runner = BatchIO(".", answer_index=2)

        self.assertEqual(runner._format_result(answers()), "(4, 5)")
        self.assertEqual(events, ["first", "second"])

    def test_answer_requires_iterator(self):
        runner = BatchIO(".", answer_index=1)

        with self.assertRaisesRegex(TypeError, "迭代器或生成器"):
            runner._format_result([1, 2, 3])

    def test_reports_missing_answer(self):
        runner = BatchIO(".", answer_index=2)

        with self.assertRaisesRegex(IndexError, "第 2 个答案"):
            runner._format_result(iter(["only"]))

    def test_rejects_non_positive_answer_index(self):
        with self.assertRaises(ValueError):
            BatchIO(".", answer_index=0)


class DSUTests(unittest.TestCase):
    def test_find_fully_compresses_path(self):
        dsu = DSU(6)
        dsu.parent[:] = [0, 0, 1, 2, 3, 4]

        self.assertEqual(dsu.find(5), 0)
        self.assertEqual(dsu.parent, [0, 0, 0, 0, 0, 0])

    def test_union_size_and_component_count(self):
        dsu = DSU(5)

        self.assertTrue(dsu.union(0, 1))
        self.assertTrue(dsu.union(1, 2))
        self.assertFalse(dsu.union(0, 2))
        self.assertTrue(dsu.same(0, 2))
        self.assertFalse(dsu.same(0, 3))
        self.assertEqual(dsu.size(1), 3)
        self.assertEqual(dsu.components, 3)

    def test_empty_dsu(self):
        dsu = DSU(0)

        self.assertEqual(dsu.components, 0)
        self.assertEqual(dsu.parent, [])

    def test_rejects_negative_size(self):
        with self.assertRaises(ValueError):
            DSU(-1)


if __name__ == "__main__":
    unittest.main()
