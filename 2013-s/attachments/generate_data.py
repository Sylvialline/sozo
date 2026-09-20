#!/usr/bin/env python3
"""Deterministically generate multi-query inputs for all six questions."""

from __future__ import annotations

from decimal import Decimal
import hashlib
import json
from pathlib import Path
import random


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SEED = 2013_08_01


def fixed_decimal(coefficient: int, exponent: int, trailing_zeros: int = 0) -> str:
    value = Decimal(coefficient).scaleb(exponent)
    text = format(value, "f")
    if trailing_zeros:
        if "." not in text:
            text += "."
        text += "0" * trailing_zeros
    return text


def decimal_cases(
    count: int,
    *,
    minimum_nonzero: Decimal,
    maximum: Decimal = Decimal("1000000"),
    seed_offset: int,
    curated: list[str],
    exponents: tuple[int, ...] = tuple(range(-12, 2)),
) -> list[str]:
    rng = random.Random(SEED + seed_offset)
    result = list(curated)
    seen = set(result)
    while len(result) < count:
        coefficient = rng.randint(1, 999_999)
        exponent = rng.choice(exponents)
        sign = -1 if rng.randrange(4) == 0 else 1
        trailing = rng.randrange(4) if rng.randrange(8) == 0 else 0
        token = fixed_decimal(sign * coefficient, exponent, trailing)
        magnitude = abs(Decimal(token))
        if magnitude < minimum_nonzero or magnitude > maximum or token in seen:
            continue
        result.append(token)
        seen.add(token)
    return result


COMMON = [
    "0", "-0.0", "1", "-1", "10", "-10", "20", "-20", "1000000",
    "0.1", "0.10", "0.100000000000", "0.099999999999", "0.100000000001",
    "0.5", "2.5", "3.333333333333", "9.999999999999", "10.000000000001",
]


def write_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="ascii", newline="\n")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_q6() -> list[str]:
    rng = random.Random(SEED + 6)
    targets = [
        ("0", 1), ("-0.0", 8), ("0.01", 8), ("-0.02", 7),
        ("0.1", 8), ("0.100000000001", 6), ("0.099999999999", 6),
        ("1", 1), ("1", 8), ("10", 8), ("20", 8),
        ("3.333333333333", 5), ("2.5", 4),
    ]
    per_n = {1: 55, 2: 50, 3: 45, 4: 40, 5: 30, 6: 20, 7: 10, 8: 6}
    counts = {n: sum(query_n == n for _, query_n in targets) for n in per_n}
    seen = set(targets)
    while any(counts[n] < per_n[n] for n in per_n):
        candidates = [n for n in per_n if counts[n] < per_n[n]]
        n = rng.choice(candidates)
        coefficient = rng.randint(1, 999_999)
        exponent = rng.choice((-7, -7, -6, -6, -5, -5, -4))
        token = fixed_decimal(-coefficient if rng.randrange(5) == 0 else coefficient, exponent)
        if abs(Decimal(token)) < Decimal("0.01") or abs(Decimal(token)) > Decimal("1000000"):
            continue
        pair = (token, n)
        if pair in seen:
            continue
        seen.add(pair)
        targets.append(pair)
        counts[n] += 1
    rng.shuffle(targets)
    return [f"{d} {n}" for d, n in targets]


def main() -> None:
    files = {
        "q1.txt": decimal_cases(
            50_000,
            minimum_nonzero=Decimal("0.000000000001"),
            seed_offset=1,
            curated=COMMON + ["0.000000000001", "-0.000000000001"],
        ),
        "q2.txt": decimal_cases(
            2_000,
            minimum_nonzero=Decimal("0.0005"),
            seed_offset=2,
            curated=COMMON + ["0.0005", "-0.0005", "0.000500000001"],
        ),
        "q3.txt": ["K2"] * 32,
        # At 20 digits after the decimal point, n=1..61 give distinct
        # rounded areas, n=62 is the first adjacent rounding collision, and
        # n>=63 has already rounded to the limiting area. Keep every
        # informative early stage, then add a few large values to catch
        # implementations that expand the boundary or iterate n times.
        "q4.txt": [
            *(str(n) for n in range(1, 65)),
            "100", "127", "128", "255", "256", "999", "1000", "1001",
            "1000000", "999999999", "1000000000",
        ],
        "q5.txt": decimal_cases(
            1_000,
            minimum_nonzero=Decimal("0.002"),
            seed_offset=5,
            curated=COMMON + ["0.002", "-0.002", "0.002000000001"],
            exponents=(-8, -7, -6, -5, -4),
        ),
        "q6.txt": build_q6(),
    }

    for name, lines in files.items():
        write_lines(DATA / name, lines)

    manifest = {
        "seed": SEED,
        "deterministic": True,
        "format": "one independent query per line; no leading case count",
        "decimal_semantics": "each decimal token is parsed exactly via Decimal",
        "files": {
            name: {
                "cases": len(lines),
                "sha256": sha256(DATA / name),
            }
            for name, lines in files.items()
        },
        "ranges": {
            "q1": "d = 0 or 1e-12 <= |d| <= 1e6",
            "q2": "d = 0 or 5e-4 <= |d| <= 1e6",
            "q3": "32 independent requests for fixed K2",
            "q4": "1 <= n <= 1e9",
            "q5": "d = 0 or 0.002 <= |d| <= 1e6",
            "q6": "d = 0 or 0.01 <= |d| <= 1e6; 1 <= n <= 8",
        },
    }
    (ROOT / "attachments" / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
