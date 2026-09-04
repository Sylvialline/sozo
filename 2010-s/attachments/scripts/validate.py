from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path

from codec import (
    SOURCE_CHARACTERS,
    build_dictionary,
    compress,
    compress_blocks,
    decompress,
    decompress_blocks,
    reference_locations,
    split_blocks,
)
from generate_data import make_s1, make_s2, make_s3
from solve import Q1_COMPRESSED, Q1_SOURCE


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"
ANSWERS = ROOT / "answers" / "answers.json"

EXPECTED_OUTPUTS = {
    "q1.out": ["aabbbaaabbbacabbbaabbbacaa", "aabbccdd000dd002aa"],
    "q2.out": ["5", "6"],
    "q3.out": ["65"],
    "q4.out": ["74", "ases, end.", "982", "kwnkifz993"],
    "q5.out": ["89", "ases, end.", "1000", "kifzzzzzzz"],
    "q6.out": ["OK"],
}


def read_data(name: str) -> str:
    raw = (DATA / name).read_bytes()
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as error:
        raise AssertionError(f"{name} is not ASCII") from error
    if "\r" in text or "\n" in text:
        raise AssertionError(f"{name} must not contain a line ending")
    return text


def read_output(name: str) -> list[str]:
    raw = (OUTPUTS / name).read_bytes()
    if not raw.endswith(b"\r\n"):
        raise AssertionError(f"{name} does not end in CRLF")
    if b"\r" in raw.replace(b"\r\n", b"") or b"\n" in raw.replace(b"\r\n", b""):
        raise AssertionError(f"{name} contains a non-CRLF line ending")
    return raw.decode("ascii").splitlines()


def independent_dictionary(source: str) -> dict[str, int]:
    first: dict[str, int] = {}
    for position in range(max(0, len(source) - 5)):
        pattern = source[position : position + 6]
        if pattern not in first:
            first[pattern] = position
    return first


def independent_compress(source: str) -> str:
    first = independent_dictionary(source)
    replacements: dict[int, int] = {}
    target = 1
    while target <= len(source) - 6:
        source_location = first[source[target : target + 6]]
        if source_location < target:
            replacements[target] = source_location
            target += 6
        else:
            target += 1

    result: list[str] = []
    position = 0
    while position < len(source):
        if position in replacements:
            result.append(f"{replacements[position]:03d}")
            position += 6
        else:
            result.append(source[position])
            position += 1
    return "".join(result)


def independent_decompress(compressed: str) -> str:
    restored = bytearray()
    raw = compressed.encode("ascii")
    position = 0
    while position < len(raw):
        if 48 <= raw[position] <= 57:
            token = raw[position : position + 3]
            if len(token) != 3 or any(not 48 <= value <= 57 for value in token):
                raise AssertionError("malformed replacement indication")
            source_location = int(token.decode("ascii"))
            position += 3
            for offset in range(6):
                restored.append(restored[source_location + offset])
        else:
            restored.append(raw[position])
            position += 1
    return restored.decode("ascii")


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("ascii")).hexdigest()


def expected_answers(s1: str, s2: str, s3: str, c1: str, c2: str) -> dict[str, object]:
    blocks = split_blocks(s3)
    compressed_blocks = [independent_compress(block) for block in blocks]
    return {
        "q1": {
            "decompressed": "aabbbaaabbbacabbbaabbbacaa",
            "compressed": "aabbccdd000dd002aa",
        },
        "q2_replacement_counts": {"c1.txt": 5, "c2.txt": 6},
        "q3_dictionary_entries": 65,
        "q4_compression": {
            "s1.txt": {"length": 74, "last_10": "ases, end."},
            "s2.txt": {"length": 982, "last_10": "kwnkifz993"},
        },
        "q5_decompression": {
            "c1.txt": {"length": 89, "last_10": "ases, end."},
            "c2.txt": {"length": 1000, "last_10": "kifzzzzzzz"},
        },
        "q6_block_round_trip": {
            "result": "OK",
            "source_length": 3005,
            "source_block_lengths": [1000, 1000, 1000, 5],
            "compressed_block_lengths": [982, 994, 511, 5],
            "total_compressed_length": 2492,
            "source_sha256": sha256(s3),
            "compressed_block_sha256": list(map(sha256, compressed_blocks)),
        },
    }


