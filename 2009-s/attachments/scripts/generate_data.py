from __future__ import annotations

import json
import random
from pathlib import Path

from rectangle_model import LARGE_LIMIT, SMALL_LIMIT, Rectangle, write_rectangles


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def make_example_data() -> list[Rectangle]:
    # Cluster 1 has three rectangles, union area 44, and a triple-covered cell.
    # Cluster 2 has four rectangles and union area 30.
    return [
        Rectangle(0, 0, 7, 6),
        Rectangle(6, 5, 2, 1),
        Rectangle(6, 5, 1, 2),
        Rectangle(20, 0, 6, 5),
        Rectangle(20, 0, 1, 1),
        Rectangle(21, 0, 1, 1),
        Rectangle(22, 0, 1, 1),
    ]


def make_ten_data() -> list[Rectangle]:
    return [
        Rectangle(10, 10, 20, 15),
        Rectangle(20, 15, 18, 20),
        Rectangle(15, 20, 15, 12),
        Rectangle(38, 15, 5, 10),
        Rectangle(100, 100, 10, 10),
        Rectangle(110, 102, 8, 6),
        Rectangle(117, 108, 5, 5),
        Rectangle(200, 200, 12, 12),
        Rectangle(212, 212, 8, 8),
        Rectangle(300, 300, 5, 5),
    ]


def scaffold(left: int, bottom: int = 300) -> list[Rectangle]:
    offsets = (0, 35, 70, 105, 140, 160)
    return [
        Rectangle(left + dx, bottom + dy, 40, 40)
        for dy in offsets
        for dx in offsets
    ]


def dense_cluster(left: int, seed: int) -> list[Rectangle]:
    rectangles = scaffold(left)
    rng = random.Random(seed)
    for _ in range(264):
        width = rng.randint(1, 50)
        height = rng.randint(1, 50)
        x = left + rng.randint(0, 200 - width)
        y = 300 + rng.randint(0, 200 - height)
        rectangles.append(Rectangle(x, y, width, height))
    assert len(rectangles) == 300
    return rectangles


def make_thousand_data() -> list[Rectangle]:
    # Two 200 x 200 covered clusters are separated by a five-unit-wide gap.
    # A third cluster consists of 400 coincident 50 x 50 rectangles.
    rectangles = dense_cluster(100, 2009) + dense_cluster(305, 2010)
    rectangles.extend(Rectangle(700, 50, 50, 50) for _ in range(400))
    assert len(rectangles) == 1000
    return rectangles


def make_q5_data() -> list[Rectangle]:
    rng = random.Random(200905)
    target_x = 9_000_025
    target_y = 8_000_025

    planted: set[Rectangle] = set()
    while len(planted) < 137:
        width = rng.randint(1, 50)
        height = rng.randint(1, 50)
        x = target_x - rng.randrange(width)
        y = target_y - rng.randrange(height)
        planted.add(Rectangle(x, y, width, height))

    rectangles = list(sorted(planted, key=lambda r: (r.x, r.y, r.w, r.h)))
    rectangles.extend(
        [
            Rectangle(0, 0, 1, 1),
            Rectangle(9_999_949, 0, 50, 50),
            Rectangle(0, 9_999_949, 50, 50),
            Rectangle(9_999_949, 9_999_949, 50, 50),
        ]
    )

    # These rectangles are mutually disjoint because adjacent slots are much
    # farther apart than the maximum width and height.
    for index in range(4859):
        width = rng.randint(1, 50)
        height = rng.randint(1, 50)
        x = 100 + (index % 1600) * 4000
        y = 500 + (index // 1600) * 100_000
        rectangles.append(Rectangle(x, y, width, height))

    assert len(rectangles) == 5000
    return rectangles


def validate_rectangles(rectangles: list[Rectangle], expected: int, limit: int) -> None:
    if len(rectangles) != expected:
        raise AssertionError(f"expected {expected} rectangles, got {len(rectangles)}")
    for rectangle in rectangles:
        rectangle.validate(limit)


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    datasets = {
        "7.txt": (make_example_data(), 7, SMALL_LIMIT),
        "10.txt": (make_ten_data(), 10, SMALL_LIMIT),
        "1000.txt": (make_thousand_data(), 1000, SMALL_LIMIT),
        "q5.txt": (make_q5_data(), 5000, LARGE_LIMIT),
    }
    for name, (rectangles, expected, limit) in datasets.items():
        validate_rectangles(rectangles, expected, limit)
        write_rectangles(DATA / name, rectangles)

    manifest = {
        "format": "ASCII text, CRLF line endings, one x y w h rectangle per line",
        "files": {
            name: {
                "rectangle_count": expected,
                "maximum_vertex_coordinate": limit - 1,
                "width_and_height_range": [1, 50],
            }
            for name, (_, expected, limit) in datasets.items()
        },
        "deterministic_seeds": {
            "1000.txt_cluster_A": 2009,
            "1000.txt_cluster_B": 2010,
            "q5.txt": 200905,
        },
        "design_notes": {
            "7.txt": "Matches the example statistics stated in the exam.",
            "1000.txt": "Contains two 200x200 clusters separated by a 5-unit gap and one 400-layer cluster.",
            "q5.txt": "Uses the enlarged coordinate range and plants 137 rectangles over one unit square; all remaining rectangles are disjoint.",
        },
    }
    (ROOT / "generation_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {len(datasets)} data files to {DATA}")


if __name__ == "__main__":
    main()
