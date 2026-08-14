"""Independent differential checks for the protected solve.py.

This file deliberately represents a maze by open cell-to-cell edges instead of
the wall coordinates used by solve.py.  It may be run during practice, but is
not part of the submitted solution.
"""

from __future__ import annotations

from collections import deque
import importlib.util
from pathlib import Path
import random


HERE = Path(__file__).resolve().parent
SIZE = 40
DIRECTIONS = ((-1, 0), (0, -1), (1, 0), (0, 1))  # U, L, D, R
OPPOSITE = (2, 3, 0, 1)


def load_numbers(name: str) -> list[int]:
    return [int(value) for value in (HERE / "data" / name).read_text().split(",")]


def load_wall_pairs(name: str) -> set[tuple[int, int]]:
    values = load_numbers(name)
    return set(zip(values[::2], values[1::2]))


def inside(cell: tuple[int, int], size: int) -> bool:
    row, column = cell
    return 0 <= row < size and 0 <= column < size


def adjacent(cell: tuple[int, int], direction: int) -> tuple[int, int]:
    dr, dc = DIRECTIONS[direction]
    return cell[0] + dr, cell[1] + dc


def edge(a: tuple[int, int], b: tuple[int, int]) -> frozenset[tuple[int, int]]:
    return frozenset((a, b))


def wall_coordinate(cell: tuple[int, int], direction: int) -> tuple[int, int]:
    row, column = cell
    return (
        (2 * row, 2 * column + 1),
        (2 * row + 1, 2 * column),
        (2 * row + 2, 2 * column + 1),
        (2 * row + 1, 2 * column + 2),
    )[direction]


def openings_from_wall_coordinates(
    size: int, walls: set[tuple[int, int]]
) -> set[frozenset[tuple[int, int]]]:
    result: set[frozenset[tuple[int, int]]] = set()
    for row in range(size):
        for column in range(size):
            cell = row, column
            for direction in (2, 3):
                other = adjacent(cell, direction)
                if inside(other, size) and wall_coordinate(cell, direction) not in walls:
                    result.add(edge(cell, other))
    return result


def has_wall(
    cell: tuple[int, int],
    direction: int,
    openings: set[frozenset[tuple[int, int]]],
    size: int,
) -> bool:
    other = adjacent(cell, direction)
    return not inside(other, size) or edge(cell, other) not in openings


def wall_report(
    cells: tuple[tuple[int, int], ...],
    openings: set[frozenset[tuple[int, int]]],
    size: int,
) -> dict[str, dict[str, str]]:
    labels = "ULDR"
    return {
        str(cell): {
            labels[direction]: (
                "present" if has_wall(cell, direction, openings, size) else "absent"
            )
            for direction in range(4)
        }
        for cell in cells
    }


def dead_ends(size: int, openings: set[frozenset[tuple[int, int]]]) -> int:
    return sum(
        sum(has_wall((row, column), direction, openings, size) for direction in range(4))
        == 3
        for row in range(size)
        for column in range(size)
    )


def neighbors(
    cell: tuple[int, int], openings: set[frozenset[tuple[int, int]]], size: int
):
    for direction in range(4):
        other = adjacent(cell, direction)
        if inside(other, size) and edge(cell, other) in openings:
            yield other


def shortest_cell_count(
    start: tuple[int, int],
    goal: tuple[int, int],
    openings: set[frozenset[tuple[int, int]]],
    size: int,
) -> int | None:
    queue = deque([(start, 1)])
    seen = {start}
    while queue:
        cell, distance = queue.popleft()
        if cell == goal:
            return distance
        for other in neighbors(cell, openings, size):
            if other not in seen:
                seen.add(other)
                queue.append((other, distance + 1))
    return None


def is_tree(size: int, openings: set[frozenset[tuple[int, int]]]) -> bool:
    if len(openings) != size * size - 1:
        return False
    seen = {(0, 0)}
    queue = deque(seen)
    while queue:
        for other in neighbors(queue.popleft(), openings, size):
            if other not in seen:
                seen.add(other)
                queue.append(other)
    return len(seen) == size * size


