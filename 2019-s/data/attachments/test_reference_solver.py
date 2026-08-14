"""Standard-library regression tests for the generated data and reference code."""

from __future__ import annotations

import json
import random
import struct
import unittest
import zlib
from functools import cache
from pathlib import Path

from reference_solver import (
    DATA1_ALPHABET,
    RSA_E,
    RSA_N,
    decode_six_bit_text,
    decompress,
    optimal_compress,
    recover_rsa_parameters,
    sha256,
    solve_all,
)


ATTACHMENTS_DIR = Path(__file__).resolve().parent
DATA_DIR = ATTACHMENTS_DIR.parent
OUTPUT_DIR = ATTACHMENTS_DIR / "reference_outputs"


def brute_minimum_size(data: bytes) -> int:
    """Small-input exhaustive oracle, deliberately separate from the fast DP."""
    @cache
    def visit(i: int) -> int:
        if i == len(data):
            return 0
        best = (1 if data[i] else 3) + visit(i + 1)
        for p in range(1, min(255, i) + 1):
            for d in range(1, min(p, len(data) - i) + 1):
                if data[i : i + d] == data[i - p : i - p + d]:
                    best = min(best, 3 + visit(i + d))
                else:
                    break
        return best

    return visit(0)


def independent_decompress(data: bytes) -> bytes:
    restored: list[int] = []
    cursor = 0
    while cursor < len(data):
        token = data[cursor]
        cursor += 1
        if token != 0:
            restored.append(token)
            continue
        if cursor + 1 >= len(data):
            raise ValueError("truncated command")
        p, d = data[cursor : cursor + 2]
        cursor += 2
        if not 0 <= d <= p < 256:
            raise ValueError("invalid p,d")
        if d == 0:
            restored.append(0)
        else:
            if p > len(restored):
                raise ValueError("copy precedes output")
            source = len(restored) - p
            copied = restored[source : source + d]
            if len(copied) != d:
                raise ValueError("overlapping copy")
            restored += copied
    return bytes(restored)


def parse_png(data: bytes) -> tuple[int, int, bytes]:
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("bad PNG signature")
    cursor = 8
    width = height = 0
    payloads: list[bytes] = []
    saw_end = False
    while cursor < len(data):
        length = struct.unpack(">I", data[cursor : cursor + 4])[0]
        kind = data[cursor + 4 : cursor + 8]
        payload = data[cursor + 8 : cursor + 8 + length]
        cursor += 12 + length
        if kind == b"IHDR":
            width, height, depth, color, compression, filtering, interlace = struct.unpack(">IIBBBBB", payload)
            if (depth, color, compression, filtering, interlace) != (8, 2, 0, 0, 0):
                raise ValueError("unexpected PNG format")
        elif kind == b"IDAT":
            payloads.append(payload)
        elif kind == b"IEND":
            saw_end = True
            break
    raw = zlib.decompress(b"".join(payloads))
    if not saw_end or len(raw) != height * (1 + 3 * width):
        raise ValueError("incomplete PNG")
    return width, height, raw


