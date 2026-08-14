"""Reproducibly generate the complete 2019-s data package and its answers."""

from __future__ import annotations

import binascii
import json
import random
import struct
import string
import zlib
from pathlib import Path

from reference_solver import (
    DATA1_ALPHABET,
    RSA_E,
    RSA_N,
    decompress,
    optimal_compress,
    sha256,
    solve_all,
)


ATTACHMENTS_DIR = Path(__file__).resolve().parent
DATA_DIR = ATTACHMENTS_DIR.parent
OUTPUT_DIR = ATTACHMENTS_DIR / "reference_outputs"
SEED = 20190825

INPUT_NAMES = (
    "data1.txt",
    "data2a.bin",
    "data2b.bin",
    "data2c.bin",
    "data3a.txt",
    "data3b.png",
    "data3c.txt",
    "data4.txt",
    "data4dict.txt",
    "data5.txt",
)


def make_tiff(width: int, height: int) -> bytes:
    """Build a standards-compliant uncompressed RGB baseline TIFF."""
    pixels = bytearray()
    for y in range(height):
        for x in range(width):
            block = ((x // 5) + (y // 4)) % 6
            palette = (
                (0, 0, 0),
                (255, 255, 255),
                (32, 64, 128),
                (128, 64, 32),
                (20, 180, 90),
                (220, 40, 100),
            )
            pixels.extend(palette[block])

    entry_count = 10
    ifd_offset = 8
    ifd_size = 2 + 12 * entry_count + 4
    bits_offset = ifd_offset + ifd_size
    pixel_offset = bits_offset + 8  # three SHORTs plus two-byte alignment padding

    def entry(tag: int, kind: int, count: int, value: int) -> bytes:
        prefix = struct.pack("<HHI", tag, kind, count)
        if kind == 3 and count == 1:
            return prefix + struct.pack("<H", value) + b"\0\0"
        return prefix + struct.pack("<I", value)

    entries = (
        entry(256, 4, 1, width),
        entry(257, 4, 1, height),
        entry(258, 3, 3, bits_offset),
        entry(259, 3, 1, 1),
        entry(262, 3, 1, 2),
        entry(273, 4, 1, pixel_offset),
        entry(277, 3, 1, 3),
        entry(278, 4, 1, height),
        entry(279, 4, 1, len(pixels)),
        entry(284, 3, 1, 1),
    )
    return (
        b"II"
        + struct.pack("<HIH", 42, ifd_offset, entry_count)
        + b"".join(entries)
        + struct.pack("<I", 0)
        + struct.pack("<HHH", 8, 8, 8)
        + b"\0\0"
        + pixels
    )


def _png_chunk(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", binascii.crc32(kind + payload) & 0xFFFFFFFF)


def make_png(width: int, height: int) -> bytes:
    """Build a valid 8-bit RGB PNG using only the standard library."""
    scanlines = bytearray()
    for y in range(height):
        scanlines.append(0)  # PNG filter type: None
        for x in range(width):
            band = (x // 6 + y // 6) % 4
            scanlines.extend(
                (
                    (17 * band + 3 * x) % 256,
                    (53 * band + 5 * y) % 256,
                    (29 * band + 2 * (x + y)) % 256,
                )
            )
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + _png_chunk(b"IHDR", ihdr) + _png_chunk(b"IDAT", zlib.compress(bytes(scanlines), 9)) + _png_chunk(b"IEND", b"")


def make_data1() -> bytes:
    values = [(i * i * 11 + i * 37 + 19) % 64 for i in range(192)]
    # Explicitly cover both alphabet ends and every mapping symbol.
    values[20:84] = range(64)
    return ("".join(DATA1_ALPHABET[value] for value in values) + "\n").encode("ascii")


def make_question_2_originals() -> dict[str, bytes]:
    text_a = (
        "restored files must preserve every byte exactly. "
        "short repeats, long repeats, and punctuation all matter.\n"
        "abcabcabcabc -- abcabcabcabc -- end.\n"
    ).encode("ascii") * 5
    text_c = (
        "復元は一バイトずつ確認する。 repeated blocks make back references useful.\n"
        "zero is represented by a three-byte command; ordinary bytes remain literal.\n"
    ).encode("utf-8") * 4
    return {
        "data2a.txt": text_a,
        "data2b.tif": make_tiff(40, 30),
        "data2c.txt": text_c,
    }


def make_question_3_inputs() -> dict[str, bytes]:
    data3a = (
        "timed programming rewards compact and readable tools.\n"
        "compact and readable tools reduce mechanical mistakes.\n"
        "timed programming rewards compact and readable tools.\n"
    ).encode("ascii") * 7
    data3c = (
        "alpha beta gamma delta alpha beta gamma delta\n"
        "境界値と繰り返しを同時に含むデータ。\n"
        "alpha beta gamma delta alpha beta gamma delta\n"
    ).encode("utf-8") * 6
    return {
        "data3a.txt": data3a,
        "data3b.png": make_png(48, 36),
        "data3c.txt": data3c,
    }


def make_question_4(rng: random.Random) -> tuple[bytes, bytes, str]:
    plaintext = (
        "quick brown foxes jump over the lazy dog while bright stars guide calm coders. "
        "practice builds compact tools and clear habits for timed programming exams. "
        "reusable helpers reduce mistakes when pressure rises."
    )
    letters = string.ascii_lowercase
    cipher_letters = "".join(letters[(11 * i + 7) % 26] for i in range(26))
    mapping = str.maketrans(letters, cipher_letters)
    ciphertext = plaintext.translate(mapping)
    words = sorted(set(plaintext.replace(".", "").split()))
    rng.shuffle(words)
    return (ciphertext + "\n").encode("ascii"), (" ".join(words) + "\n").encode("ascii"), plaintext


def make_question_5() -> tuple[bytes, str]:
    plaintext = "reusable tools make timed coding calmer."
    raw = plaintext.encode("utf-8")
    if len(raw) % 4:
        raise AssertionError("question 5 plaintext must occupy complete four-byte chunks")
    encrypted = [str(pow(int.from_bytes(raw[i : i + 4], "big"), RSA_E, RSA_N)) for i in range(0, len(raw), 4)]
    return (" ".join(encrypted) + "\n").encode("ascii"), plaintext


def render_answers(answers: dict[str, object]) -> str:
    q1 = answers["1"]
    q2 = answers["2"]
    q3 = answers["3"]
    q4 = answers["4"]
    q5 = answers["5"]
    lines = [
        "2019-s reference answers",
        "",
        f"(1) bits 310..320: {q1['bit_sequence']}",  # type: ignore[index]
        "",
        "(2) restored sizes:",
    ]
    for name, result in q2["files"].items():  # type: ignore[index,union-attr]
        lines.append(f"  {name} -> {result['restored_name']}: {result['restored_size_bytes']} bytes")
    lines.extend(("", "(3) minimum compressed sizes:"))
    for name, result in q3["files"].items():  # type: ignore[index,union-attr]
        lines.append(f"  {name} -> {result['compressed_name']}: {result['compressed_size_bytes']} bytes")
    lines.extend(
        (
            "",
            f"(4) first sentence: {q4['first_sentence']}",  # type: ignore[index]
            "",
            f"(5) plaintext: {q5['plaintext']}",  # type: ignore[index]
            f"    p={q5['p']}, q={q5['q']}, d={q5['d']}",  # type: ignore[index]
            "",
        )
    )
    return "\n".join(lines)


def write_reference_outputs(q2_originals: dict[str, bytes], q3_inputs: dict[str, bytes]) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    for name, data in q2_originals.items():
        (OUTPUT_DIR / name).write_bytes(data)
    for name, data in q3_inputs.items():
        (OUTPUT_DIR / f"{Path(name).stem}.bin").write_bytes(optimal_compress(data))


def write_summary(inputs: dict[str, bytes], q2_originals: dict[str, bytes], answers: dict[str, object]) -> None:
    summary = {
        "seed": SEED,
        "input_files": {
            name: {"size_bytes": len(data), "sha256": sha256(data)}
            for name, data in sorted(inputs.items())
        },
        "coverage": {
            "1": "192 six-bit symbols; all 64 mapping characters occur; queried range crosses character boundaries.",
            "2": "literal bytes, zero commands, short and long non-overlapping back-references; UTF-8 text and a valid RGB TIFF.",
            "3": "minimum-size dynamic programming on ASCII text, a valid RGB PNG, and UTF-8 text; repeated and incompressible regions.",
            "4": "three sentences, every dictionary word used, all lower-case letters represented, unique substitution solution.",
            "5": "ten four-byte chunks; recovered secret exponent and UTF-8/ASCII plaintext.",
        },
        "restored_question_2": {
            name: {"size_bytes": len(data), "sha256": sha256(data)}
            for name, data in sorted(q2_originals.items())
        },
        "answers_sha256": sha256((json.dumps(answers, ensure_ascii=False, indent=2) + "\n").encode("utf-8")),
    }
    (ATTACHMENTS_DIR / "dataset_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_manifest() -> None:
    lines = ["sha256\tsize_bytes\tpath"]
    for path in sorted(DATA_DIR.rglob("*"), key=lambda p: p.relative_to(DATA_DIR).as_posix()):
        if not path.is_file() or path.name == "manifest.sha256.tsv" or "__pycache__" in path.parts:
            continue
        data = path.read_bytes()
        lines.append(f"{sha256(data)}\t{len(data)}\t{path.relative_to(DATA_DIR).as_posix()}")
    (ATTACHMENTS_DIR / "manifest.sha256.tsv").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    rng = random.Random(SEED)
    q2_originals = make_question_2_originals()
    q3_inputs = make_question_3_inputs()
    data4, dictionary4, expected_q4 = make_question_4(rng)
    data5, expected_q5 = make_question_5()

    inputs = {
        "data1.txt": make_data1(),
        "data2a.bin": optimal_compress(q2_originals["data2a.txt"]),
        "data2b.bin": optimal_compress(q2_originals["data2b.tif"]),
        "data2c.bin": optimal_compress(q2_originals["data2c.txt"]),
        **q3_inputs,
        "data4.txt": data4,
        "data4dict.txt": dictionary4,
        "data5.txt": data5,
    }
    if set(inputs) != set(INPUT_NAMES):
        raise AssertionError("generated input file set does not match the statement")
    for name, data in inputs.items():
        (DATA_DIR / name).write_bytes(data)

    write_reference_outputs(q2_originals, q3_inputs)
    answers = solve_all(DATA_DIR)
    if answers["4"]["plaintext"] != expected_q4 or answers["5"]["plaintext"] != expected_q5:  # type: ignore[index]
        raise AssertionError("generated cipher answers did not round-trip")
    for compressed_name, restored_name in (
        ("data2a.bin", "data2a.txt"),
        ("data2b.bin", "data2b.tif"),
        ("data2c.bin", "data2c.txt"),
    ):
        if decompress(inputs[compressed_name]) != q2_originals[restored_name]:
            raise AssertionError(f"{compressed_name} did not round-trip")

    answer_json = json.dumps(answers, ensure_ascii=False, indent=2) + "\n"
    (ATTACHMENTS_DIR / "answers.json").write_text(answer_json, encoding="utf-8", newline="\n")
    (ATTACHMENTS_DIR / "answers.txt").write_text(render_answers(answers), encoding="utf-8", newline="\n")
    write_summary(inputs, q2_originals, answers)
    write_manifest()
    print(f"generated {len(inputs)} input files and answers for five questions")


if __name__ == "__main__":
    main()