def maze_from_p(size: int, sequence: list[int]) -> set[frozenset[tuple[int, int]]]:
    """Start with every internal edge open, then add the requested walls."""
    openings = {
        edge((row, column), adjacent((row, column), direction))
        for row in range(size)
        for column in range(size)
        for direction in (2, 3)
        if inside(adjacent((row, column), direction), size)
    }
    for row in range(1, size):
        for column in range(1, size):
            value = sequence[row * size + column]
            if value == 0:
                pair = edge((row, column), (row - 1, column))
            elif value == 1:
                pair = edge((row, column), (row, column - 1))
            elif value == 2:
                pair = edge((row - 1, column - 1), (row, column - 1))
            else:
                pair = edge((row - 1, column - 1), (row - 1, column))
            openings.discard(pair)
    return openings


def maze_from_neighbor_and_cell(
    size: int,
    start: tuple[int, int],
    neighbor_sequence: list[int],
    cell_sequence: list[int],
) -> set[frozenset[tuple[int, int]]]:
    unvisited = {(row, column) for row in range(size) for column in range(size)}
    unvisited.remove(start)
    openings: set[frozenset[tuple[int, int]]] = set()
    current = start

    while True:
        offset = sum(current)
        chosen = None
        for index in range(offset, len(neighbor_sequence)):
            candidate = adjacent(current, neighbor_sequence[index])
            if candidate in unvisited:
                chosen = candidate
                break
        if chosen is not None:
            openings.add(edge(current, chosen))
            unvisited.remove(chosen)
            current = chosen
            continue

        chosen = None
        for index in range(2 * offset, len(cell_sequence) - 1, 2):
            candidate = cell_sequence[index], cell_sequence[index + 1]
            if (
                inside(candidate, size)
                and candidate not in unvisited
                and any(adjacent(candidate, d) in unvisited for d in range(4))
            ):
                chosen = candidate
                break
        if chosen is None:
            return openings
        current = chosen


def l_corner_count(
    size: int, openings: set[frozenset[tuple[int, int]]]
) -> int:
    result = 0
    for row in range(size):
        for column in range(size):
            walls = tuple(
                direction
                for direction in range(4)
                if has_wall((row, column), direction, openings, size)
            )
            if len(walls) == 2 and walls[1] != OPPOSITE[walls[0]]:
                result += 1
    return result


def longest_passages(
    size: int, openings: set[frozenset[tuple[int, int]]]
) -> tuple[int, int, set[tuple[tuple[int, int], ...]]]:
    passages: list[tuple[tuple[int, int], ...]] = []
    for row in range(size):
        start = 0
        for column in range(size):
            if has_wall((row, column), 3, openings, size):
                passages.append(tuple((row, c) for c in range(start, column + 1)))
                start = column + 1
    for column in range(size):
        start = 0
        for row in range(size):
            if has_wall((row, column), 2, openings, size):
                passages.append(tuple((r, column) for r in range(start, row + 1)))
                start = row + 1
    longest = max(map(len, passages))
    selected = {passage for passage in passages if len(passage) == longest}
    return longest, len(selected), selected


def left_hand_visited_count(
    start: tuple[int, int],
    goal: tuple[int, int],
    openings: set[frozenset[tuple[int, int]]],
    size: int,
) -> int:
    current = start
    facing = 3  # right; the upper wall is initially on the left
    visited = {current}
    seen_states = set()
    while current != goal:
        state = current, facing
        if state in seen_states:
            raise AssertionError("independent left-hand traversal looped")
        seen_states.add(state)

        left = (facing + 1) % 4  # U,L,D,R are in counter-clockwise order
        if not has_wall(current, left, openings, size):
            facing = left
        elif has_wall(current, facing, openings, size):
            facing = (facing - 1) % 4
            continue
        current = adjacent(current, facing)
        visited.add(current)
    return len(visited)