class ReferenceSolverTests(unittest.TestCase):
    def test_layout(self) -> None:
        expected_root = {
            "attachments",
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
        }
        expected_attachments = {
            "README.md",
            "answers.json",
            "answers.txt",
            "dataset_summary.json",
            "generate_data.py",
            "manifest.sha256.tsv",
            "reference_outputs",
            "reference_solver.py",
            "test_reference_solver.py",
        }
        expected_outputs = {
            "data2a.txt",
            "data2b.tif",
            "data2c.txt",
            "data3a.bin",
            "data3b.bin",
            "data3c.bin",
        }
        self.assertEqual({path.name for path in DATA_DIR.iterdir()}, expected_root)
        self.assertEqual({path.name for path in ATTACHMENTS_DIR.iterdir()}, expected_attachments)
        self.assertEqual({path.name for path in OUTPUT_DIR.iterdir()}, expected_outputs)

    def test_statement_six_bit_example(self) -> None:
        self.assertEqual(decode_six_bit_text("BHC#"), "000001000111000010111111")
        self.assertEqual(len(DATA1_ALPHABET), 64)

    def test_statement_decompression_example(self) -> None:
        compressed = bytes.fromhex("41 42 43 44 45 46 47 00 06 05 48")
        expected = bytes.fromhex("41 42 43 44 45 46 47 42 43 44 45 46 48")
        self.assertEqual(decompress(compressed), expected)
        self.assertEqual(independent_decompress(compressed), expected)

    def test_fast_compressor_against_exhaustive_oracle(self) -> None:
        rng = random.Random(19082019)
        cases = [b"", b"\0", b"aaaaaa", b"abcabcabc", b"\0\0\0\0", bytes(range(12))]
        cases += [bytes(rng.randrange(5) for _ in range(length)) for length in range(1, 15) for _ in range(25)]
        for original in cases:
            with self.subTest(original=original):
                compressed = optimal_compress(original)
                self.assertEqual(independent_decompress(compressed), original)
                self.assertEqual(len(compressed), brute_minimum_size(original))

    def test_delivery_answers(self) -> None:
        expected = json.loads((ATTACHMENTS_DIR / "answers.json").read_text(encoding="utf-8"))
        self.assertEqual(solve_all(DATA_DIR), expected)
        self.assertEqual(expected["1"]["bit_sequence"], "11100000100")
        self.assertEqual(
            [expected["2"]["files"][name]["restored_size_bytes"] for name in ("data2a.bin", "data2b.bin", "data2c.bin")],
            [715, 3742, 656],
        )
        self.assertEqual(
            [expected["3"]["files"][name]["compressed_size_bytes"] for name in ("data3a.txt", "data3b.png", "data3c.txt")],
            [107, 5183, 100],
        )

    def test_reference_output_artifacts(self) -> None:
        pairs = {
            "data2a.bin": "data2a.txt",
            "data2b.bin": "data2b.tif",
            "data2c.bin": "data2c.txt",
        }
        for compressed_name, restored_name in pairs.items():
            expected = (OUTPUT_DIR / restored_name).read_bytes()
            encoded = (DATA_DIR / compressed_name).read_bytes()
            self.assertEqual(independent_decompress(encoded), expected)

        for input_name in ("data3a.txt", "data3b.png", "data3c.txt"):
            encoded = (OUTPUT_DIR / f"{Path(input_name).stem}.bin").read_bytes()
            original = (DATA_DIR / input_name).read_bytes()
            self.assertEqual(independent_decompress(encoded), original)

    def test_png_structure(self) -> None:
        width, height, raw = parse_png((DATA_DIR / "data3b.png").read_bytes())
        self.assertEqual((width, height), (48, 36))
        self.assertTrue(all(raw[y * (1 + 3 * width)] == 0 for y in range(height)))

    def test_substitution_answer_is_consistent(self) -> None:
        answers = json.loads((ATTACHMENTS_DIR / "answers.json").read_text(encoding="utf-8"))
        plaintext = answers["4"]["plaintext"]
        ciphertext = (DATA_DIR / "data4.txt").read_text(encoding="ascii").strip()
        dictionary = set((DATA_DIR / "data4dict.txt").read_text(encoding="ascii").split())
        self.assertEqual(set(plaintext.replace(".", "").split()), dictionary)
        self.assertEqual(len(ciphertext), len(plaintext))
        c2p: dict[str, str] = {}
        p2c: dict[str, str] = {}
        for cipher, plain in zip(ciphertext, plaintext):
            self.assertEqual(c2p.setdefault(cipher, plain), plain)
            self.assertEqual(p2c.setdefault(plain, cipher), cipher)
        self.assertTrue(plaintext.endswith("."))

    def test_rsa_relation_and_plaintext(self) -> None:
        p, q, d = recover_rsa_parameters()
        self.assertEqual(p * q, RSA_N)
        self.assertEqual(RSA_E * d, (p - 1) * (q - 1) + 1)
        answers = json.loads((ATTACHMENTS_DIR / "answers.json").read_text(encoding="utf-8"))
        raw = answers["5"]["plaintext"].encode("utf-8")
        ciphertext = [int(token) for token in (DATA_DIR / "data5.txt").read_text(encoding="ascii").split()]
        self.assertEqual(len(raw) % 4, 0)
        self.assertEqual(
            ciphertext,
            [pow(int.from_bytes(raw[i : i + 4], "big"), RSA_E, RSA_N) for i in range(0, len(raw), 4)],
        )

    def test_manifest(self) -> None:
        rows = (ATTACHMENTS_DIR / "manifest.sha256.tsv").read_text(encoding="utf-8").splitlines()
        self.assertEqual(rows[0], "sha256\tsize_bytes\tpath")
        for row in rows[1:]:
            digest, size, relative = row.split("\t")
            data = (DATA_DIR / relative).read_bytes()
            self.assertEqual(len(data), int(size))
            self.assertEqual(sha256(data), digest)


if __name__ == "__main__":
    unittest.main(verbosity=2)
