import unittest

from utils import nth, nth_element


class SelectionTests(unittest.TestCase):
    def test_nth_element_matches_sorted_and_partitions_in_place(self):
        values = [9, 1, 7, 3, 5, 3, 8, 2]
        expected = sorted(values)

        for n, item in enumerate(expected):
            with self.subTest(n=n):
                candidate = values.copy()
                result = nth_element(candidate, n)

                self.assertEqual(result, item)
                self.assertEqual(candidate[n], item)
                self.assertTrue(all(value <= item for value in candidate[:n]))
                self.assertTrue(all(value >= item for value in candidate[n + 1 :]))
                self.assertCountEqual(candidate, values)

    def test_nth_does_not_change_input(self):
        values = [9, 1, 7, 3, 5, 3, 8, 2]
        original = values.copy()

        self.assertEqual(nth(values, 3), sorted(values)[3])
        self.assertEqual(values, original)

    def test_supports_negative_indices_and_reverse_order(self):
        values = [4, 1, 9, 2]

        self.assertEqual(nth_element(values.copy(), -1), 9)

        descending = values.copy()
        self.assertEqual(nth_element(descending, 1, reverse=True), 4)
        self.assertTrue(all(value >= 4 for value in descending[:1]))
        self.assertTrue(all(value <= 4 for value in descending[2:]))

        self.assertEqual(nth_element(values.copy(), -1, reverse=True), 1)

    def test_key_is_stable_and_called_once_per_item(self):
        calls = []
        first = {"name": "first", "score": 1}
        second = {"name": "second", "score": 1}
        third = {"name": "third", "score": 2}

        def score(item):
            calls.append(item)
            return item["score"]

        result = nth(
            (first, second, third),
            1,
            key=score,
        )

        self.assertIs(result, second)
        self.assertEqual(calls, [first, second, third])

    def test_accepts_generators(self):
        result = nth((x * x for x in range(6)), 3)

        self.assertEqual(result, 9)

    def test_rejects_invalid_index_and_options(self):
        for n in (-4, 3):
            with self.subTest(n=n):
                with self.assertRaises(IndexError):
                    nth_element([1, 2, 3], n)

        with self.assertRaises(IndexError):
            nth_element([], 0)
        with self.assertRaises(TypeError):
            nth_element([1], 0.5)
        with self.assertRaises(TypeError):
            nth_element([1], 0, key=1)
        with self.assertRaises(TypeError):
            nth_element([1], 0, reverse=1)
        with self.assertRaises(TypeError):
            nth_element((1, 2, 3), 1)
