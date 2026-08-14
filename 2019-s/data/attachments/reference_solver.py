"""Independent reference solution for the 2020 Summer Programming exam.

The directory is named ``2019-s`` in this repository because the examination
was held in summer 2019 for admission in academic year 2020.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from math import isqrt
from pathlib import Path
from typing import Iterable


DATA1_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#"
RSA_E = 551263368336670859257571
RSA_N = 3858843578360632069557337


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decode_six_bit_text(text: str) -> str:
    """Restore the bit string encoded with the statement's 64 characters."""
    encoded = "".join(text.split())
    try:
        return "".join(f"{DATA1_ALPHABET.index(ch):06b}" for ch in encoded)
    except ValueError as exc:
        raise ValueError("data1.txt contains a character outside the 64-symbol alphabet") from exc


def solve_1(path: Path) -> dict[str, object]:
    bits = decode_six_bit_text(path.read_text(encoding="ascii"))
    if len(bits) <= 320:
        raise ValueError("data1.txt must encode at least 321 bits")
    return {
        "bit_range": [310, 320],
        "bit_sequence": bits[310:321],
        "encoded_characters": len(bits) // 6,
        "total_bits": len(bits),
    }


def decompress(data: bytes) -> bytes:
    """Decode the byte-oriented format specified in questions (2) and (3)."""
    restored = bytearray()
    i = 0
    while i < len(data):
        value = data[i]
        i += 1
        if value:
            restored.append(value)
            continue

        if i + 2 > len(data):
            raise ValueError("truncated three-byte command")
        p, d = data[i], data[i + 1]
        i += 2
        if p < d:
            raise ValueError(f"invalid command: p={p} is smaller than d={d}")
        if d == 0:
            restored.append(0)
            continue
        if p == 0 or p > len(restored):
            raise ValueError(f"invalid command: p={p} exceeds restored prefix")

        # d <= p makes this a non-overlapping copy, as required by the statement.
        start = len(restored) - p
        restored.extend(restored[start : start + d])
    return bytes(restored)


def _maximum_copy_lengths(data: bytes) -> list[int]:
    """For every position, find its longest legal earlier copy in O(255*n)."""
    n = len(data)
    longest = [0] * n
    for p in range(1, min(255, n - 1) + 1):
        run = 0
        for i in range(n - 1, p - 1, -1):
            if data[i] == data[i - p]:
                run += 1
            else:
                run = 0
            length = min(run, p)
            if length > longest[i]:
                longest[i] = length
    return longest


def optimal_compress(data: bytes) -> bytes:
    """Return a minimum-byte encoding accepted by :func:`decompress`.

    Dynamic programming is necessary: choosing the longest available copy at
    every position is not guaranteed to give the smallest complete file.
    """
    n = len(data)
    longest = _maximum_copy_lengths(data)
    costs = [0] * (n + 1)
    token_counts = [0] * (n + 1)
    choices: list[tuple[str, int] | None] = [None] * n

    for i in range(n - 1, -1, -1):
        literal_cost = 1 if data[i] else 3
        best_score = (literal_cost + costs[i + 1], 1 + token_counts[i + 1], 1, -1)
        best_choice = ("literal", 1)

        for length in range(1, longest[i] + 1):
            score = (3 + costs[i + length], 1 + token_counts[i + length], 0, -length)
            if score < best_score:
                best_score = score
                best_choice = ("copy", length)

        costs[i], token_counts[i] = best_score[:2]
        choices[i] = best_choice

    encoded = bytearray()
    i = 0
    while i < n:
        kind, length = choices[i]  # type: ignore[misc]
        if kind == "literal":
            if data[i]:
                encoded.append(data[i])
            else:
                encoded.extend((0, 0, 0))
            i += 1
            continue

        p = next(
            p
            for p in range(length, min(255, i) + 1)
            if data[i : i + length] == data[i - p : i - p + length]
        )
        encoded.extend((0, p, length))
        i += length

    if len(encoded) != costs[0] or decompress(encoded) != data:
        raise AssertionError("internal optimal-compression consistency check failed")
    return bytes(encoded)


def solve_2(data_dir: Path) -> dict[str, object]:
    files: dict[str, object] = {}
    for stem, output_name in (
        ("data2a", "data2a.txt"),
        ("data2b", "data2b.tif"),
        ("data2c", "data2c.txt"),
    ):
        restored = decompress((data_dir / f"{stem}.bin").read_bytes())
        files[f"{stem}.bin"] = {
            "restored_name": output_name,
            "restored_size_bytes": len(restored),
            "restored_sha256": sha256(restored),
        }
    return {"files": files}


def solve_3(data_dir: Path) -> dict[str, object]:
    files: dict[str, object] = {}
    for input_name in ("data3a.txt", "data3b.png", "data3c.txt"):
        original = (data_dir / input_name).read_bytes()
        compressed = optimal_compress(original)
        output_name = f"{Path(input_name).stem}.bin"
        files[input_name] = {
            "compressed_name": output_name,
            "original_size_bytes": len(original),
            "compressed_size_bytes": len(compressed),
            "compressed_sha256": sha256(compressed),
        }
    return {"files": files}


def _pattern(word: str) -> tuple[int, ...]:
    ids: dict[str, int] = {}
    return tuple(ids.setdefault(ch, len(ids)) for ch in word)


def _compatible(cipher_word: str, plain_word: str, c2p: dict[str, str], p2c: dict[str, str]) -> bool:
    return all(
        c2p.get(c, p) == p and p2c.get(p, c) == c
        for c, p in zip(cipher_word, plain_word)
    )


