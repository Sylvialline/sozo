from __future__ import annotations

import hashlib
import json
from pathlib import Path

from codec import (
    build_dictionary,
    compress,
    compress_blocks,
    decompress,
    decompress_blocks,
    reference_locations,
    split_blocks,
    total_compressed_length,
)


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"
ANSWERS = ROOT / "answers"

Q1_COMPRESSED = "aabbba000c001008a"
Q1_SOURCE = "aabbccddaabbccddbbccddaa"


def read_raw_ascii(name: str) -> str:
    return (DATA / name).read_bytes().decode("ascii")


def write_lines(name: str, lines: list[str | int]) -> None:
    content = "\r\n".join(map(str, lines)) + "\r\n"
    (OUTPUTS / name).write_bytes(content.encode("ascii"))


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("ascii")).hexdigest()


def main() -> None:
    s1 = read_raw_ascii("s1.txt")
    s2 = read_raw_ascii("s2.txt")
    s3 = read_raw_ascii("s3.txt")
    c1 = read_raw_ascii("c1.txt")
    c2 = read_raw_ascii("c2.txt")

    q1 = [decompress(Q1_COMPRESSED), compress(Q1_SOURCE)]
    q2 = [len(reference_locations(c1)), len(reference_locations(c2))]
    q3 = len(build_dictionary(s1))

    compressed_s1 = compress(s1)
    compressed_s2 = compress(s2)
    q4 = [len(compressed_s1), compressed_s1[-10:], len(compressed_s2), compressed_s2[-10:]]

    decompressed_c1 = decompress(c1)
    decompressed_c2 = decompress(c2)
    q5 = [len(decompressed_c1), decompressed_c1[-10:], len(decompressed_c2), decompressed_c2[-10:]]

    source_blocks = split_blocks(s3)
    compressed_blocks = compress_blocks(s3)
    recovered_s3 = decompress_blocks(compressed_blocks)
    q6_ok = recovered_s3 == s3
    if not q6_ok:
        raise AssertionError("Q6 round trip failed")

    OUTPUTS.mkdir(parents=True, exist_ok=True)
    ANSWERS.mkdir(parents=True, exist_ok=True)
    write_lines("q1.out", q1)
    write_lines("q2.out", q2)
    write_lines("q3.out", [q3])
    write_lines("q4.out", q4)
    write_lines("q5.out", q5)
    write_lines("q6.out", ["OK"])

    answers = {
        "q1": {"decompressed": q1[0], "compressed": q1[1]},
        "q2_replacement_counts": {"c1.txt": q2[0], "c2.txt": q2[1]},
        "q3_dictionary_entries": q3,
        "q4_compression": {
            "s1.txt": {"length": q4[0], "last_10": q4[1]},
            "s2.txt": {"length": q4[2], "last_10": q4[3]},
        },
        "q5_decompression": {
            "c1.txt": {"length": q5[0], "last_10": q5[1]},
            "c2.txt": {"length": q5[2], "last_10": q5[3]},
        },
        "q6_block_round_trip": {
            "result": "OK",
            "source_length": len(s3),
            "source_block_lengths": list(map(len, source_blocks)),
            "compressed_block_lengths": list(map(len, compressed_blocks)),
            "total_compressed_length": total_compressed_length(compressed_blocks),
            "source_sha256": digest(s3),
            "compressed_block_sha256": list(map(digest, compressed_blocks)),
        },
    }
    (ANSWERS / "answers.json").write_text(
        json.dumps(answers, indent=2) + "\n", encoding="utf-8"
    )

    markdown = f"""# Standard Answers

## Q1

### Q1-1

```text
{q1[0]}
```

### Q1-2

```text
{q1[1]}
```

## Q2

The numbers for `c1.txt` and `c2.txt`, respectively, are:

```text
{q2[0]}
{q2[1]}
```

## Q3

```text
{q3}
```

## Q4

Each pair gives the compressed length and its last 10 characters.

```text
s1.txt: {q4[0]} {q4[1]}
s2.txt: {q4[2]} {q4[3]}
```

## Q5

Each pair gives the decompressed length and its last 10 characters.

```text
c1.txt: {q5[0]} {q5[1]}
c2.txt: {q5[2]} {q5[3]}
```

## Q6

```text
OK
```

The source is recovered exactly. Its {len(s3)} characters are split into blocks of lengths `{list(map(len, source_blocks))}`. The corresponding compressed block lengths are `{list(map(len, compressed_blocks))}`.
"""
    (ANSWERS / "standard_answers.md").write_text(markdown, encoding="utf-8")
    print(f"wrote six output files and standard answers under {ROOT}")


if __name__ == "__main__":
    main()
