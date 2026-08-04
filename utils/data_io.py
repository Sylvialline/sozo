from __future__ import annotations

import inspect
from pathlib import Path


def read_data(name: str) -> str | dict[str, str] | None:
    """Read matching files from the caller's sibling ``data`` directory.

    File names are matched by a case-sensitive substring search. If exactly
    one regular file matches, its contents are returned directly. Multiple
    matches produce a filename-to-contents dictionary, and no matches produce
    ``None``.
    """
    frame = inspect.currentframe()
    if frame is None or frame.f_back is None:
        raise RuntimeError("无法确定 read_data() 的调用代码文件")

    try:
        caller_filename = frame.f_back.f_code.co_filename
    finally:
        del frame

    if caller_filename.startswith("<") and caller_filename.endswith(">"):
        raise RuntimeError("read_data() 必须从代码文件中调用")

    data_dir = Path(caller_filename).resolve().parent / "data"
    if not data_dir.is_dir():
        return None

    paths = sorted(
        (
            path
            for path in data_dir.iterdir()
            if path.is_file() and name in path.name
        ),
        key=lambda path: path.name,
    )
    if not paths:
        return None

    result = {
        path.name: path.read_text(encoding="utf-8")
        for path in paths
    }
    if len(result) == 1:
        return next(iter(result.values()))
    return result
