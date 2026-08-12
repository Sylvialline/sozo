from __future__ import annotations

import inspect
from pathlib import Path


_UTILS_DIR = Path(__file__).resolve().parent


def caller_directory(owner: str, *, action: str = "调用") -> Path:
    """Return the first caller directory outside the ``utils`` package."""
    frame = inspect.currentframe()
    if frame is None:
        raise RuntimeError(f"无法确定 {owner} 的调用代码文件")

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

    raise RuntimeError(f"{owner} 必须从代码文件中{action}")
