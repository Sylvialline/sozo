from __future__ import annotations

from array import array
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


SMALL_LIMIT = 1000
LARGE_LIMIT = 10_000_000


@dataclass(frozen=True, slots=True)
class Rectangle:
    x: int
    y: int
    w: int
    h: int

    @property
    def right(self) -> int:
        return self.x + self.w

    @property
    def top(self) -> int:
        return self.y + self.h

    @property
    def area(self) -> int:
        return self.w * self.h

    def validate(self, coordinate_limit: int) -> None:
        if self.x < 0 or self.y < 0:
            raise ValueError(f"negative coordinate: {self}")
        if not (1 <= self.w <= 50 and 1 <= self.h <= 50):
            raise ValueError(f"width and height must be in [1, 50]: {self}")
        if self.right >= coordinate_limit or self.top >= coordinate_limit:
            raise ValueError(
                f"all vertex coordinates must be in [0, {coordinate_limit - 1}]: {self}"
            )


def read_rectangles(path: Path, coordinate_limit: int) -> list[Rectangle]:
    rectangles: list[Rectangle] = []
    for line_number, line in enumerate(path.read_text(encoding="ascii").splitlines(), 1):
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) != 4:
            raise ValueError(f"{path.name}:{line_number}: expected four integers")
        rectangle = Rectangle(*(int(value) for value in parts))
        rectangle.validate(coordinate_limit)
        rectangles.append(rectangle)
    return rectangles


def write_rectangles(path: Path, rectangles: Iterable[Rectangle]) -> None:
    lines = [f"{r.x} {r.y} {r.w} {r.h}" for r in rectangles]
    path.write_bytes(("\r\n".join(lines) + "\r\n").encode("ascii"))


def rectangles_connected(a: Rectangle, b: Rectangle) -> bool:
    overlap_x = min(a.right, b.right) - max(a.x, b.x)
    overlap_y = min(a.top, b.top) - max(a.y, b.y)
    return overlap_x >= 0 and overlap_y >= 0 and (overlap_x > 0 or overlap_y > 0)


class DisjointSetUnion:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))
        self.component_size = [1] * size

    def find(self, item: int) -> int:
        parent = self.parent
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(self, left: int, right: int) -> None:
        left = self.find(left)
        right = self.find(right)
        if left == right:
            return
        if self.component_size[left] < self.component_size[right]:
            left, right = right, left
        self.parent[right] = left
        self.component_size[left] += self.component_size[right]


@dataclass(slots=True)
class LayoutAnalysis:
    maximum_thickness: int
    cluster_count: int
    maximum_cluster_elements: int
    maximum_cluster_area: int
    coverage: list[array]
    labels: list[array]
    cluster_areas: tuple[int, ...]
    cluster_sizes: tuple[int, ...]
    cluster_bounding_boxes: tuple[tuple[int, int, int, int], ...]

    def summary(self) -> dict[str, int]:
        return {
            "maximum_thickness": self.maximum_thickness,
            "cluster_count": self.cluster_count,
            "maximum_cluster_elements": self.maximum_cluster_elements,
            "maximum_cluster_area": self.maximum_cluster_area,
        }


def analyze_layout(rectangles: Sequence[Rectangle], limit: int = SMALL_LIMIT) -> LayoutAnalysis:
    if not rectangles:
        raise ValueError("the layout must contain at least one rectangle")
    for rectangle in rectangles:
        rectangle.validate(limit)

    # Vertex coordinates are 0,...,limit-1, so there are limit-1 unit-cell
    # columns and rows.
    cell_limit = limit - 1
    coverage = [array("H", [0]) * cell_limit for _ in range(cell_limit)]
    for rectangle in rectangles:
        for y in range(rectangle.y, rectangle.top):
            row = coverage[y]
            for x in range(rectangle.x, rectangle.right):
                row[x] += 1
    maximum_thickness = max(max(row) for row in coverage)

    dsu = DisjointSetUnion(len(rectangles))
    for left, a in enumerate(rectangles):
        for right in range(left + 1, len(rectangles)):
            if rectangles_connected(a, rectangles[right]):
                dsu.union(left, right)

    roots = [dsu.find(index) for index in range(len(rectangles))]
    unique_roots = sorted(set(roots))
    cluster_of_root = {root: index for index, root in enumerate(unique_roots)}
    cluster_of_rectangle = [cluster_of_root[root] for root in roots]

    cluster_sizes = [0] * len(unique_roots)
    for cluster in cluster_of_rectangle:
        cluster_sizes[cluster] += 1

    labels = [array("h", [-1]) * cell_limit for _ in range(cell_limit)]
    cluster_areas = [0] * len(unique_roots)
    bounding_boxes = [[cell_limit, cell_limit, 0, 0] for _ in unique_roots]
    for rectangle, cluster in zip(rectangles, cluster_of_rectangle):
        box = bounding_boxes[cluster]
        box[0] = min(box[0], rectangle.x)
        box[1] = min(box[1], rectangle.y)
        box[2] = max(box[2], rectangle.right)
        box[3] = max(box[3], rectangle.top)
        for y in range(rectangle.y, rectangle.top):
            row = labels[y]
            for x in range(rectangle.x, rectangle.right):
                previous = row[x]
                if previous == -1:
                    row[x] = cluster
                    cluster_areas[cluster] += 1
                elif previous != cluster:
                    raise AssertionError("overlapping rectangles were assigned to different clusters")

    return LayoutAnalysis(
        maximum_thickness=maximum_thickness,
        cluster_count=len(unique_roots),
        maximum_cluster_elements=max(cluster_sizes),
        maximum_cluster_area=max(cluster_areas),
        coverage=coverage,
        labels=labels,
        cluster_areas=tuple(cluster_areas),
        cluster_sizes=tuple(cluster_sizes),
        cluster_bounding_boxes=tuple(tuple(box) for box in bounding_boxes),
    )


