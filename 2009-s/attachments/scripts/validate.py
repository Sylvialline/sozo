from __future__ import annotations

import argparse
import json
from collections import Counter, deque
from pathlib import Path
from typing import Any, Sequence

from rectangle_model import (
    LARGE_LIMIT,
    SMALL_LIMIT,
    Rectangle,
    analyze_additions,
    analyze_layout,
    maximum_thickness_sweep,
    read_rectangles,
    total_rectangle_area,
)


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"
ANSWERS = ROOT / "answers" / "answers.json"

EXPECTED_LINE_COUNTS = {
    "7.txt": 7,
    "10.txt": 10,
    "1000.txt": 1000,
    "q5.txt": 5000,
}
EXPECTED_OUTPUTS = {
    "q1.out": [3, 5, 4, 645],
    "q2.out": [1_456_830],
    "q3.out": [400, 3, 400, 40_000],
    "q4.out": [3186, 209],
    "q5.out": [137],
}


def read_ascii_crlf(path: Path) -> str:
    raw = path.read_bytes()
    if not raw.endswith(b"\r\n"):
        raise AssertionError(f"{path.name} does not end in CRLF")
    residue = raw.replace(b"\r\n", b"")
    if b"\r" in residue or b"\n" in residue:
        raise AssertionError(f"{path.name} contains a non-CRLF newline")
    try:
        return raw.decode("ascii")
    except UnicodeDecodeError as error:
        raise AssertionError(f"{path.name} is not pure ASCII") from error


def independent_small_summary(rectangles: Sequence[Rectangle]) -> dict[str, int]:
    thickness: Counter[tuple[int, int]] = Counter()
    for rectangle in rectangles:
        for y in range(rectangle.y, rectangle.top):
            for x in range(rectangle.x, rectangle.right):
                thickness[x, y] += 1

    unvisited = set(thickness)
    component_of: dict[tuple[int, int], int] = {}
    component_areas: list[int] = []
    while unvisited:
        start = unvisited.pop()
        component = len(component_areas)
        queue = deque([start])
        component_of[start] = component
        area = 0
        while queue:
            x, y = queue.popleft()
            area += 1
            for neighbor in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if neighbor in unvisited:
                    unvisited.remove(neighbor)
                    component_of[neighbor] = component
                    queue.append(neighbor)
        component_areas.append(area)

    rectangle_counts = Counter(component_of[rectangle.x, rectangle.y] for rectangle in rectangles)
    return {
        "maximum_thickness": max(thickness.values()),
        "cluster_count": len(component_areas),
        "maximum_cluster_elements": max(rectangle_counts.values()),
        "maximum_cluster_area": max(component_areas),
    }


def interval_overlap(left1: int, right1: int, left2: int, right2: int) -> int:
    return max(0, min(right1, right2) - max(left1, left2))


def connected(a: Rectangle, b: Rectangle) -> bool:
    overlap_x = min(a.right, b.right) - max(a.x, b.x)
    overlap_y = min(a.top, b.top) - max(a.y, b.y)
    return overlap_x >= 0 and overlap_y >= 0 and (overlap_x > 0 or overlap_y > 0)


def independent_q4() -> tuple[int, int, int]:
    boxes = (
        Rectangle(100, 300, 200, 200),
        Rectangle(305, 300, 200, 200),
        Rectangle(700, 50, 50, 50),
    )
    areas = (40_000, 40_000, 2_500)
    thickness_increasing = 0
    best_area = 40_000
    best_count = 0

    for y in range(990):
        for x in range(995):
            added = Rectangle(x, y, 5, 10)
            if (
                interval_overlap(added.x, added.right, boxes[2].x, boxes[2].right)
                * interval_overlap(added.y, added.top, boxes[2].y, boxes[2].top)
                > 0
            ):
                thickness_increasing += 1

            touched = [index for index, box in enumerate(boxes) if connected(added, box)]
            overlap_area = sum(
                interval_overlap(added.x, added.right, boxes[index].x, boxes[index].right)
                * interval_overlap(added.y, added.top, boxes[index].y, boxes[index].top)
                for index in touched
            )
            merged_area = added.area - overlap_area + sum(areas[index] for index in touched)
            resulting_area = max(40_000, merged_area)
            if resulting_area > best_area:
                best_area = resulting_area
                best_count = 1
            elif resulting_area == best_area and best_area > 40_000:
                best_count += 1

    return thickness_increasing, best_area, best_count


