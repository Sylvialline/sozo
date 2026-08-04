import json
import time
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from utils import AnswerBook, BatchIO, DSU, read_data


class AnswerBookTests(unittest.TestCase):
    @staticmethod
    def _make_book(root: Path, timeout=None, show_log=False):
        caller_path = root / "caller.py"
        namespace = {}
        source = (
            "from utils import AnswerBook\n"
            "\n"
            "def make(timeout=None, show_log=False):\n"
            "    return AnswerBook(timeout=timeout, show_log=show_log)\n"
        )
        exec(compile(source, str(caller_path), "exec"), namespace)
        return namespace["make"](timeout, show_log)

    def test_runs_task_and_adds_elapsed_time(self):
        with TemporaryDirectory() as temp_dir:
            book = self._make_book(Path(temp_dir))
            result = {"value": 42}

            with patch(
                "utils.answer_book.perf_counter",
                side_effect=[10.0, 10.25],
            ):
                answer = book.run("1.a", lambda: result)

            self.assertEqual(answer, {"value": 42, "time": 0.25})
            self.assertEqual(book.as_dict(), {"1.a": answer})
            self.assertNotIn("time", result)

    def test_wraps_non_mapping_results(self):
        with TemporaryDirectory() as temp_dir:
            book = self._make_book(Path(temp_dir))

            with patch(
                "utils.answer_book.perf_counter",
                side_effect=[5.0, 5.5],
            ):
                answer = book.run("scalar", lambda: 7)

            self.assertEqual(answer, {"result": 7, "time": 0.5})

    def test_rejects_duplicate_labels_without_running_task(self):
        with TemporaryDirectory() as temp_dir:
            book = self._make_book(Path(temp_dir))
            book.run("same", lambda: {})
            called = False

            def task():
                nonlocal called
                called = True
                return {}

            with self.assertRaisesRegex(KeyError, "答案编号重复"):
                book.run("same", task)

            self.assertFalse(called)

    def test_class_timeout_is_stored_as_answer(self):
        with TemporaryDirectory() as temp_dir:
            book = self._make_book(Path(temp_dir), timeout=0.05)

            answer = book.run("slow", time.sleep, 1)

            self.assertTrue(answer["timeout"])
            self.assertGreaterEqual(answer["time"], 0.05)
            self.assertEqual(answer["timeout_limit"], 0.05)
            self.assertEqual(book.answers, {"slow": answer})

    def test_task_timeout_overrides_class_timeout(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            book = self._make_book(root, timeout=0.01)
            answer = book.run("allowed", dict, timeout=2)
            self.assertGreaterEqual(answer["time"], 0)
            self.assertLess(answer["time"], 2)

            book = self._make_book(root, timeout=2)
            answer = book.run("limited", time.sleep, 1, timeout=0.05)
            self.assertTrue(answer["timeout"])
            self.assertEqual(answer["timeout_limit"], 0.05)

    def test_propagates_picklable_task_exception(self):
        with TemporaryDirectory() as temp_dir:
            book = self._make_book(Path(temp_dir), timeout=2)

            with self.assertRaisesRegex(ValueError, "invalid literal"):
                book.run("bad", int, "not-an-integer")

            self.assertEqual(book.answers, {})

    def test_logs_start_done_timeout_and_failure(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            stream = StringIO()

            book = self._make_book(root, show_log=True)
            with redirect_stderr(stream):
                book.run("done", dict)

            book = self._make_book(root, timeout=0.05, show_log=True)
            with redirect_stderr(stream):
                book.run("slow", time.sleep, 1)
                with self.assertRaises(ValueError):
                    book.run("bad", int, "not-an-integer", timeout=None)

            log = stream.getvalue()
            self.assertIn("[START] done: 开始执行", log)
            self.assertIn("[DONE] done: 完成", log)
            self.assertIn("[TIMEOUT] slow:", log)
            self.assertIn("[FAILED] bad: ValueError:", log)

    def test_explicit_none_disables_class_timeout(self):
        with TemporaryDirectory() as temp_dir:
            book = self._make_book(Path(temp_dir), timeout=1)

            with patch(
                "utils.answer_book.perf_counter",
                side_effect=[30.0, 35.0],
            ):
                answer = book.run("unlimited", lambda: {}, timeout=None)

            self.assertEqual(answer["time"], 5.0)

    def test_writes_to_caller_sibling_output_by_default(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            book = self._make_book(root)
            book.run("1.a", lambda: {"value": "答案"})

            output_path = book.write_json()

            self.assertEqual(output_path, (root / "output.txt").resolve())
            self.assertEqual(
                json.loads(output_path.read_text(encoding="utf-8")),
                book.answers,
            )


class ReadDataTests(unittest.TestCase):
    @staticmethod
    def _make_caller(root: Path):
        caller_path = root / "caller.py"
        namespace = {}
        source = (
            "from utils import read_data\n"
            "\n"
            "def load(name):\n"
            "    return read_data(name)\n"
        )
        exec(compile(source, str(caller_path), "exec"), namespace)
        return namespace["load"]

    def test_returns_string_for_one_match(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data_dir = root / "data"
            data_dir.mkdir()
            (data_dir / "case-a.txt").write_text(
                "one\n二\n", encoding="utf-8"
            )
            (data_dir / "other.txt").write_text("other", encoding="utf-8")

            load = self._make_caller(root)

            self.assertEqual(load("case-"), "one\n二\n")

    def test_returns_sorted_filename_mapping_for_multiple_matches(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data_dir = root / "data"
            data_dir.mkdir()
            (data_dir / "part-b.txt").write_text("B", encoding="utf-8")
            (data_dir / "part-a.txt").write_text("A", encoding="utf-8")
            (data_dir / "part-dir").mkdir()

            load = self._make_caller(root)

            self.assertEqual(
                load("part"),
                {"part-a.txt": "A", "part-b.txt": "B"},
            )

    def test_returns_none_for_no_match_or_missing_data_directory(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            load = self._make_caller(root)

            self.assertIsNone(load("anything"))

            (root / "data").mkdir()
            (root / "data" / "input.txt").write_text(
                "input", encoding="utf-8"
            )
            self.assertIsNone(load("missing"))


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