def load_solution_module():
    spec = importlib.util.spec_from_file_location("exam_2022_8_solution", HERE / "solve.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def wall_coordinates_from_openings(
    size: int, openings: set[frozenset[tuple[int, int]]]
) -> set[tuple[int, int]]:
    walls = set()
    for row in range(size):
        for column in range(size):
            cell = row, column
            for direction in range(4):
                if has_wall(cell, direction, openings, size):
                    walls.add(wall_coordinate(cell, direction))
    return walls


def random_spanning_tree(size: int, rng: random.Random):
    start = 0, 0
    seen = {start}
    stack = [start]
    openings = set()
    while stack:
        current = stack[-1]
        candidates = [
            adjacent(current, direction)
            for direction in range(4)
            if inside(adjacent(current, direction), size)
            and adjacent(current, direction) not in seen
        ]
        if not candidates:
            stack.pop()
            continue
        chosen = rng.choice(candidates)
        openings.add(edge(current, chosen))
        seen.add(chosen)
        stack.append(chosen)
    return openings


def verify_real_inputs(solution) -> dict[str, object]:
    cells = ((5, 25), (20, 20), (30, 33))

    maze2 = openings_from_wall_coordinates(SIZE, load_wall_pairs("maze2.txt"))
    assert dead_ends(SIZE, maze2) == solution.task1_2(SIZE, load_wall_pairs("maze2.txt"))["count"]

    maze3_walls = load_wall_pairs("maze3.txt")
    maze3 = openings_from_wall_coordinates(SIZE, maze3_walls)
    assert shortest_cell_count((0, 0), (39, 29), maze3, SIZE) == solution.task1_3(
        SIZE, (0, 0), (39, 29), maze3_walls
    )

    expected_tree_files = []
    source_tree_files = {}
    for number in range(10, 20):
        name = f"maze{number}.txt"
        walls = load_wall_pairs(name)
        source_tree_files[f"data/{name}"] = walls
        if is_tree(SIZE, openings_from_wall_coordinates(SIZE, walls)):
            expected_tree_files.append(f"data/{name}")
    assert expected_tree_files == solution.task1_4(SIZE, source_tree_files)

    p = load_numbers("p.txt")
    maze22 = maze_from_p(SIZE, p)
    source22_walls = solution.make_walls_from_p(SIZE, p)
    assert openings_from_wall_coordinates(SIZE, source22_walls) == maze22
    actual22 = solution.task2_2(SIZE, p)
    assert wall_report(cells, maze22, SIZE) == actual22["A"]
    assert l_corner_count(SIZE, maze22) == actual22["B"]

    neighbor_sequence = load_numbers("neighbor.txt")
    cell_sequence = load_numbers("cell.txt")
    maze23 = maze_from_neighbor_and_cell(
        SIZE, (0, 0), neighbor_sequence, cell_sequence
    )
    source23_walls = solution.make_walls_from_n_c(
        SIZE, (0, 0), neighbor_sequence, cell_sequence
    )
    assert openings_from_wall_coordinates(SIZE, source23_walls) == maze23
    actual23 = solution.task2_3(
        SIZE, (0, 0), (39, 27), neighbor_sequence, cell_sequence
    )
    assert wall_report(cells, maze23, SIZE) == actual23["A"]
    assert l_corner_count(SIZE, maze23) == actual23["B"]
    length, count, passages = longest_passages(SIZE, maze23)
    actual_passages = {tuple(map(tuple, passage)) for passage in actual23["C"]["passages"]}
    assert (length, passages) == (actual23["C"]["length"], actual_passages)
    independent_visited = left_hand_visited_count(
        (0, 0), (39, 27), maze23, SIZE
    )
    assert independent_visited == actual23["D"]["number_visited"]

    return {
        "1.2": dead_ends(SIZE, maze2),
        "1.3": shortest_cell_count((0, 0), (39, 29), maze3, SIZE),
        "1.4": expected_tree_files,
        "2.2(a)": wall_report(cells, maze22, SIZE),
        "2.2(b)": l_corner_count(SIZE, maze22),
        "2.3(a)": wall_report(cells, maze23, SIZE),
        "2.3(b)": l_corner_count(SIZE, maze23),
        "2.3(c)": {"length": length, "count": count, "passages": sorted(passages)},
        "2.3(d)": independent_visited,
    }