def validate_q5_structure(rectangles: Sequence[Rectangle]) -> None:
    target = (9_000_025, 8_000_025)
    planted = rectangles[:137]
    boundary = rectangles[137:141]
    grid = rectangles[141:]

    if len(set(planted)) != 137:
        raise AssertionError("the 137 planted Q5 rectangles must be distinct")
    if any(not (r.x <= target[0] < r.right and r.y <= target[1] < r.top) for r in planted):
        raise AssertionError("every planted Q5 rectangle must cover the target unit square")

    expected_boundary = [
        Rectangle(0, 0, 1, 1),
        Rectangle(9_999_949, 0, 50, 50),
        Rectangle(0, 9_999_949, 50, 50),
        Rectangle(9_999_949, 9_999_949, 50, 50),
    ]
    if list(boundary) != expected_boundary:
        raise AssertionError("Q5 boundary cases changed unexpectedly")
    if len(grid) != 4859:
        raise AssertionError("Q5 must contain 4859 disjoint grid-slot rectangles")
    for index, rectangle in enumerate(grid):
        expected_x = 100 + (index % 1600) * 4000
        expected_y = 500 + (index // 1600) * 100_000
        if (rectangle.x, rectangle.y) != (expected_x, expected_y):
            raise AssertionError(f"unexpected Q5 slot at index {index}")

    # Grid slots are separated by at least 4000 horizontally or 100000
    # vertically, while widths and heights are at most 50. The four boundary
    # cases and the planted group lie outside those slots. Thus only the 137
    # planted rectangles can overlap, and they all share the target square.


def output_values(path: Path) -> list[int]:
    text = read_ascii_crlf(path)
    return [int(line) for line in text.splitlines()]


def expected_answer_json() -> dict[str, Any]:
    return {
        "q1": {
            "maximum_thickness": 3,
            "cluster_count": 5,
            "maximum_cluster_elements": 4,
            "maximum_cluster_area": 645,
        },
        "q2_total_rectangle_area": 1_456_830,
        "q3": {
            "maximum_thickness": 400,
            "cluster_count": 3,
            "maximum_cluster_elements": 400,
            "maximum_cluster_area": 40_000,
        },
        "q4": {
            "thickness_increasing_placements": 3186,
            "maximum_cluster_area_after_addition": 80_050,
            "maximizing_cluster_area_placements": 209,
        },
        "q5_maximum_thickness": 137,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate generated data and all standard answers.")
    parser.add_argument("--report", type=Path, default=ROOT / "validation.json")
    args = parser.parse_args()

    for name, expected_lines in EXPECTED_LINE_COUNTS.items():
        text = read_ascii_crlf(DATA / name)
        if len(text.splitlines()) != expected_lines:
            raise AssertionError(f"{name} must contain {expected_lines} lines")
    for name, expected in EXPECTED_OUTPUTS.items():
        if output_values(OUTPUTS / name) != expected:
            raise AssertionError(f"{name} does not contain the expected values")

    seven = read_rectangles(DATA / "7.txt", SMALL_LIMIT)
    ten = read_rectangles(DATA / "10.txt", SMALL_LIMIT)
    thousand = read_rectangles(DATA / "1000.txt", SMALL_LIMIT)
    q5_rectangles = read_rectangles(DATA / "q5.txt", LARGE_LIMIT)

    independent_seven = independent_small_summary(seven)
    independent_ten = independent_small_summary(ten)
    independent_thousand = independent_small_summary(thousand)
    if independent_seven != {
        "maximum_thickness": 3,
        "cluster_count": 2,
        "maximum_cluster_elements": 4,
        "maximum_cluster_area": 44,
    }:
        raise AssertionError(f"7.txt no longer matches the exam example: {independent_seven}")
    if list(independent_ten.values()) != EXPECTED_OUTPUTS["q1.out"]:
        raise AssertionError("independent Q1 result mismatch")
    if list(independent_thousand.values()) != EXPECTED_OUTPUTS["q3.out"]:
        raise AssertionError("independent Q3 result mismatch")
    if total_rectangle_area(thousand) != EXPECTED_OUTPUTS["q2.out"][0]:
        raise AssertionError("Q2 rectangle-area sum mismatch")

    q1_model = analyze_layout(ten)
    q3_model = analyze_layout(thousand)
    if q1_model.summary() != independent_ten or q3_model.summary() != independent_thousand:
        raise AssertionError("grid-component and rectangle-DSU analyses disagree")

    independent_q4_result = independent_q4()
    if independent_q4_result != (3186, 80_050, 209):
        raise AssertionError(f"independent Q4 result mismatch: {independent_q4_result}")
    q4_model = analyze_additions(q3_model)
    if (
        q4_model.thickness_increasing_placements,
        q4_model.maximum_cluster_area_after_addition,
        q4_model.maximizing_cluster_area_placements,
    ) != independent_q4_result:
        raise AssertionError("Q4 model and independent box enumeration disagree")

    validate_q5_structure(q5_rectangles)
    if maximum_thickness_sweep(q5_rectangles) != 137:
        raise AssertionError("Q5 sweep result must be 137")

    answers = json.loads(ANSWERS.read_text(encoding="utf-8"))
    if answers != expected_answer_json():
        raise AssertionError("answers.json does not match independently checked answers")

    report = {
        "data_files": list(EXPECTED_LINE_COUNTS),
        "output_files": list(EXPECTED_OUTPUTS),
        "encoding": "ASCII",
        "line_endings": "CRLF",
        "rectangle_counts": EXPECTED_LINE_COUNTS,
        "small_coordinate_range": [0, 999],
        "q5_coordinate_range": [0, 9_999_999],
        "width_and_height_range": [1, 50],
        "example_statistics_verified": True,
        "independent_component_check": True,
        "independent_q4_enumeration": True,
        "q5_large_coordinate_structure_verified": True,
        "all_answers_verified": True,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