def fuzz_codec() -> None:
    rng = random.Random(201099)
    alphabet = "ab ,."
    hand_cases = [
        "",
        "a",
        "abcde",
        "abcdef",
        "abababababababab",
        "a" * 1000,
        ("abc, ." * 167)[:1000],
    ]
    random_cases = [
        "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 1000)))
        for _ in range(200)
    ]
    for source in hand_cases + random_cases:
        expected = independent_compress(source)
        actual = compress(source)
        if actual != expected:
            raise AssertionError(f"compression implementations disagree for length {len(source)}")
        if decompress(actual) != source or independent_decompress(actual) != source:
            raise AssertionError(f"round trip failed for length {len(source)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the data and standard answers.")
    parser.add_argument("--report", type=Path, default=ROOT / "validation.json")
    args = parser.parse_args()

    s1, s2, s3 = read_data("s1.txt"), read_data("s2.txt"), read_data("s3.txt")
    c1, c2 = read_data("c1.txt"), read_data("c2.txt")

    if (s1, s2, s3) != (make_s1(), make_s2(), make_s3(make_s2())):
        raise AssertionError("source data are not reproducible from the deterministic generator")
    if (len(s1), len(s2), len(s3)) != (89, 1000, 3005):
        raise AssertionError("source lengths changed")
    if not s1.startswith(" ") or not s3.endswith(" "):
        raise AssertionError("significant boundary spaces are missing")
    if set(s1 + s2 + s3) - SOURCE_CHARACTERS:
        raise AssertionError("source data contain invalid characters")

    independent_c1 = independent_compress(s1)
    independent_c2 = independent_compress(s2)
    if (c1, c2) != (independent_c1, independent_c2):
        raise AssertionError("compressed data do not match the independent compressor")
    if reference_locations(c1) != [1, 16, 16, 0, 6]:
        raise AssertionError("c1.txt no longer covers its intended references")
    if reference_locations(c2) != [0, 9, 99, 100, 9, 993]:
        raise AssertionError("c2.txt no longer covers reference-format boundaries")

    if independent_decompress(Q1_COMPRESSED) != EXPECTED_OUTPUTS["q1.out"][0]:
        raise AssertionError("independent Q1-1 result mismatch")
    if independent_compress(Q1_SOURCE) != EXPECTED_OUTPUTS["q1.out"][1]:
        raise AssertionError("independent Q1-2 result mismatch")
    if len(set(s1[i : i + 6] for i in range(len(s1) - 5))) != 65:
        raise AssertionError("independent Q3 dictionary size mismatch")

    source_blocks = split_blocks(s3)
    independent_blocks = [independent_compress(block) for block in source_blocks]
    if [len(block) for block in independent_blocks] != [982, 994, 511, 5]:
        raise AssertionError("Q6 compressed block lengths changed")
    if "".join(independent_decompress(block) for block in independent_blocks) != s3:
        raise AssertionError("independent Q6 round trip failed")
    if compress_blocks(s3) != independent_blocks or decompress_blocks(independent_blocks) != s3:
        raise AssertionError("primary and independent block implementations disagree")

    fuzz_codec()

    for name, expected in EXPECTED_OUTPUTS.items():
        if read_output(name) != expected:
            raise AssertionError(f"{name} differs from its independently computed answer")
    answers = json.loads(ANSWERS.read_text(encoding="utf-8"))
    if answers != expected_answers(s1, s2, s3, c1, c2):
        raise AssertionError("answers.json differs from the independently computed answer")
    if build_dictionary(s1) != independent_dictionary(s1):
        raise AssertionError("dictionary implementations disagree")

    report = {
        "data_files": ["s1.txt", "s2.txt", "s3.txt", "c1.txt", "c2.txt"],
        "output_files": list(EXPECTED_OUTPUTS),
        "encoding": "ASCII",
        "data_trailing_newline": False,
        "source_lengths": {"s1.txt": 89, "s2.txt": 1000, "s3.txt": 3005},
        "compressed_lengths": {"c1.txt": 74, "c2.txt": 982},
        "c2_reference_locations": [0, 9, 99, 100, 9, 993],
        "s3_block_lengths": [1000, 1000, 1000, 5],
        "independent_implementation_match": True,
        "fuzz_cases_passed": 207,
        "overlapping_reference_cases_passed": True,
        "all_answers_verified": True,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
