import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
PROFILER = ROOT / "workflow" / "profile_python.py"


class ProfilePythonTests(unittest.TestCase):
    def _write_probe(self, directory: Path) -> Path:
        script = directory / "probe.py"
        script.write_text(
            "def work(n):\n"
            "    total = 0\n"
            "    for i in range(n):\n"
            "        total += i * i\n"
            "    return total\n"
            "\n"
            "if __name__ == '__main__':\n"
            "    print(work(1000))\n",
            encoding="utf-8",
        )
        return script

    def test_function_profile_creates_stats_and_summary(self):
        with TemporaryDirectory() as temp_dir:
            script = self._write_probe(Path(temp_dir))
            completed = subprocess.run(
                [sys.executable, str(PROFILER), "functions", "--top", "3", str(script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True,
                encoding="utf-8",
            )

            self.assertTrue(script.with_name("probe.py.prof").is_file())
            self.assertIn("[cumulative time: top 3]", completed.stdout)
            self.assertIn("[self time: top 3]", completed.stdout)

    @unittest.skipIf(
        importlib.util.find_spec("line_profiler") is None,
        "line_profiler is not installed",
    )
    def test_line_profile_auto_profiles_script_without_decorator(self):
        with TemporaryDirectory() as temp_dir:
            script = self._write_probe(Path(temp_dir))
            completed = subprocess.run(
                [sys.executable, str(PROFILER), "lines", str(script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True,
                encoding="utf-8",
            )

            self.assertTrue(script.with_name("probe.py.lprof").is_file())
            self.assertIn("Function: work", completed.stdout)


if __name__ == "__main__":
    unittest.main()
