"""用途：把任意标签转换为 Windows 可创建的安全输出文件名。

示例输入：``"case: 01/A*B?"`` 与保留名 ``"CON"``。
示例输出：``case_ 01_A_B_.txt``、``_CON.txt``。
复杂度：O(文件名长度)。
常见陷阱：Windows 禁止 ``<>:"/\\|?*``、尾部点/空格及 CON 等设备名。
"""

import re


INVALID = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
RESERVED = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def safe_filename(label: str, suffix: str = ".txt") -> str:
    cleaned = INVALID.sub("_", label).rstrip(" .") or "output"
    if cleaned.split(".", 1)[0].upper() in RESERVED:
        cleaned = "_" + cleaned
    return cleaned + suffix


def main() -> None:
    print(safe_filename("case: 01/A*B?"))
    print(safe_filename("CON"))


if __name__ == "__main__":
    main()
