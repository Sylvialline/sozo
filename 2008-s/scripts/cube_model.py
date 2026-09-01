from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Iterator, Sequence


FACES = ("U", "R", "F", "D", "L", "B")
COLORS = {"U": "p", "R": "w", "F": "g", "D": "r", "L": "y", "B": "b"}
MOVES = tuple(f"{face}{power}" for face in "URF" for power in (1, 2, 3))

Vector = tuple[int, int, int]
Slot = tuple[str, int, int]
State = tuple[str, ...]
Transform = Callable[[Vector], Vector]


def add(*vectors: Vector) -> Vector:
    return tuple(sum(vector[i] for vector in vectors) for i in range(3))  # type: ignore[return-value]


def scale(k: int, vector: Vector) -> Vector:
    return tuple(k * value for value in vector)  # type: ignore[return-value]


# Figure 3 is a staircase net, not three independent pairs of faces:
#
# U R
#   F D
#     L B
#
# For every displayed 2x2 face, store its outward normal, direction to the
# right on the printed net, and direction upward on the printed net. Starting
# at U, propagate these directions across each shared edge of the staircase;
# viewing every face independently from outside would rotate R/F/D incorrectly.
# With this layout the invariant D-L-B cubie is r3, y2, b1.
FACE_GEOMETRY: dict[str, tuple[Vector, Vector, Vector]] = {
    "U": ((0, 1, 0), (1, 0, 0), (0, 0, -1)),
    "R": ((1, 0, 0), (0, -1, 0), (0, 0, -1)),
    "F": ((0, 0, 1), (0, -1, 0), (1, 0, 0)),
    "D": ((0, -1, 0), (0, 0, -1), (1, 0, 0)),
    "L": ((-1, 0, 0), (0, 0, -1), (0, -1, 0)),
    "B": ((0, 0, -1), (1, 0, 0), (0, -1, 0)),
}

SLOTS: tuple[Slot, ...] = tuple((face, row, column) for face in FACES for row in range(2) for column in range(2))


def slot_geometry(slot: Slot) -> tuple[Vector, Vector]:
    face, row, column = slot
    normal, right, up = FACE_GEOMETRY[face]
    horizontal = -1 if column == 0 else 1
    vertical = 1 if row == 0 else -1
    position = add(normal, scale(horizontal, right), scale(vertical, up))
    return position, normal


GEOMETRY_TO_INDEX = {slot_geometry(slot): index for index, slot in enumerate(SLOTS)}


def rotate_x_clockwise(vector: Vector) -> Vector:
    x, y, z = vector
    return x, z, -y


def rotate_y_clockwise(vector: Vector) -> Vector:
    x, y, z = vector
    return -z, y, x


def rotate_z_clockwise(vector: Vector) -> Vector:
    x, y, z = vector
    return y, -x, z


MOVE_GEOMETRY: dict[str, tuple[int, Transform]] = {
    "U": (1, rotate_y_clockwise),
    "R": (0, rotate_x_clockwise),
    "F": (2, rotate_z_clockwise),
}


def make_initial_state(*, indexed: bool = False) -> State:
    values: list[str] = []
    clockwise_index = {(0, 0): 1, (0, 1): 2, (1, 1): 3, (1, 0): 4}
    for face, row, column in SLOTS:
        color = COLORS[face]
        values.append(f"{color}{clockwise_index[row, column]}" if indexed else color)
    return tuple(values)


INITIAL_STATE = make_initial_state()
INDEXED_INITIAL_STATE = make_initial_state(indexed=True)


def quarter_turn_permutation(face: str) -> tuple[int, ...]:
    axis, rotation = MOVE_GEOMETRY[face]
    destination_of_source: list[int] = []
    for slot in SLOTS:
        position, normal = slot_geometry(slot)
        if position[axis] == 1:
            position = rotation(position)
            normal = rotation(normal)
        destination_of_source.append(GEOMETRY_TO_INDEX[position, normal])
    return tuple(destination_of_source)


QUARTER_TURN_PERMUTATIONS = {face: quarter_turn_permutation(face) for face in "URF"}


def apply_permutation(state: State, destination_of_source: Sequence[int]) -> State:
    result = [""] * len(state)
    for source, destination in enumerate(destination_of_source):
        result[destination] = state[source]
    return tuple(result)


def apply_move(state: State, move: str) -> State:
    if len(move) != 2 or move[0] not in "URF" or move[1] not in "123":
        raise ValueError(f"invalid move: {move!r}")
    for _ in range(int(move[1])):
        state = apply_permutation(state, QUARTER_TURN_PERMUTATIONS[move[0]])
    return state


def apply_sequence(state: State, moves: Iterable[str]) -> State:
    for move in moves:
        state = apply_move(state, move)
    return state


def inverse_move(move: str) -> str:
    inverse_power = {"1": "3", "2": "2", "3": "1"}[move[1]]
    return move[0] + inverse_power