def _extend_mapping(
    cipher_word: str,
    plain_word: str,
    c2p: dict[str, str],
    p2c: dict[str, str],
) -> tuple[dict[str, str], dict[str, str]]:
    new_c2p = c2p.copy()
    new_p2c = p2c.copy()
    for c, p in zip(cipher_word, plain_word):
        new_c2p[c] = p
        new_p2c[p] = c
    return new_c2p, new_p2c


def decrypt_substitution(ciphertext: str, dictionary: Iterable[str]) -> str:
    """Solve the substitution cipher, including unknown space/period symbols."""
    words = sorted(set(dictionary))
    if not ciphertext or not words:
        raise ValueError("ciphertext and dictionary must both be nonempty")

    by_signature: dict[tuple[int, tuple[int, ...]], list[str]] = defaultdict(list)
    for word in words:
        if not word.isascii() or not word.islower() or not word.isalpha():
            raise ValueError(f"invalid dictionary word: {word!r}")
        by_signature[(len(word), _pattern(word))].append(word)

    cipher_period = ciphertext[-1]
    solutions: list[str] = []
    for cipher_space in sorted(set(ciphertext) - {cipher_period}):
        parts = ciphertext.split(cipher_space)
        if any(not part for part in parts):
            continue

        cipher_words: list[str] = []
        sentence_ends: list[bool] = []
        valid_layout = True
        for part in parts:
            if cipher_period in part[:-1]:
                valid_layout = False
                break
            ends = part.endswith(cipher_period)
            word = part[:-1] if ends else part
            if not word:
                valid_layout = False
                break
            cipher_words.append(word)
            sentence_ends.append(ends)
        if not valid_layout or not sentence_ends[-1]:
            continue

        unique_cipher_words = sorted(set(cipher_words))
        if len(unique_cipher_words) != len(words):
            continue
        candidates = {
            cw: by_signature[(len(cw), _pattern(cw))]
            for cw in unique_cipher_words
        }
        if any(not options for options in candidates.values()):
            continue

        def search(
            remaining: tuple[str, ...],
            c2p: dict[str, str],
            p2c: dict[str, str],
            assignment: dict[str, str],
        ) -> None:
            if len(solutions) > 1:
                return
            if not remaining:
                plain_parts = [assignment[word] + ("." if end else "") for word, end in zip(cipher_words, sentence_ends)]
                solutions.append(" ".join(plain_parts))
                return

            best_word = min(
                remaining,
                key=lambda cw: sum(
                    _compatible(cw, pw, c2p, p2c)
                    for pw in candidates[cw]
                ),
            )
            next_remaining = tuple(cw for cw in remaining if cw != best_word)
            for plain_word in candidates[best_word]:
                if plain_word in assignment.values() or not _compatible(best_word, plain_word, c2p, p2c):
                    continue
                next_c2p, next_p2c = _extend_mapping(best_word, plain_word, c2p, p2c)
                assignment[best_word] = plain_word
                search(next_remaining, next_c2p, next_p2c, assignment)
                del assignment[best_word]

        search(
            tuple(unique_cipher_words),
            {cipher_space: " ", cipher_period: "."},
            {" ": cipher_space, ".": cipher_period},
            {},
        )

    unique_solutions = sorted(set(solutions))
    if len(unique_solutions) != 1:
        raise ValueError(f"expected one substitution solution, found {len(unique_solutions)}")
    return unique_solutions[0]


def solve_4(cipher_path: Path, dictionary_path: Path) -> dict[str, object]:
    ciphertext = cipher_path.read_text(encoding="ascii").strip()
    dictionary = dictionary_path.read_text(encoding="ascii").split()
    plaintext = decrypt_substitution(ciphertext, dictionary)
    first_sentence = plaintext.split(".", 1)[0] + "."
    return {
        "first_sentence": first_sentence,
        "plaintext": plaintext,
        "dictionary_words": len(set(dictionary)),
    }


def recover_rsa_parameters(e: int = RSA_E, n: int = RSA_N) -> tuple[int, int, int]:
    """Use e*d=(p-1)(q-1)+1 and p*q=n to recover p, q, and d."""
    # p+q = n+2-e*d must be positive, so the search has a finite tight bound.
    for d in range(1, (n + 1) // e + 1):
        total = n + 2 - e * d
        discriminant = total * total - 4 * n
        if discriminant < 0:
            continue
        root = isqrt(discriminant)
        if root * root != discriminant or (total + root) % 2:
            continue
        p = (total + root) // 2
        q = (total - root) // 2
        if p * q == n and e * d == (p - 1) * (q - 1) + 1:
            return min(p, q), max(p, q), d
    raise ValueError("could not recover RSA parameters from the stated equality")


def decrypt_rsa_text(text: str) -> tuple[str, int, int, int]:
    p, q, d = recover_rsa_parameters()
    restored = b"".join(pow(int(token), d, RSA_N).to_bytes(4, "big") for token in text.split())
    return restored.decode("utf-8"), p, q, d


def solve_5(path: Path) -> dict[str, object]:
    plaintext, p, q, d = decrypt_rsa_text(path.read_text(encoding="ascii"))
    return {"plaintext": plaintext, "p": p, "q": q, "d": d}


def solve_all(data_dir: Path) -> dict[str, object]:
    data_dir = data_dir.resolve()
    return {
        "1": solve_1(data_dir / "data1.txt"),
        "2": solve_2(data_dir),
        "3": solve_3(data_dir),
        "4": solve_4(data_dir / "data4.txt", data_dir / "data4dict.txt"),
        "5": solve_5(data_dir / "data5.txt"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_dir", nargs="?", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    print(json.dumps(solve_all(args.data_dir), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