@dataclass(frozen=True, slots=True)
class AdditionAnalysis:
    thickness_increasing_placements: int
    maximum_cluster_area_after_addition: int
    maximizing_cluster_area_placements: int


def _maximum_cell_prefix(coverage: Sequence[array], maximum: int) -> list[array]:
    limit = len(coverage)
    prefix = [array("I", [0]) * (limit + 1) for _ in range(limit + 1)]
    for y in range(limit):
        running = 0
        current = prefix[y + 1]
        previous = prefix[y]
        source = coverage[y]
        for x in range(limit):
            running += source[x] == maximum
            current[x + 1] = previous[x + 1] + running
    return prefix


def _rectangle_sum(prefix: Sequence[array], x: int, y: int, w: int, h: int) -> int:
    return (
        prefix[y + h][x + w]
        - prefix[y][x + w]
        - prefix[y + h][x]
        + prefix[y][x]
    )


def analyze_additions(
    layout: LayoutAnalysis,
    width: int = 5,
    height: int = 10,
) -> AdditionAnalysis:
    limit = len(layout.coverage)
    max_x = limit - width
    max_y = limit - height
    total_placements = (max_x + 1) * (max_y + 1)

    prefix = _maximum_cell_prefix(layout.coverage, layout.maximum_thickness)
    thickness_increasing = sum(
        _rectangle_sum(prefix, x, y, width, height) > 0
        for y in range(max_y + 1)
        for x in range(max_x + 1)
    )

    candidate_positions: set[tuple[int, int]] = set()
    for left, bottom, right, top in layout.cluster_bounding_boxes:
        for y in range(max(0, bottom - height), min(max_y, top) + 1):
            for x in range(max(0, left - width), min(max_x, right) + 1):
                candidate_positions.add((x, y))

    labels = layout.labels
    areas = layout.cluster_areas
    original_maximum = layout.maximum_cluster_area
    best_area = original_maximum
    best_count = total_placements

    for x, y in candidate_positions:
        touched: set[int] = set()
        overlap_area = 0

        for row_index in range(y, y + height):
            row = labels[row_index]
            for column in range(x, x + width):
                cluster = row[column]
                if cluster >= 0:
                    touched.add(cluster)
                    overlap_area += 1

        if x > 0:
            column = x - 1
            for row_index in range(y, y + height):
                cluster = labels[row_index][column]
                if cluster >= 0:
                    touched.add(cluster)
        if x + width < limit:
            column = x + width
            for row_index in range(y, y + height):
                cluster = labels[row_index][column]
                if cluster >= 0:
                    touched.add(cluster)
        if y > 0:
            row = labels[y - 1]
            for column in range(x, x + width):
                cluster = row[column]
                if cluster >= 0:
                    touched.add(cluster)
        if y + height < limit:
            row = labels[y + height]
            for column in range(x, x + width):
                cluster = row[column]
                if cluster >= 0:
                    touched.add(cluster)

        merged_area = width * height - overlap_area + sum(areas[item] for item in touched)
        resulting_maximum = max(original_maximum, merged_area)
        if resulting_maximum > best_area:
            best_area = resulting_maximum
            best_count = 1
        elif resulting_maximum == best_area and best_area > original_maximum:
            best_count += 1

    return AdditionAnalysis(
        thickness_increasing_placements=thickness_increasing,
        maximum_cluster_area_after_addition=best_area,
        maximizing_cluster_area_placements=best_count,
    )


class RangeAddMaximumTree:
    def __init__(self, size: int) -> None:
        self.size = size
        self.maximum = [0] * (4 * size)
        self.lazy = [0] * (4 * size)

    def add(self, left: int, right: int, value: int) -> None:
        if left < right:
            self._add(1, 0, self.size, left, right, value)

    def _add(
        self,
        node: int,
        node_left: int,
        node_right: int,
        query_left: int,
        query_right: int,
        value: int,
    ) -> None:
        if query_left <= node_left and node_right <= query_right:
            self.maximum[node] += value
            self.lazy[node] += value
            return
        middle = (node_left + node_right) // 2
        if query_left < middle:
            self._add(node * 2, node_left, middle, query_left, query_right, value)
        if middle < query_right:
            self._add(node * 2 + 1, middle, node_right, query_left, query_right, value)
        self.maximum[node] = self.lazy[node] + max(
            self.maximum[node * 2], self.maximum[node * 2 + 1]
        )

    @property
    def value(self) -> int:
        return self.maximum[1]


def maximum_thickness_sweep(rectangles: Sequence[Rectangle]) -> int:
    if not rectangles:
        return 0
    y_coordinates = sorted({coordinate for r in rectangles for coordinate in (r.y, r.top)})
    y_index = {coordinate: index for index, coordinate in enumerate(y_coordinates)}
    events: list[tuple[int, int, int, int]] = []
    for rectangle in rectangles:
        bottom = y_index[rectangle.y]
        top = y_index[rectangle.top]
        events.append((rectangle.x, 1, bottom, top))
        events.append((rectangle.right, -1, bottom, top))
    events.sort()

    tree = RangeAddMaximumTree(len(y_coordinates) - 1)
    answer = 0
    event_index = 0
    while event_index < len(events):
        x = events[event_index][0]
        while event_index < len(events) and events[event_index][0] == x:
            _, delta, bottom, top = events[event_index]
            tree.add(bottom, top, delta)
            event_index += 1
        answer = max(answer, tree.value)
    return answer


def total_rectangle_area(rectangles: Iterable[Rectangle]) -> int:
    return sum(rectangle.area for rectangle in rectangles)
