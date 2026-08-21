import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from workflow.run_python import (
    UTF8_CODE_PAGE,
    find_pypy,
    utf8_console,
    utf8_environment,
)


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "workflow" / "run_python.py"


class RunPythonTests(unittest.TestCase):
    def test_utf8_environment_sets_python_io_flags(self):
        environment = utf8_environment()

        self.assertEqual(environment["PYTHONIOENCODING"], "utf-8")
        self.assertEqual(environment["PYTHONUTF8"], "1")

    def test_cpython_child_writes_utf8(self):
        self._assert_runtime_writes_utf8("python")

    def test_pypy_child_writes_utf8_when_available(self):
        if find_pypy() is None:
            self.skipTest("PyPy is not installed")
        self._assert_runtime_writes_utf8("pypy")

    @unittest.skipUnless(sys.platform == "win32", "Windows-only behavior")
    def test_console_code_pages_are_temporarily_utf8_and_restored(self):
        import ctypes

        kernel32 = ctypes.windll.kernel32
        original_input = kernel32.GetConsoleCP()
        original_output = kernel32.GetConsoleOutputCP()
        if not original_input or not original_output:
            self.skipTest("No Windows console is attached")

        with utf8_console():
            self.assertEqual(kernel32.GetConsoleCP(), UTF8_CODE_PAGE)
            self.assertEqual(kernel32.GetConsoleOutputCP(), UTF8_CODE_PAGE)

        self.assertEqual(kernel32.GetConsoleCP(), original_input)
        self.assertEqual(kernel32.GetConsoleOutputCP(), original_output)

    def _assert_runtime_writes_utf8(self, runtime: str):
        with TemporaryDirectory() as temp_dir:
            script = Path(temp_dir) / "encoding_probe.py"
            script.write_text(
                "import os, sys\n"
                "print(sys.stdout.encoding)\n"
                "print(os.environ['PYTHONIOENCODING'])\n"
                "print(os.environ['PYTHONUTF8'])\n"
                "print('中文输出')\n",
                encoding="utf-8",
            )

            completed = subprocess.run(
                [sys.executable, str(RUNNER), runtime, str(script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            output = completed.stdout.decode("utf-8")
            lines = output.splitlines()

            self.assertIn("utf-8", output.lower())
            self.assertIn("1", lines)
            self.assertIn("中文输出", output)
