from __future__ import annotations

import inspect
from pathlib import Path


_UTILS_DIR = Path(__file__).resolve().parent


def _caller_directory() -> Path:
    """Return the first caller directory outside the ``utils`` package."""
    frame = inspect.currentframe()
    if frame is None:
        raise RuntimeError("无法确定 read_data() 的调用代码文件")

    try:
        caller = frame.f_back
        while caller is not None:
            filename = caller.f_code.co_filename
            if not (filename.startswith("<") and filename.endswith(">")):
                path = Path(filename).resolve()
                if not path.is_relative_to(_UTILS_DIR):
                    return path.parent
            caller = caller.f_back
    finally:
        del frame

    raise RuntimeError("read_data() 必须从代码文件中调用")


def read_data(
    name: str,
    *,
    base_dir: str | Path | None = None,
) -> str | dict[str, str] | None:
    """Read matching files from the caller's sibling ``data`` directory.

    File names are matched by a case-sensitive substring search. An empty
    ``name`` matches every regular file. If exactly one file matches, its
    contents are returned directly. Multiple matches produce a
    filename-to-contents dictionary, and no matches produce ``None``.

    ``base_dir`` is mainly used by orchestration code that has already captured
    the caller directory, including Windows timeout subprocesses whose stack no
    longer contains the original caller.
    """
    if not isinstance(name, str):
        raise TypeError("name 必须是字符串")

    root = _caller_directory() if base_dir is None else Path(base_dir).resolve()
    data_dir = root / "data"
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