def verify_random_cases(solution, rounds: int = 200) -> None:
    rng = random.Random(202208)
    direction_names = "ULDR"
    for _ in range(rounds):
        size = rng.randint(2, 9)
        openings = random_spanning_tree(size, rng)
        walls = wall_coordinates_from_openings(size, openings)
        maze = solution.Maze(size, walls)

        assert maze.count_deadend_cells()["count"] == dead_ends(size, openings)
        assert maze.is_tree()
        goal = rng.randrange(size), rng.randrange(size)
        assert maze.shortest_path_length((0, 0), goal) == shortest_cell_count(
            (0, 0), goal, openings, size
        )
        assert solution.L_shaped_count(size, walls) == l_corner_count(size, openings)

        ref_length, _, ref_passages = longest_passages(size, openings)
        actual = solution.longest_straight_passages(size, walls)
        actual_passages = {tuple(passage) for passage in actual["passages"]}
        assert (actual["length"], actual_passages) == (ref_length, ref_passages)

        if goal != (0, 0):
            assert solution.navigate((0, 0), goal, walls)["number_visited"] == (
                left_hand_visited_count((0, 0), goal, openings, size)
            )

        for row in range(size):
            for column in range(size):
                cell = row, column
                for direction, name in enumerate(direction_names):
                    other = adjacent(cell, direction)
                    if inside(other, size):
                        assert solution.cell2wall(cell, name) == solution.cell2wall(
                            other, direction_names[OPPOSITE[direction]]
                        )

    # General mazes cover disconnected graphs, cycles, and negative is_tree cases.
    for _ in range(rounds):
        size = rng.randint(2, 9)
        openings = {
            edge((row, column), adjacent((row, column), direction))
            for row in range(size)
            for column in range(size)
            for direction in (2, 3)
            if inside(adjacent((row, column), direction), size) and rng.random() < 0.5
        }
        walls = wall_coordinates_from_openings(size, openings)
        maze = solution.Maze(size, walls)
        assert maze.count_deadend_cells()["count"] == dead_ends(size, openings)
        assert maze.is_tree() == is_tree(size, openings)
        goal = rng.randrange(size), rng.randrange(size)
        assert maze.shortest_path_length((0, 0), goal) == shortest_cell_count(
            (0, 0), goal, openings, size
        )
        assert solution.L_shaped_count(size, walls) == l_corner_count(size, openings)

    # The p-based construction is task-specific and intentionally fixed at 40 x 40.
    for _ in range(50):
        sequence = [rng.randrange(4) for _ in range(SIZE * SIZE)]
        expected = maze_from_p(SIZE, sequence)
        actual_walls = solution.make_walls_from_p(SIZE, sequence)
        assert openings_from_wall_coordinates(SIZE, actual_walls) == expected

    # Exercise both N-selection and C-selection.  A periodic neighbor sequence
    # guarantees that any available direction is eventually considered; repeated
    # complete cell listings guarantee a suitable C is present when one exists.
    for _ in range(rounds):
        size = rng.randint(2, 8)
        phase = rng.randrange(4)
        neighbor_sequence = [
            (index + phase) % 4 for index in range(8 * size * size)
        ]
        cells = [(row, column) for row in range(size) for column in range(size)]
        rng.shuffle(cells)
        repeated_cells = cells * 3
        cell_sequence = [coordinate for cell in repeated_cells for coordinate in cell]
        expected = maze_from_neighbor_and_cell(
            size, (0, 0), neighbor_sequence, cell_sequence
        )
        actual_walls = solution.make_walls_from_n_c(
            size, (0, 0), neighbor_sequence, cell_sequence
        )
        assert openings_from_wall_coordinates(size, actual_walls) == expected


def main() -> None:
    solution = load_solution_module()
    results = verify_real_inputs(solution)
    verify_random_cases(solution)
    print("Independent real-input comparison: PASS")
    print("Random/property comparisons (650 generated cases): PASS")
    for label, value in results.items():
        print(f"{label}: {value}")


if __name__ == "__main__":
    main()
