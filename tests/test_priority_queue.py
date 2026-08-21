import unittest

from utils import PriorityQueue


class PriorityQueueTests(unittest.TestCase):
    def test_empty_queue_can_be_created_without_inferring_from_an_empty_tuple(self):
        queue = PriorityQueue(key=lambda item: item["priority"])
        queued = {"priority": 1, "value": "ready"}
        queue.push(queued)

        self.assertIs(queue.pop(), queued)

        typed = PriorityQueue[str](None)
        typed.push("ready")
        self.assertEqual(typed.pop(), "ready")

    def test_min_queue_accepts_initial_items_and_supports_peek(self):
        queue = PriorityQueue([5, 1, 3])

        self.assertEqual(queue.peek(), 1)
        self.assertEqual(len(queue), 3)
        self.assertEqual([queue.pop(), queue.pop(), queue.pop()], [1, 3, 5])
        self.assertFalse(queue)

    def test_reverse_queue_returns_largest_priority_first(self):
        queue = PriorityQueue([5, 1, 3], reverse=True)
        queue.push(8)

        self.assertEqual([queue.pop(), queue.pop()], [8, 5])

        stable = PriorityQueue(key=lambda item: item[0], reverse=True)
        stable.push((2, "first"))
        stable.push((2, "second"))
        self.assertEqual(stable.pop(), (2, "first"))
        self.assertEqual(stable.pop(), (2, "second"))

    def test_key_keeps_equal_priorities_stable_without_comparing_items(self):
        first = {"name": "first", "priority": 1}
        second = {"name": "second", "priority": 1}
        later = {"name": "later", "priority": 2}
        queue = PriorityQueue(
            [first, second, later],
            key=lambda item: item["priority"],
        )

        self.assertIs(queue.pop(), first)
        self.assertIs(queue.pop(), second)
        self.assertIs(queue.pop(), later)

    def test_explicit_priority_and_priority_aware_operations(self):
        queue = PriorityQueue[str]()
        queue.push("low", priority=10)
        queue.push("high", priority=1)

        self.assertEqual(queue.peek_with_priority(), (1, "high"))
        self.assertEqual(queue.pop_with_priority(), (1, "high"))
        self.assertEqual(queue.pop_with_priority(), (10, "low"))

    def test_clear_resets_queue_and_empty_operations_raise(self):
        queue = PriorityQueue([2, 1])
        queue.clear()

        self.assertFalse(queue)
        for operation in (
            queue.peek,
            queue.peek_with_priority,
            queue.pop,
            queue.pop_with_priority,
        ):
            with self.subTest(operation=operation.__name__):
                with self.assertRaises(IndexError):
                    operation()

    def test_rejects_invalid_configuration(self):
        with self.assertRaises(TypeError):
            PriorityQueue(key=1)
        with self.assertRaises(TypeError):
            PriorityQueue(reverse=1)