def inverse_sequence(moves: Sequence[str]) -> tuple[str, ...]:
    return tuple(inverse_move(move) for move in reversed(moves))


def state_rows(state: State) -> list[list[str]]:
    rows: list[list[str]] = []
    for face_index in range(0, 6, 2):
        left = face_index * 4
        right = (face_index + 1) * 4
        rows.append([state[left], state[left + 1], state[right], state[right + 1]])
        rows.append([state[left + 2], state[left + 3], state[right + 2], state[right + 3]])
    return rows


def format_state(state: State, newline: str = "\n") -> str:
    return newline.join(" ".join(row) for row in state_rows(state)) + newline


def parse_state(text: str) -> State:
    rows = [line.split() for line in text.splitlines() if line.strip()]
    if len(rows) != 6 or any(len(row) != 4 for row in rows):
        raise ValueError("a cube state must contain six non-empty rows of four entries")
    values = [""] * 24
    for pair in range(3):
        left_face = pair * 2
        right_face = left_face + 1
        top, bottom = rows[pair * 2], rows[pair * 2 + 1]
        left = left_face * 4
        right = right_face * 4
        values[left : left + 4] = [top[0], top[1], bottom[0], bottom[1]]
        values[right : right + 4] = [top[2], top[3], bottom[2], bottom[3]]
    return tuple(values)


def read_state(path: Path) -> State:
    return parse_state(path.read_text(encoding="ascii"))


def search_from_initial(max_depth: int) -> tuple[dict[State, int], dict[State, tuple[str, ...]]]:
    depth = {INITIAL_STATE: 0}
    path = {INITIAL_STATE: ()}
    queue = deque([INITIAL_STATE])
    while queue:
        state = queue.popleft()
        current_depth = depth[state]
        if current_depth == max_depth:
            continue
        previous_face = path[state][-1][0] if path[state] else None
        for move in MOVES:
            if move[0] == previous_face:
                continue
            following = apply_move(state, move)
            if following in depth:
                continue
            depth[following] = current_depth + 1
            path[following] = path[state] + (move,)
            queue.append(following)
    return depth, path


FACE_BY_NORMAL = {normal: face for face, (normal, _, _) in FACE_GEOMETRY.items()}


@dataclass(frozen=True)
class Orientation:
    # The transformed normal of each original face, in FACES order.
    normals: tuple[Vector, ...]

    @classmethod
    def identity(cls) -> "Orientation":
        return cls(tuple(FACE_GEOMETRY[face][0] for face in FACES))

    def followed_by(self, rotation: Transform) -> "Orientation":
        return Orientation(tuple(rotation(normal) for normal in self.normals))

    def apply_vector(self, vector: Vector) -> Vector:
        image_x = self.normals[FACES.index("R")]
        image_y = self.normals[FACES.index("U")]
        image_z = self.normals[FACES.index("F")]
        x, y, z = vector
        return add(scale(x, image_x), scale(y, image_y), scale(z, image_z))

    def followed_by_orientation(self, following: "Orientation") -> "Orientation":
        return Orientation(tuple(following.apply_vector(normal) for normal in self.normals))

    def label(self) -> str:
        old_at_new: dict[str, str] = {}
        for old_face, normal in zip(FACES, self.normals):
            old_at_new[FACE_BY_NORMAL[normal]] = old_face
        return old_at_new["U"] + old_at_new["R"]

    def inverse(self) -> "Orientation":
        image_x = self.normals[FACES.index("R")]
        image_y = self.normals[FACES.index("U")]
        image_z = self.normals[FACES.index("F")]

        def inverse_vector(vector: Vector) -> Vector:
            return (
                sum(a * b for a, b in zip(vector, image_x)),
                sum(a * b for a, b in zip(vector, image_y)),
                sum(a * b for a, b in zip(vector, image_z)),
            )

        return Orientation(tuple(inverse_vector(FACE_GEOMETRY[face][0]) for face in FACES))


ORIENTATION_GENERATORS: dict[str, Transform] = {
    "FR": rotate_x_clockwise,
    "UB": rotate_y_clockwise,
}


def enumerate_orientations() -> tuple[dict[str, Orientation], dict[str, tuple[str, ...]]]:
    identity = Orientation.identity()
    by_label = {identity.label(): identity}
    paths = {identity.label(): ()}
    queue = deque([identity])
    while queue:
        orientation = queue.popleft()
        label = orientation.label()
        for name, rotation in ORIENTATION_GENERATORS.items():
            following = orientation.followed_by(rotation)
            following_label = following.label()
            if following_label in by_label:
                continue
            by_label[following_label] = following
            paths[following_label] = paths[label] + (name,)
            queue.append(following)
    if len(by_label) != 24:
        raise AssertionError(f"expected 24 cube orientations, got {len(by_label)}")
    return by_label, paths


def iter_states_at_depth(depth: dict[State, int], wanted: int) -> Iterator[State]:
    return (state for state, value in depth.items() if value == wanted)
