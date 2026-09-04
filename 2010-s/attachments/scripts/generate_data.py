from __future__ import annotations

import json
import random
import string
from pathlib import Path

from codec import (
    SOURCE_CHARACTERS,
    compress,
    compress_blocks,
    decompress,
    decompress_blocks,
    reference_locations,
)


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ALPHABET = string.ascii_lowercase + " ,."


def make_s1() -> str:
    source = (
        " abcdefgabcdef, abababababababab. the quick fox, "
        "abcdefgabcdef. overlapping phrases, end."
    )
    assert len(source) == 89
    return source


def make_s2() -> str:
    rng = random.Random(201005)
    source = [rng.choice(ALPHABET) for _ in range(1000)]

    # Overlapping reference to 000.
    source[:8] = "abababab"

    # Exact three-digit formatting and minimum-location selection.
    source[9:15] = "qz,px."
    source[99:105] = "v.,qjk"
    source[300:306] = source[9:15]
    source[400:406] = source[99:105]
    source[500:506] = source[100:106]
    source[600:606] = source[9:15]

    # S[993:999] and S[994:1000] are both zzzzzz. The second one must
    # become reference 993, the largest possible indication.
    source[993:1000] = "zzzzzzz"
    result = "".join(source)
    assert len(result) == 1000
    compressed = compress(result)
    locations = reference_locations(compressed)
    assert {0, 9, 99, 100, 993} <= set(locations)
    assert locations[-1] == 993
    return result


def make_s3(s2: str) -> str:
    rng = random.Random(201006)
    second = [rng.choice(ALPHABET) for _ in range(1000)]
    second[:6] = "qz,px."  # also occurs in block 1, but dictionaries reset
    second[200:206] = "qz,px."
    second[700:712] = "xyzxyzxyzxyz"
    second = "".join(second)

    phrase = "the quick fox, jumps. "
    third = (phrase * (1000 // len(phrase) + 1))[:1000]
    tail = "end. "  # a five-character final block, including a significant space
    source = s2 + second + third + tail
    assert len(source) == 3005
    return source


def write_raw_ascii(path: Path, text: str) -> None:
    path.write_bytes(text.encode("ascii"))


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    s1 = make_s1()
    s2 = make_s2()
    s3 = make_s3(s2)
    c1 = compress(s1)
    c2 = compress(s2)

    if decompress(c1) != s1 or decompress(c2) != s2:
        raise AssertionError("single-block round trip failed")
    compressed_s3_blocks = compress_blocks(s3)
    if decompress_blocks(compressed_s3_blocks) != s3:
        raise AssertionError("multi-block round trip failed")
    if set(s1 + s2 + s3) - SOURCE_CHARACTERS:
        raise AssertionError("a source file contains an invalid character")

    files = {"s1.txt": s1, "s2.txt": s2, "s3.txt": s3, "c1.txt": c1, "c2.txt": c2}
    for name, content in files.items():
        write_raw_ascii(DATA / name, content)

    manifest = {
        "encoding": "ASCII",
        "trailing_newline": False,
        "files": {
            name: {
                "length": len(content),
                "kind": "source" if name.startswith("s") else "compressed",
            }
            for name, content in files.items()
        },
        "fixed_source_lengths": {"s1.txt": 89, "s2.txt": 1000, "s3.txt": 3005},
        "seeds": {"s2.txt": 201005, "s3.txt_second_block": 201006},
        "bug_traps": [
            "overlapping decompression references",
            "minimum matching location",
            "three-digit references 000, 009, 099, 100, and 993",
            "spaces, commas, and periods",
            "maximum single-block length 1000",
            "dictionary reset at 1000-character block boundaries",
            "five-character final block and significant trailing space",
        ],
        "s3_block_lengths": [1000, 1000, 1000, 5],
        "s3_compressed_block_lengths": list(map(len, compressed_s3_blocks)),
    }
    (ROOT / "generation_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {len(files)} data files to {DATA}")


if __name__ == "__main__":
    main()
