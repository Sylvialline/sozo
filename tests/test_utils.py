import json
import pickle
import time
import unittest
from contextlib import redirect_stderr
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from enum import Enum
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from utils import (
    AnswerBook,
    Case,
    DSU,
    Exam,
    Graph,
    Input,
    Series,
    divisors,
    factor_pairs,
    read_data,
    read_files,
)

import utils.exam as exam_module
from utils._caller import caller_directory


def _identity_task(value):
    return value


def _parse_csv(data):
    return list(map(int, data.split(",")))


def _parse_colon(data):
    return list(map(int, data.split(":")))


def _uppercase_parser(data):
    return data.upper()


class CallerDirectoryTests(unittest.TestCase):
    def test_skips_internal_utils_frames_and_finds_external_caller(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            caller_path = root / "caller.py"
            namespace = {"caller_directory": caller_directory}
            source = (
                "def locate():\n"
                "    return caller_directory('test()')\n"
            )
            exec(compile(source, str(caller_path), "exec"), namespace)

            self.assertEqual(namespace["locate"](), root.resolve())

    def test_error_message_names_the_requesting_api(self):
        with patch("utils._caller.inspect.currentframe", return_value=None):
            with self.assertRaisesRegex(RuntimeError, r"read_data\(\)"):
                read_data("input")
            with self.assertRaisesRegex(RuntimeError, r"read_files\(\)"):
                read_files("input.txt")
            with self.assertRaisesRegex(RuntimeError, r"Exam\(\)"):
                Exam(str)
            with self.assertRaisesRegex(RuntimeError, r"AnswerBook\(\)"):
                AnswerBook()


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
            result = {"value": 42, "time": "task-owned value"}

            with patch(
                "utils.answer_book.perf_counter",
                side_effect=[10.0, 10.25],
            ):
                answer = book.run("1.a", lambda: result)

            self.assertEqual(
                answer,
                {
                    "result": {
                        "value": 42,
                        "time": "task-owned value",
                    },
                    "time": 0.25,
                },
            )
            self.assertEqual(book.as_dict(), {"1.a": answer})
            self.assertEqual(result["time"], "task-owned value")

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

            self.assertEqual(output_path, (root / "answer.json").resolve())
            self.assertEqual(
                json.loads(output_path.read_text(encoding="utf-8")),
                book.answers,
            )

    def test_pretty_json_keeps_only_simple_one_dimensional_lists_inline(self):
        with TemporaryDirectory() as temp_dir:
            book = self._make_book(Path(temp_dir))
            book.answers = {
                "case": {
                    "vector": [1, 2, "三", True, None],
                    "matrix": [[1, 2], [3, 4]],
                    "records": [{"value": 1}, {"value": 2}],
                }
            }

            output = book.dumps()

            self.assertIn(
                '"vector": [1, 2, "三", true, null]',
                output,
            )
            self.assertIn(
                '"matrix": [\n      [1, 2],\n      [3, 4]\n    ]',
                output,
            )
            self.assertIn(
                '"records": [\n      {\n        "value": 1\n      }',
                output,
            )
            self.assertEqual(json.loads(output), book.answers)

    def test_can_disable_inline_simple_lists(self):
        with TemporaryDirectory() as temp_dir:
            book = self._make_book(Path(temp_dir))
            book.answers = {"case": {"vector": [1, 2]}}

            output = book.dumps(inline_simple_lists=False)

            self.assertIn('"vector": [\n', output)
            self.assertEqual(json.loads(output), book.answers)

    def test_json_output_converts_common_non_json_types_recursively(self):
        class Status(Enum):
            DONE = "done"

        @dataclass
        class Point:
            x: int
            tags: set[str]

        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            book = self._make_book(root)
            book.answers = {
                "case": {
                    "set": {3, 1, 2},
                    "frozen": frozenset({"b", "a"}),
                    "point": Point(4, {"right", "left"}),
                    "status": Status.DONE,
                    "path": root / "result.txt",
                    "date": date(2026, 8, 20),
                    "duration": timedelta(seconds=2.5),
                    "decimal": Decimal("1.2300"),
                    "iterator": iter((5, 6)),
                }
            }

            restored = json.loads(book.dumps())

            self.assertEqual(restored["case"]["set"], [1, 2, 3])
            self.assertEqual(restored["case"]["frozen"], ["a", "b"])
            self.assertEqual(
                restored["case"]["point"],
                {"x": 4, "tags": ["left", "right"]},
            )
            self.assertEqual(restored["case"]["status"], "done")
            self.assertEqual(
                restored["case"]["path"],
                str(root / "result.txt"),
            )
            self.assertEqual(restored["case"]["date"], "2026-08-20")
            self.assertEqual(restored["case"]["duration"], 2.5)
            self.assertEqual(restored["case"]["decimal"], "1.2300")
            self.assertEqual(restored["case"]["iterator"], [5, 6])
            self.assertIsInstance(book.answers["case"]["set"], set)

    def test_json_output_supports_numpy_scalars_arrays_and_keys(self):
        try:
            import numpy as np
        except ModuleNotFoundError:
            self.skipTest("NumPy 未安装")

        with TemporaryDirectory() as temp_dir:
            book = self._make_book(Path(temp_dir))
            book.answers = {
                "case": {
                    "integer": np.int64(7),
                    "floating": np.float32(1.5),
                    "boolean": np.bool_(True),
                    "array": np.array([[1, 2], [3, 4]], dtype=np.int64),
                    "mapping": {np.int64(9): np.int64(10)},
                }
            }

            restored = json.loads(book.dumps())

            self.assertEqual(restored["case"]["integer"], 7)
            self.assertEqual(restored["case"]["floating"], 1.5)
            self.assertIs(restored["case"]["boolean"], True)
            self.assertEqual(restored["case"]["array"], [[1, 2], [3, 4]])
            self.assertEqual(restored["case"]["mapping"], {"9": 10})

    def test_json_protocol_handles_custom_objects_and_rejects_unknown_ones(self):
        class Custom:
            def __json__(self):
                return {"values": {2, 1}}

        class Unknown:
            pass

        with TemporaryDirectory() as temp_dir:
            book = self._make_book(Path(temp_dir))
            book.answers = {"case": {"custom": Custom()}}
            self.assertEqual(
                json.loads(book.dumps()),
                {"case": {"custom": {"values": [1, 2]}}},
            )

            book.answers = {"case": {"unknown": Unknown()}}
            with self.assertRaisesRegex(TypeError, "Unknown.*不能序列化"):
                book.dumps()

    def test_json_output_still_rejects_circular_references(self):
        with TemporaryDirectory() as temp_dir:
            book = self._make_book(Path(temp_dir))
            circular = []
            circular.append(circular)
            book.answers = {"case": circular}

            with self.assertRaisesRegex(ValueError, "Circular reference"):
                book.dumps()

    def test_json_output_rejects_keys_that_collapse_to_the_same_string(self):
        with TemporaryDirectory() as temp_dir:
            book = self._make_book(Path(temp_dir))
            book.answers = {"case": {1: "number", "1": "string"}}

            with self.assertRaisesRegex(ValueError, "键在转换后发生冲突"):
                book.dumps()


class ExamTests(unittest.TestCase):
    @staticmethod
    def _make_exam(root: Path, reader, **kwargs):
        caller_path = root / "caller.py"
        namespace = {}
        source = (
            "from utils import Exam\n"
            "\n"
            "def make(reader, **kwargs):\n"
            "    return Exam(reader, **kwargs)\n"
        )
        exec(compile(source, str(caller_path), "exec"), namespace)
        return namespace["make"](reader, **kwargs)

    def test_bare_task_decorator_infers_series_and_preserves_function(self):
        with TemporaryDirectory() as temp_dir:
            loaded = []

            def reader(name):
                loaded.append(name)
                return f"data:{name}"

            exam = self._make_exam(
                Path(temp_dir),
                reader,
                show_log=False,
            )

            @exam.task
            def task8(left, right):
                return [left, right]

            self.assertEqual(
                task8("left", "right"),
                ["left", "right"],
            )

            book = exam.execute(output=None)

            self.assertEqual(
                loaded,
                ["8a1", "8a2", "8b1", "8b2", "8c1", "8c2"],
            )
            self.assertEqual(list(book.answers), ["8a", "8b", "8c"])
            self.assertEqual(
                book.answers["8a"]["result"],
                ["data:8a1", "data:8a2"],
            )

    def test_configured_task_decorator_registers_explicit_case(self):
        with TemporaryDirectory() as temp_dir:
            exam = self._make_exam(
                Path(temp_dir),
                str.upper,
                show_log=False,
            )

            @exam.task(Case("custom", 4, files=("data",)))
            def solve(size, data):
                return {"value": (size, data)}

            book = exam.execute(output=None)

            self.assertEqual(
                book.answers["custom"]["result"]["value"],
                (4, "DATA"),
            )

    def test_execute_only_runs_selected_decorated_task(self):
        with TemporaryDirectory() as temp_dir:
            loaded = []

            def reader(name):
                loaded.append(name)
                return name.upper()

            exam = self._make_exam(
                Path(temp_dir),
                reader,
                show_log=False,
            )

            @exam.task(Case("one", files=("one",)))
            def task1(data):
                return data

            @exam.task(
                Case("two.a", files=("two-a",)),
                Case("two.b", files=("two-b",)),
            )
            def task2(data):
                return data

            book = exam.execute(only=task2, output=None)

            self.assertEqual(loaded, ["two-a", "two-b"])
            self.assertEqual(list(book.answers), ["two.a", "two.b"])
            self.assertEqual(book.answers["two.a"]["result"], "TWO-A")

    def test_execute_only_accepts_multiple_tasks(self):
        with TemporaryDirectory() as temp_dir:
            exam = self._make_exam(
                Path(temp_dir),
                str.upper,
                show_log=False,
            )

            @exam.task(Case("one", files=("one",)))
            def task1(data):
                return data

            @exam.task(Case("two", files=("two",)))
            def task2(data):
                return data

            @exam.task(Case("three", files=("three",)))
            def task3(data):
                return data

            book = exam.execute(only=(task1, task3), output=None)

            self.assertEqual(list(book.answers), ["one", "three"])

    def test_execute_only_rejects_unregistered_task(self):
        with TemporaryDirectory() as temp_dir:
            exam = self._make_exam(
                Path(temp_dir),
                str,
                show_log=False,
            )

            @exam.task(Case("one"))
            def task1():
                return 1

            def task2():
                return 2

            with self.assertRaisesRegex(ValueError, "未注册.*task2"):
                exam.execute(only=task2, output=None)

            book = exam.execute(only=task1, output=None)
            self.assertEqual(book.answers["one"]["result"], 1)

    def test_series_generates_labels_parameters_and_data_file_names(self):
        with TemporaryDirectory() as temp_dir:
            loaded = []

            def reader(name):
                loaded.append(name)
                return f"data:{name}"

            exam = self._make_exam(
                Path(temp_dir),
                reader,
                show_log=False,
            )
            exam.add(
                lambda size, left, right: {
                    "value": (size, left, right),
                },
                Series(
                    "3",
                    {"a": (10,), "b": (20,)},
                    input_count=2,
                    label_separator=".",
                ),
            )

            book = exam.execute(output=None)

            self.assertEqual(loaded, ["3a1", "3a2", "3b1", "3b2"])
            self.assertEqual(list(book.answers), ["3.a", "3.b"])
            self.assertEqual(
                book.answers["3.a"]["result"]["value"],
                (10, "data:3a1", "data:3a2"),
            )

    def test_case_appends_explicit_files_after_parameters(self):
        with TemporaryDirectory() as temp_dir:
            exam = self._make_exam(
                Path(temp_dir),
                lambda name: name.upper(),
                show_log=False,
            )
            exam.add(
                lambda *args: {"args": args},
                Case("4.a", 2, 4, files=("4a", "4b")),
            )

            book = exam.execute(output=None)

            self.assertEqual(
                book.answers["4.a"]["result"]["args"],
                (2, 4, "4A", "4B"),
            )

    def test_direct_read_data_reader_uses_exam_caller_and_accepts_empty_match(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data_dir = root / "data"
            data_dir.mkdir()
            (data_dir / "b.txt").write_text("B", encoding="utf-8")
            (data_dir / "a.txt").write_text("A", encoding="utf-8")

            exam = self._make_exam(root, read_data, show_log=False)
            exam.add(lambda data: data, Case("all", files=("",)))

            book = exam.execute(output=None)

            self.assertEqual(
                book.answers["all"]["result"],
                {"a.txt": "A", "b.txt": "B"},
            )

    def test_direct_read_data_reader_keeps_exam_directory_in_timeout_process(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data_dir = root / "data"
            data_dir.mkdir()
            (data_dir / "input.txt").write_text("input", encoding="utf-8")

            exam = self._make_exam(
                root,
                read_data,
                timeout=1,
                show_log=False,
                parser=_uppercase_parser,
            )
            exam.add(_identity_task, Case("input", files=("input",)))

            book = exam.execute(output=None)

            self.assertEqual(book.answers["input"]["result"], "INPUT")

    def test_global_parser_recursively_parses_reader_mappings(self):
        with TemporaryDirectory() as temp_dir:
            def reader(name):
                return {
                    "a.txt": "1,2",
                    "nested": {"b.txt": "3,4"},
                }

            exam = self._make_exam(
                Path(temp_dir),
                reader,
                parser=_parse_csv,
                show_log=False,
            )
            exam.add(_identity_task, Case("parsed", files=("all",)))

            book = exam.execute(output=None)

            self.assertEqual(
                book.answers["parsed"]["result"],
                {
                    "a.txt": [1, 2],
                    "nested": {"b.txt": [3, 4]},
                },
            )

    def test_case_and_series_parser_can_override_or_disable_global_parser(self):
        with TemporaryDirectory() as temp_dir:
            def reader(name):
                return "1:2" if name == "colon" else "3,4"

            exam = self._make_exam(
                Path(temp_dir),
                reader,
                parser=_parse_csv,
                show_log=False,
            )
            exam.add(
                _identity_task,
                Case("colon", files=("colon",), parser=_parse_colon),
                Case("raw", files=("colon",), parser=None),
                Series("csv", "x", parser=_parse_csv),
            )

            book = exam.execute(output=None)

            self.assertEqual(book.answers["colon"]["result"], [1, 2])
            self.assertEqual(book.answers["raw"]["result"], "1:2")
            self.assertEqual(book.answers["csvx"]["result"], [3, 4])

    def test_reader_and_parser_inherit_independently_at_each_level(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            def exam_reader(name):
                return f"exam:{name}"

            def case_reader(name):
                return f"case:{name}"

            def input_reader(name):
                return f"input:{name}"

            exam = self._make_exam(
                root,
                exam_reader,
                parser=str.upper,
                show_log=False,
            )
            exam.add(
                lambda *values: values,
                Case(
                    "layers",
                    Input("exam"),
                    Input("input-reader", reader=input_reader),
                    Input("raw", parser=None),
                    Input(
                        "input-both",
                        reader=input_reader,
                        parser=str.lower,
                    ),
                    reader=case_reader,
                ),
            )

            result = exam.execute(output=None).answers["layers"]["result"]

            self.assertEqual(
                result,
                (
                    "CASE:EXAM",
                    "INPUT:INPUT-READER",
                    "case:raw",
                    "input:input-both",
                ),
            )

    def test_series_propagates_reader_and_parser_to_generated_cases(self):
        with TemporaryDirectory() as temp_dir:
            exam = self._make_exam(
                Path(temp_dir),
                lambda name: f"exam:{name}",
                parser=str.lower,
                show_log=False,
            )
            exam.add(
                _identity_task,
                Series(
                    "x",
                    "a",
                    reader=lambda name: f"series:{name}",
                    parser=str.upper,
                ),
            )

            result = exam.execute(output=None).answers["xa"]["result"]

            self.assertEqual(result, "SERIES:XA")

    def test_files_accepts_explicit_input_with_local_configuration(self):
        with TemporaryDirectory() as temp_dir:
            exam = self._make_exam(
                Path(temp_dir),
                lambda name: name,
                parser=str.upper,
                show_log=False,
            )
            exam.add(
                lambda left, right: (left, right),
                Case(
                    "mixed",
                    files=(
                        "left",
                        Input(
                            "right",
                            reader=lambda name: f"<{name}>",
                            parser=None,
                        ),
                    ),
                ),
            )

            result = exam.execute(output=None).answers["mixed"]["result"]

            self.assertEqual(result, ("LEFT", "<right>"))

    def test_input_level_read_data_binds_exam_directory(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data_dir = root / "data"
            data_dir.mkdir()
            (data_dir / "input.txt").write_text("bound", encoding="utf-8")
            exam = self._make_exam(
                root,
                str,
                timeout=1,
                show_log=False,
            )
            exam.add(
                _identity_task,
                Case("bound", Input("input", reader=read_data)),
            )

            result = exam.execute(output=None).answers["bound"]["result"]

            self.assertEqual(result, "bound")

    def test_input_level_read_files_binds_exam_directory_in_timeout_process(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "infections.txt").write_text("root", encoding="utf-8")
            exam = self._make_exam(
                root,
                str,
                timeout=1,
                show_log=False,
            )
            exam.add(
                _identity_task,
                Case(
                    "bound-file",
                    Input("infections.txt", reader=read_files),
                ),
            )

            result = exam.execute(output=None).answers["bound-file"]["result"]

            self.assertEqual(result, "root")

    def test_inherit_sentinel_survives_pickle_round_trip(self):
        restored = pickle.loads(pickle.dumps(Input("x")))

        self.assertIs(restored.reader, exam_module.INHERIT)
        self.assertIs(restored.parser, exam_module.INHERIT)

    def test_input_parser_can_reenable_parsing_disabled_by_case(self):
        with TemporaryDirectory() as temp_dir:
            exam = self._make_exam(
                Path(temp_dir),
                str,
                parser=str.lower,
                show_log=False,
            )
            exam.add(
                lambda raw, parsed: (raw, parsed),
                Case(
                    "reenabled",
                    Input("RAW"),
                    Input("PARSED", parser=str.lower),
                    parser=None,
                ),
            )

            result = exam.execute(output=None).answers["reenabled"]["result"]

            self.assertEqual(result, ("RAW", "parsed"))

    def test_rejects_invalid_layer_configuration(self):
        with self.assertRaises(TypeError):
            Input("x", reader=None)
        with self.assertRaises(TypeError):
            Input("x", parser=1)
        with self.assertRaises(TypeError):
            Case("x", reader=None)
        with self.assertRaises(TypeError):
            Series("x", reader=None)
        with TemporaryDirectory() as temp_dir:
            with self.assertRaises(TypeError):
                self._make_exam(
                    Path(temp_dir),
                    str,
                    parser=exam_module.INHERIT,
                )

    def test_resolves_explicit_input_recursively(self):
        with TemporaryDirectory() as temp_dir:
            exam = self._make_exam(
                Path(temp_dir),
                lambda name: f"data:{name}",
                show_log=False,
            )
            exam.add(
                lambda value: {"value": value},
                Case("nested", {"items": [Input("x")]}),
            )

            book = exam.execute(output=None)

            self.assertEqual(
                book.answers["nested"]["result"]["value"],
                {"items": ["data:x"]},
            )

    def test_rejects_duplicate_labels_before_reading_or_running(self):
        with TemporaryDirectory() as temp_dir:
            reader = Mock()
            task = Mock()
            exam = self._make_exam(
                Path(temp_dir),
                reader,
                show_log=False,
            )
            exam.add(task, Case("same"), Case("same"))

            with self.assertRaisesRegex(ValueError, "重复"):
                exam.execute(output=None)

            reader.assert_not_called()
            task.assert_not_called()

    def test_passes_case_timeout_and_uses_requested_output(self):
        with TemporaryDirectory() as temp_dir:
            book = Mock()
            exam = self._make_exam(
                Path(temp_dir),
                lambda name: name,
                book=book,
            )
            task = Mock()
            exam.add(task, Case("limited", files=("x",), timeout=0.5))

            result = exam.execute(output="answers.json")

            self.assertIs(result, book)
            run_args, run_kwargs = book.run.call_args
            self.assertEqual(run_args[0], "limited")
            self.assertIs(run_args[2], task)
            self.assertEqual(run_args[3], (Input("x"),))
            self.assertIs(run_args[4], exam.reader)
            self.assertIsNone(run_args[5])
            self.assertEqual(run_kwargs, {"timeout": 0.5})
            book.write_json.assert_called_once_with(
                "answers.json",
                indent=2,
                inline_simple_lists=True,
            )
            book.print_json.assert_not_called()

    def test_prints_answers_by_default(self):
        with TemporaryDirectory() as temp_dir:
            book = Mock()
            exam = self._make_exam(
                Path(temp_dir),
                lambda name: name,
                book=book,
            )
            exam.add(Mock(), Case("case"))

            exam.execute()

            book.print_json.assert_called_once_with(
                indent=2,
                inline_simple_lists=True,
            )
            book.write_json.assert_not_called()

    def test_true_output_uses_default_output_file(self):
        with TemporaryDirectory() as temp_dir:
            book = Mock()
            exam = self._make_exam(
                Path(temp_dir),
                lambda name: name,
                book=book,
            )
            exam.add(Mock(), Case("case"))

            exam.execute(output=True)

            book.write_json.assert_called_once_with(
                indent=2,
                inline_simple_lists=True,
            )
            book.print_json.assert_not_called()

    def test_execute_forwards_json_format_options(self):
        with TemporaryDirectory() as temp_dir:
            book = Mock()
            exam = self._make_exam(
                Path(temp_dir),
                lambda name: name,
                book=book,
            )
            exam.add(Mock(), Case("case"))

            exam.execute(indent=4, inline_simple_lists=False)

            book.print_json.assert_called_once_with(
                indent=4,
                inline_simple_lists=False,
            )

    def test_execute_writes_non_json_task_results_through_compatibility_layer(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            exam = self._make_exam(
                root,
                str,
                show_log=False,
            )
            exam.add(lambda: {"values": {3, 1, 2}}, Case("case"))

            exam.execute(output="answers.json")

            restored = json.loads(
                (root / "answers.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                restored["case"]["result"],
                {"values": [1, 2, 3]},
            )

    def test_reader_and_parser_run_inside_answer_book_timing(self):
        with TemporaryDirectory() as temp_dir:
            events = []

            def reader(name):
                events.append(f"read:{name}")
                return name.upper()

            def parser(data):
                events.append(f"parse:{data}")
                return data.lower()

            def task(data):
                events.append(f"task:{data}")
                return {"value": data}

            exam = self._make_exam(
                Path(temp_dir),
                reader,
                parser=parser,
                show_log=False,
            )
            exam.add(task, Case("case", files=("input",)))

            with patch(
                "utils.answer_book.perf_counter",
                side_effect=lambda: (
                    events.append("clock")
                    or float(events.count("clock"))
                ),
            ):
                exam.execute(output=None)

            self.assertEqual(
                events,
                ["clock", "read:input", "parse:INPUT", "task:input", "clock"],
            )

    def test_class_timeout_stops_a_case_through_exam(self):
        with TemporaryDirectory() as temp_dir:
            exam = self._make_exam(
                Path(temp_dir),
                str,
                timeout=0.05,
                show_log=False,
            )
            exam.add(time.sleep, Case("slow", 1))

            book = exam.execute(output=None)

            self.assertTrue(book.answers["slow"]["timeout"])
            self.assertEqual(
                book.answers["slow"]["timeout_limit"],
                0.05,
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

    def test_empty_name_returns_all_regular_files(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data_dir = root / "data"
            data_dir.mkdir()
            (data_dir / "b.txt").write_text("B", encoding="utf-8")
            (data_dir / "a.txt").write_text("A", encoding="utf-8")
            (data_dir / "nested").mkdir()

            load = self._make_caller(root)

            self.assertEqual(
                load(""),
                {"a.txt": "A", "b.txt": "B"},
            )

    def test_explicit_base_directory_works_without_caller_stack(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data_dir = root / "data"
            data_dir.mkdir()
            (data_dir / "input.txt").write_text("input", encoding="utf-8")

            self.assertEqual(read_data("input", base_dir=root), "input")

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


class ReadFilesTests(unittest.TestCase):
    def test_reads_exact_path_and_sorted_glob_with_stable_shapes(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "infections.txt").write_text("root", encoding="utf-8")
            data_dir = root / "data"
            data_dir.mkdir()
            (data_dir / "data2.txt").write_text("B", encoding="utf-8")
            (data_dir / "data1.txt").write_text("A", encoding="utf-8")

            self.assertEqual(
                read_files("infections.txt", base_dir=root),
                "root",
            )
            self.assertEqual(
                read_files("data/data*.txt", base_dir=root),
                {"data/data1.txt": "A", "data/data2.txt": "B"},
            )
            self.assertEqual(
                read_files("data/data1.*", base_dir=root),
                {"data/data1.txt": "A"},
            )

    def test_rejects_missing_absolute_empty_and_parent_selectors(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            with self.assertRaises(FileNotFoundError):
                read_files("missing.txt", base_dir=root)
            with self.assertRaises(FileNotFoundError):
                read_files("data/*.txt", base_dir=root)
            with self.assertRaises(ValueError):
                read_files("", base_dir=root)
            with self.assertRaises(ValueError):
                read_files(str(root / "input.txt"), base_dir=root)
            with self.assertRaises(ValueError):
                read_files("../input.txt", base_dir=root)


class GraphTests(unittest.TestCase):
    def test_node_type_can_be_specialized(self):
        graph = Graph[int].from_edges([(1, 2), (2, 3)])

        self.assertEqual(list(graph), [1, 2, 3])
        self.assertEqual(graph.bfs_distances(1), {1: 0, 2: 1, 3: 2})

    def test_node_set_is_complete_and_queries_do_not_create_nodes(self):
        graph = Graph({"a": ["b"]})

        self.assertEqual(list(graph), ["a", "b"])
        self.assertEqual(graph["b"], [])
        self.assertEqual(graph.indegrees(), {"a": 0, "b": 1})

        before = list(graph)
        with self.assertRaises(KeyError):
            graph.neighbors("missing")
        with self.assertRaises(KeyError):
            graph["missing"]
        self.assertEqual(list(graph), before)

        graph.add_edge("b", "c")
        self.assertEqual(list(graph), ["a", "b", "c"])
        self.assertEqual(graph["c"], [])

    def test_weighted_edges_reverse_and_degrees(self):
        graph = Graph.from_edges(
            [("a", "b", 3), ("a", "c", 5)],
            weighted=True,
        )

        self.assertEqual(
            list(graph.edges()),
            [("a", "b", 3), ("a", "c", 5)],
        )
        self.assertEqual(graph.outdegrees(), {"a": 2, "b": 0, "c": 0})
        self.assertEqual(graph.indegrees(), {"a": 0, "b": 1, "c": 1})
        self.assertEqual(
            list(graph.reverse().edges()),
            [("b", "a", 3), ("c", "a", 5)],
        )

    def test_bfs_distances_start_at_zero_and_omit_unreachable_nodes(self):
        graph = Graph.from_nodes(range(6))
        graph.add_undirected_edge(0, 1)
        graph.add_undirected_edge(1, 2)
        graph.add_undirected_edge(0, 3)

        self.assertEqual(
            graph.bfs_distances(0),
            {0: 0, 1: 1, 3: 1, 2: 2},
        )
        self.assertNotIn(4, graph.bfs_distances(0))
        with self.assertRaises(KeyError):
            graph.bfs_distances("missing")

        weighted = Graph.from_edges(
            [(0, 1, 100), (0, 2, 1), (2, 1, 1)],
            weighted=True,
        )
        self.assertEqual(weighted.bfs_distances(0), {0: 0, 1: 1, 2: 1})

    def test_dijkstra_distances_use_weights_and_omit_unreachable_nodes(self):
        graph = Graph.from_nodes([0, 1, 2, 3, "equal"], weighted=True)
        graph.add_edge(0, 1, 4)
        graph.add_edge(0, "equal", 4)
        graph.add_edge(0, 2, 1)
        graph.add_edge(2, 1, 2)

        self.assertEqual(
            graph.dijkstra_distances(0),
            {0: 0, 1: 3, "equal": 4, 2: 1},
        )
        self.assertNotIn(3, graph.dijkstra_distances(0))
        with self.assertRaises(KeyError):
            graph.dijkstra_distances("missing")

        unweighted = Graph.from_edges([(0, 1)])
        with self.assertRaisesRegex(ValueError, "requires a weighted graph"):
            unweighted.dijkstra_distances(0)

        negative = Graph.from_edges([(0, 1, -1)], weighted=True)
        with self.assertRaisesRegex(ValueError, "negative edge weights"):
            negative.dijkstra_distances(0)

    def test_topological_sort_and_cycle_detection(self):
        graph = Graph.from_edges(
            [
                ("parse", "build"),
                ("parse", "test"),
                ("build", "test"),
            ]
        )

        order = graph.topological_sort()
        positions = {node: index for index, node in enumerate(order)}
        self.assertLess(positions["parse"], positions["build"])
        self.assertLess(positions["build"], positions["test"])
        self.assertEqual(graph.topological_sort(reverse=True), list(reversed(order)))

        cycle = Graph.from_edges([(1, 2), (2, 3), (3, 1)])
        with self.assertRaisesRegex(ValueError, "contains a cycle"):
            cycle.topological_sort()

    def test_condensation_contracts_sccs_and_preserves_parallel_edges(self):
        graph = Graph.from_edges(
            [
                ("a", "b"),
                ("b", "a"),
                ("a", "c"),
                ("b", "c"),
                ("c", "d"),
                ("d", "c"),
                ("d", "e"),
            ]
        )

        result = graph.condensation()
        condensed_graph, members, component_of = result
        self.assertIs(condensed_graph, result.graph)
        self.assertEqual(members, result.members)
        self.assertEqual(component_of, result.component_of)
        first = result.component_of["a"]
        middle = result.component_of["c"]
        last = result.component_of["e"]

        self.assertEqual(first, result.component_of["b"])
        self.assertEqual(middle, result.component_of["d"])
        self.assertNotEqual(first, middle)
        self.assertNotEqual(middle, last)
        self.assertEqual(
            {frozenset(component) for component in result.members},
            {frozenset({"a", "b"}), frozenset({"c", "d"}), frozenset({"e"})},
        )
        self.assertEqual(result.components, result.members)
        self.assertEqual(result.graph.edge_count(), 3)
        self.assertEqual(
            set(result.graph.edges()),
            {(first, middle), (middle, last)},
        )

        order = result.graph.topological_sort()
        positions = {component: index for index, component in enumerate(order)}
        self.assertLess(positions[first], positions[middle])
        self.assertLess(positions[middle], positions[last])
        self.assertEqual(
            result.graph.topological_sort(reverse=True),
            list(reversed(order)),
        )

    def test_weighted_condensation_preserves_cross_component_weight(self):
        graph = Graph.from_edges(
            [("a", "b", 1), ("b", "a", 2), ("b", "c", 9)],
            weighted=True,
        )

        result = graph.condensation()
        source = result.component_of["a"]
        target = result.component_of["c"]

        self.assertTrue(result.graph.weighted)
        self.assertEqual(list(result.graph.edges()), [(source, target, 9)])

    def test_scc_uses_an_iterative_dfs(self):
        graph = Graph.from_edges((i, i + 1) for i in range(3_000))

        components = graph.strongly_connected_components()

        self.assertEqual(len(components), 3_001)
        self.assertEqual({node for component in components for node in component}, set(graph))


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


class MathExtTests(unittest.TestCase):
    def test_divisors_are_sorted_and_do_not_repeat_square_root(self):
        self.assertEqual(divisors(1), [1])
        self.assertEqual(
            divisors(36),
            [1, 2, 3, 4, 6, 9, 12, 18, 36],
        )

    def test_factor_pairs_can_include_swapped_orientations(self):
        self.assertEqual(
            factor_pairs(36),
            [(1, 36), (2, 18), (3, 12), (4, 9), (6, 6)],
        )
        self.assertEqual(
            factor_pairs(12, include_swapped=True),
            [(1, 12), (2, 6), (3, 4), (4, 3), (6, 2), (12, 1)],
        )

    def test_factor_helpers_require_a_positive_integer(self):
        for value in (0, -1):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    divisors(value)

        for value in (True, 2.5, "12"):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    factor_pairs(value)


if __name__ == "__main__":
    unittest.main()
