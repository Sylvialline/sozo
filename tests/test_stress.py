import io
import math
import random
import pickle
from pathlib import Path
from functools import partial
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from contextlib import redirect_stderr
from unittest.mock import Mock, patch

from utils import StressFailure, stress as persistent_stress


# These core comparison tests deliberately opt out of disk persistence.
stress = partial(persistent_stress, failure_file=None)


class StressTests(unittest.TestCase):
    def setUp(self):
        self.output = io.StringIO()
        # Keep test output small while checking the public summary.
        self.redirect = redirect_stderr(self.output)
        self.redirect.__enter__()
        self.addCleanup(self.redirect.__exit__, None, None, None)

    def test_random_cases_repeat_without_using_global_random(self):
        state = random.getstate()
        runs = []
        for _ in range(2):
            seen = []

            def generate(rng):
                values = [rng.randrange(-10, 11) for _ in range(rng.randrange(8))]
                seen.append(values.copy())
                return (values,)

            self.assertEqual(stress(sum, lambda a: sum(reversed(a)), generate,
                                    trials=30, seed=17), 30)
            runs.append(seen)
        self.assertEqual(runs[0], runs[1])
        self.assertEqual(random.getstate(), state)
        self.assertIn("30 cases, seed=17", self.output.getvalue())

    def test_first_mismatch_keeps_original_input_and_stops(self):
        seen = []

        def candidate(values):
            seen.append(values.copy())
            values.sort()
            return values[0]

        cases = [([1],), ([2, 1],), ([3],)]
        with self.assertRaises(StressFailure) as caught:
            stress(candidate, lambda values: values[0], cases, seed=9)
        failure = caught.exception
        self.assertEqual(failure.inputs, ([2, 1],))
        self.assertEqual(cases[1], ([2, 1],))
        self.assertEqual(seen, [[1], [2, 1]])
        self.assertEqual((failure.actual, failure.expected), (1, 2))
        self.assertEqual((failure.case_index, failure.seed, failure.phase),
                         (2, 9, "mismatch"))

    def test_deep_copies_preserve_aliases_within_one_call(self):
        values = [[1]]

        def candidate(a, b):
            self.assertIs(a, b)
            a[0].append(2)
            return a

        def reference(a, b):
            self.assertIs(a, b)
            self.assertEqual(a, [[1]])
            return [[1, 2]]

        self.assertEqual(stress(candidate, reference, [(values, values)]), 1)
        self.assertEqual(values, [[1]])

    def test_snapshot_return_value_before_other_solver_mutates_it(self):
        shared = []

        def candidate():
            shared[:] = [1]
            return shared

        def reference():
            shared[:] = [2]
            return shared

        with self.assertRaises(StressFailure) as caught:
            stress(candidate, reference, [()])
        self.assertEqual(caught.exception.actual, [1])
        self.assertEqual(caught.exception.expected, [2])

    def test_custom_comparison_and_trial_limit_do_not_overconsume(self):
        seen = []

        def cases():
            for value in range(10):
                seen.append(value)
                yield (value,)

        self.assertEqual(stress(lambda x: x + 1e-10, lambda x: x, cases(),
                                equal=lambda a, b: math.isclose(a, b, abs_tol=1e-9),
                                trials=3), 3)
        self.assertEqual(seen, [0, 1, 2])

    def test_exception_retains_stage_input_and_cause(self):
        def broken(*args):
            raise RuntimeError("broken")

        for phase in ("generate", "candidate", "reference", "compare"):
            with self.subTest(phase=phase):
                with self.assertRaises(StressFailure) as caught:
                    stress(broken if phase == "candidate" else sum,
                           broken if phase == "reference" else sum,
                           broken if phase == "generate" else [([1],)],
                           equal=broken if phase == "compare" else lambda a, b: a == b)
                self.assertEqual(caught.exception.phase, phase)
                self.assertIsInstance(caught.exception.__cause__, RuntimeError)
                self.assertEqual(caught.exception.inputs,
                                 None if phase == "generate" else ([1],))

    def test_rejects_ambiguous_cases_and_empty_run(self):
        with self.assertRaises(StressFailure) as caught:
            stress(sum, sum, [[1, 2]])
        self.assertIsInstance(caught.exception.__cause__, TypeError)
        with self.assertRaises(ValueError):
            stress(sum, sum, [])
        for trials in (0, -1, True, 1.5):
            with self.subTest(trials=trials), self.assertRaises(ValueError):
                stress(sum, sum, [], trials=trials)

    def test_keyboard_interrupt_is_not_caught(self):
        def interrupt():
            raise KeyboardInterrupt

        with self.assertRaises(KeyboardInterrupt):
            stress(interrupt, lambda: 0, [()])


class StressReplayTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.path = self.root / "case.pickle"
        self.output = io.StringIO()
        self.enterContext(redirect_stderr(self.output))

    def save_failure(self, candidate=lambda a: -1, reference=sum):
        with self.assertRaises(StressFailure) as caught:
            persistent_stress(candidate, reference, [([3, 2],)], seed=7,
                              failure_file=self.path)
        self.assertEqual(caught.exception.failure_file, self.path)

    def test_unchanged_failure_replays_before_generating_or_consuming(self):
        self.save_failure()
        generate = Mock(side_effect=AssertionError("must not generate"))
        with self.assertRaises(StressFailure) as caught:
            persistent_stress(lambda a: -2, sum, generate, seed=99,
                              failure_file=self.path)
        failure = caught.exception
        self.assertTrue(failure.replayed)
        self.assertEqual((failure.inputs, failure.actual, failure.expected),
                         (([3, 2],), -2, 5))
        self.assertEqual((failure.seed, failure.case_index), (7, 1))
        generate.assert_not_called()

    def test_fixed_case_is_kept_and_fresh_random_sequence_is_unchanged(self):
        self.save_failure()
        seen = []

        def candidate(a):
            seen.append(a.copy())
            return sum(a)

        def generate(rng):
            return ([rng.randrange(100)],)

        count = persistent_stress(candidate, sum, generate, trials=2, seed=41,
                                  failure_file=self.path)
        rng = random.Random(41)
        self.assertEqual(seen, [[3, 2], [rng.randrange(100)], [rng.randrange(100)]])
        self.assertEqual(count, 3)
        self.assertTrue(self.path.is_file())
        self.assertIn("Stress replay passed", self.output.getvalue())
        self.assertEqual(persistent_stress(sum, sum, failure_file=self.path), 1)

    def test_new_failure_replaces_previous_after_successful_replay(self):
        self.save_failure()
        with self.assertRaises(StressFailure):
            persistent_stress(lambda a: sum(a) if a else -1, sum, [( [],)],
                              seed=8, failure_file=self.path)
        with self.assertRaises(StressFailure) as caught:
            persistent_stress(lambda a: -1, sum, failure_file=self.path)
        self.assertEqual(caught.exception.inputs, ([],))
        self.assertEqual(caught.exception.seed, 8)

    def test_runtime_error_replays_original_unmodified_data(self):
        def crash(a):
            a.clear()
            raise ZeroDivisionError("broken")

        self.save_failure(crash)
        self.assertEqual(persistent_stress(sum, lambda a: 5,
                                          failure_file=self.path), 1)

    def test_reference_and_comparator_are_recomputed(self):
        self.save_failure()
        self.assertEqual(persistent_stress(lambda a: 10, lambda a: 11,
                                          equal=lambda a, b: abs(a-b) <= 1,
                                          failure_file=self.path), 1)

    def test_default_paths_are_separate_for_different_function_pairs(self):
        def first(a):
            return -1

        def second(a):
            return -2

        with patch("utils.stress.caller_directory", return_value=self.root):
            paths = []
            for candidate in (first, second):
                with self.assertRaises(StressFailure) as caught:
                    persistent_stress(candidate, sum, [([1],)])
                paths.append(caught.exception.failure_file)
            self.assertNotEqual(paths[0], paths[1])
            self.assertTrue(all(path.parent == self.root / ".stress" for path in paths))

    def test_missing_corrupt_or_unwritable_cache_is_visible(self):
        with self.assertRaises(FileNotFoundError):
            persistent_stress(sum, sum, failure_file=self.path)
        self.path.write_bytes(pickle.dumps({"version": 100}))
        with self.assertRaisesRegex(ValueError, "Invalid stress failure file"):
            persistent_stress(sum, sum, failure_file=self.path)
        self.path.unlink()
        with patch("utils.stress._save_failure", side_effect=OSError("disk full")):
            with self.assertRaises(StressFailure) as caught:
                persistent_stress(lambda a: 0, sum, [([1],)], failure_file=self.path)
        self.assertEqual(caught.exception.phase, "mismatch")
        self.assertIsNone(caught.exception.failure_file)
        self.assertIn("disk full", " ".join(caught.exception.__notes__))

    def test_auto_replay_survives_new_process_and_code_edit(self):
        script = self.root / "probe.py"
        repo = Path(__file__).resolve().parents[1]
        source = (
            "import sys\n"
            f"sys.path.insert(0, {str(repo)!r})\n"
            "from utils import stress\n"
            "def candidate(a):\n"
            "    return -1\n"
            "def reference(a):\n"
            "    return sum(a)\n"
            "if len(sys.argv) == 1:\n"
            "    stress(candidate, reference, [([1],), ([3, 2],)])\n"
            "else:\n"
            "    stress(candidate, reference)\n"
        )
        script.write_text(source, encoding="utf-8")
        first = subprocess.run([sys.executable, str(script)], cwd=repo,
                               capture_output=True, text=True, timeout=15)
        self.assertNotEqual(first.returncode, 0)
        self.assertIn("Counterexample saved", first.stderr)
        # Edit the function body, retaining its name; rerun from a different cwd.
        script.write_text(source.replace("return -1", "return sum(a)"), encoding="utf-8")
        second = subprocess.run([sys.executable, str(script), "replay"], cwd=self.root,
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn("Stress replay passed", second.stderr)


if __name__ == "__main__":
    unittest.main()
