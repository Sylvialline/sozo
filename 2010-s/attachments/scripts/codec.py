from __future__ import annotations

import string
from collections.abc import Iterable, Sequence


SOURCE_CHARACTERS = frozenset(string.ascii_lowercase + " ,.")
PATTERN_LENGTH = 6
BLOCK_LENGTH = 1000
MAX_REFERENCE = 993


def validate_source(source: str, *, maximum_length: int | None = BLOCK_LENGTH) -> None:
    if maximum_length is not None and len(source) > maximum_length:
        raise ValueError(f"source length {len(source)} exceeds {maximum_length}")
    invalid = set(source) - SOURCE_CHARACTERS
    if invalid:
        raise ValueError(f"invalid source characters: {sorted(invalid)!r}")


def build_dictionary(source: str) -> dict[str, int]:
    validate_source(source)
    dictionary: dict[str, int] = {}
    for location in range(len(source) - PATTERN_LENGTH + 1):
        dictionary.setdefault(source[location : location + PATTERN_LENGTH], location)
    return dictionary


def compress(source: str) -> str:
    """Compress one source block of at most 1000 characters."""
    dictionary = build_dictionary(source)
    result: list[str] = []
    literal_start = 0
    target = 1

    while target + PATTERN_LENGTH <= len(source):
        pattern = source[target : target + PATTERN_LENGTH]
        source_location = dictionary[pattern]
        if source_location < target:
            result.append(source[literal_start:target])
            result.append(f"{source_location:03d}")
            target += PATTERN_LENGTH
            literal_start = target
        else:
            target += 1

    result.append(source[literal_start:])
    return "".join(result)


def decompress(compressed: str) -> str:
    """Decompress one block; overlapping references are copied sequentially."""
    result: list[str] = []
    position = 0
    while position < len(compressed):
        character = compressed[position]
        if character in SOURCE_CHARACTERS:
            result.append(character)
            position += 1
            continue

        token = compressed[position : position + 3]
        if len(token) != 3 or not token.isascii() or not token.isdigit():
            raise ValueError(f"invalid replacement indication at compressed index {position}")
        source_location = int(token)
        if source_location > MAX_REFERENCE:
            raise ValueError(f"replacement indication out of range: {token}")
        position += 3
        for offset in range(PATTERN_LENGTH):
            copy_from = source_location + offset
            if copy_from >= len(result):
                raise ValueError(
                    f"reference {token} is unavailable while producing source index {len(result)}"
                )
            result.append(result[copy_from])

    return "".join(result)


def reference_locations(compressed: str) -> list[int]:
    locations: list[int] = []
    position = 0
    while position < len(compressed):
        if compressed[position] in SOURCE_CHARACTERS:
            position += 1
        else:
            token = compressed[position : position + 3]
            if len(token) != 3 or not token.isascii() or not token.isdigit():
                raise ValueError(f"invalid replacement indication at compressed index {position}")
            location = int(token)
            if location > MAX_REFERENCE:
                raise ValueError(f"replacement indication out of range: {token}")
            locations.append(location)
            position += 3
    return locations


def split_blocks(source: str, block_length: int = BLOCK_LENGTH) -> list[str]:
    if block_length <= 0:
        raise ValueError("block length must be positive")
    validate_source(source, maximum_length=None)
    return [source[start : start + block_length] for start in range(0, len(source), block_length)]


def compress_blocks(source: str) -> list[str]:
    return [compress(block) for block in split_blocks(source)]


def decompress_blocks(compressed_blocks: Sequence[str]) -> str:
    return "".join(decompress(block) for block in compressed_blocks)


def total_compressed_length(compressed_blocks: Iterable[str]) -> int:
    return sum(map(len, compressed_blocks))
