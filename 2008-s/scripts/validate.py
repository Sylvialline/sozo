from __future__ import annotations

import argparse
import json
from collections import Counter, deque
from pathlib import Path
from typing import Any

from cube_model import (
    FACES,
    INDEXED_INITIAL_STATE,
    INITIAL_STATE,
    MOVES,
    Orientation,
    SLOTS,
    apply_move,
    apply_permutation,
    apply_sequence,
    enumerate_orientations,
    inverse_sequence,
    parse_state,
    quarter_turn_permutation,
    read_state,
    search_from_initial,
    slot_geometry,
    state_rows,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data"
DEFAULT_ANSWERS = ROOT / "answers" / "answers.json"
EXPECTED_FILES = ("init-state.txt", "rotseq.txt") + tuple(f"data{i}.txt" for i in range(1, 6))


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


def validate_move_model() -> None:
    identity = tuple(range(24))
    unique = tuple(f"s{i}" for i in range(24))
    for face in "URF":
        permutation = quarter_turn_permutation(face)
        if tuple(sorted(permutation)) != identity:
            raise AssertionError(f"{face} is not a permutation of 24 facelets")
        state = unique
        for _ in range(4):
            state = apply_permutation(state, permutation)
        if state != unique:
            raise AssertionError(f"{face}^4 is not the identity")
        if apply_move(apply_move(unique, face + "1"), face + "3") != unique:
            raise AssertionError(f"{face}1 and {face}3 are not inverses")

    # Independent regression fixtures transcribed from the staircase net in
    # Figure 3. Generic outside views of the six faces can still satisfy the
    # group identities above while rotating R/F/D in the wrong in-face
    # orientation, so compare all 24 indexed facelets as well.
    expected_clockwise_rows = {
        "U1": (
            ("p4", "p1", "b4", "w2"),
            ("p3", "p2", "b3", "w3"),
            ("w1", "g2", "r1", "r2"),
            ("w4", "g3", "r4", "r3"),
            ("y1", "y2", "b1", "b2"),
            ("g1", "g4", "y4", "y3"),
        ),
        "R1": (
            ("p1", "g1", "w4", "w1"),
            ("p4", "g2", "w3", "w2"),
            ("r1", "r2", "b2", "b3"),
            ("g4", "g3", "r4", "r3"),
            ("y1", "y2", "b1", "p2"),
            ("y4", "y3", "b4", "p3"),
        ),
        "F1": (
            ("p1", "p2", "w1", "w2"),
            ("y1", "y4", "p4", "p3"),
            ("g4", "g1", "w4", "r2"),
            ("g3", "g2", "w3", "r3"),
            ("r1", "y2", "b1", "b2"),
            ("r4", "y3", "b4", "b3"),
        ),
    }
    for move, expected in expected_clockwise_rows.items():
        actual = tuple(tuple(row) for row in state_rows(apply_move(INDEXED_INITIAL_STATE, move)))
        if actual != expected:
            raise AssertionError(f"{move} does not match the indexed staircase net in Figure 3")

    fixed_indices = [
        index for index, slot in enumerate(SLOTS) if slot_geometry(slot)[0] == (-1, -1, -1)
    ]
    if len(fixed_indices) != 3:
        raise AssertionError("the U-R-F invariant cubicle must have exactly three facelets")
    fixed_labels = [INDEXED_INITIAL_STATE[index] for index in fixed_indices]
    if fixed_labels != ["r3", "y2", "b1"]:
        raise AssertionError(
            f"the Figure 3 staircase layout must map the invariant D-L-B cubicle to r3, y2, b1; got {fixed_labels}"
        )
    for move in ("U1", "R1", "F1"):
        moved = apply_move(INDEXED_INITIAL_STATE, move)
        if any(moved[index] != INDEXED_INITIAL_STATE[index] for index in fixed_indices):
            raise AssertionError(f"{move} moves the invariant cubicle")


def validate_orientations() -> tuple[dict[str, Orientation], dict[str, tuple[str, ...]]]:
    orientations, paths = enumerate_orientations()
    if len(orientations) != 24 or set(paths) != set(orientations):
        raise AssertionError("the replacement group must contain exactly 24 orientations")
    rb = Orientation.identity()
    for generator in ("UB", "FR"):
        rotation = {"FR": lambda v: (v[0], v[2], -v[1]), "UB": lambda v: (-v[2], v[1], v[0])}[generator]
        rb = rb.followed_by(rotation)
    if rb.label() != "RB":
        raise AssertionError("the statement's example UB FR = RB is not satisfied")
    identity = Orientation.identity()
    for label, orientation in orientations.items():
        if orientation.followed_by_orientation(orientation.inverse()) != identity:
            raise AssertionError(f"incorrect inverse for replacement {label}")
    return orientations, paths


def validate_files(data_dir: Path) -> tuple[list[tuple[str, ...]], list[tuple[str, ...]]]:
    texts = {name: read_ascii_crlf(data_dir / name) for name in EXPECTED_FILES}
    if parse_state(texts["init-state.txt"]) != INITIAL_STATE:
        raise AssertionError("init-state.txt is not the required initial state")

    rotation_sequences = [tuple(line.split()) for line in texts["rotseq.txt"].splitlines()]
    if len(rotation_sequences) != 4:
        raise AssertionError("rotseq.txt must contain exactly four lines")
    if rotation_sequences[0] != ("R1", "U3", "F2"):
        raise AssertionError("the first rotation sequence must be R1 U3 F2")
    if any(move not in MOVES for sequence in rotation_sequences for move in sequence):
        raise AssertionError("rotseq.txt contains an invalid rotation")

    states: list[tuple[str, ...]] = []
    fixed_indices = [
        index for index, slot in enumerate(SLOTS) if slot_geometry(slot)[0] == (-1, -1, -1)
    ]
    for index in range(1, 6):
        text = texts[f"data{index}.txt"]
        rows = [line.split() for line in text.splitlines()]
        if len(rows) != 6 or any(len(row) != 4 for row in rows):
            raise AssertionError(f"data{index}.txt must contain six rows of four entries")
        if any(len(token) != 1 or token not in "pwgryb" for row in rows for token in row):
            raise AssertionError(f"data{index}.txt contains an invalid color token")
        state = parse_state(text)
        if Counter(state) != Counter({color: 4 for color in "pwgryb"}):
            raise AssertionError(f"data{index}.txt does not contain four facelets of every color")
        if any(state[position] != INITIAL_STATE[position] for position in fixed_indices):
            raise AssertionError(f"data{index}.txt is not correctly replaced at the invariant cubicle")
        states.append(state)
    return rotation_sequences, states


def validate_answers(
    answers: dict[str, Any],
    rotation_sequences: list[tuple[str, ...]],
    data_states: list[tuple[str, ...]],
    orientations: dict[str, Orientation],
    paths: dict[str, tuple[str, ...]],
) -> dict[str, Any]:
    if answers["q1_equivalent_state_count"] != 24:
        raise AssertionError("Q1 answer must be 24")

    q2 = apply_move(INDEXED_INITIAL_STATE, "U1")
    if answers["q2_state_after_U1"] != state_rows(q2):
        raise AssertionError("Q2 state mismatch")
    fixed_indices = [
        index for index, slot in enumerate(SLOTS) if slot_geometry(slot)[0] == (-1, -1, -1)
    ]
    if answers["q2_facelets_to_circle"] != [q2[index] for index in fixed_indices]:
        raise AssertionError("Q2 circled facelets mismatch")

    for label, sequence in answers["q3_1_compositions"].items():
        if tuple(sequence) != paths[label]:
            raise AssertionError(f"Q3-1 composition mismatch for {label}")
    for label, inverse_label in answers["q3_2_inverses"]:
        if orientations[label].inverse().label() != inverse_label:
            raise AssertionError(f"Q3-2 inverse mismatch for {label}")
    if len(answers["q3_2_inverses"]) != 23:
        raise AssertionError("Q3-2 must contain all 23 non-identity replacements")

    for move in ("U1", "R1", "F1"):
        expected = state_rows(apply_move(INITIAL_STATE, move))
        if answers["q4_2_single_rotations"][move] != expected:
            raise AssertionError(f"Q4-2 mismatch for {move}")
    for answer, sequence in zip(answers["q4_3_rotation_sequences"], rotation_sequences):
        if tuple(answer["sequence"]) != sequence:
            raise AssertionError("Q4-3 sequence mismatch")
        if answer["result"] != state_rows(apply_sequence(INITIAL_STATE, sequence)):
            raise AssertionError("Q4-3 state mismatch")

    depth, shortest_paths = search_from_initial(6)
    exact_distances: list[int] = []
    for index, (state, item) in enumerate(zip(data_states, answers["q5_shortest_solutions"]), 1):
        if state not in depth:
            raise AssertionError(f"data{index}.txt requires more than six rotations")
        solution = tuple(item["one_shortest_solution"])
        if item["file"] != f"data{index}.txt" or item["shortest_length"] != depth[state]:
            raise AssertionError(f"Q5 metadata mismatch for data{index}.txt")
        if len(solution) != depth[state] or apply_sequence(state, solution) != INITIAL_STATE:
            raise AssertionError(f"Q5 solution for data{index}.txt is not shortest and correct")
        if inverse_sequence(shortest_paths[state]) != solution:
            raise AssertionError(f"Q5 canonical solution mismatch for data{index}.txt")
        exact_distances.append(depth[state])

    if exact_distances != [2, 3, 4, 5, 6]:
        raise AssertionError(f"expected exact Q5 distances 2 through 6, got {exact_distances}")

    # Confirm the five distances with a second BFS that applies all nine moves
    # at every state and does not use the same-face pruning of the solver.
    targets = set(data_states)
    independent_depth = {INITIAL_STATE: 0}
    queue = deque([INITIAL_STATE])
    while queue and targets - independent_depth.keys():
        state = queue.popleft()
        current_depth = independent_depth[state]
        if current_depth == 6:
            continue
        for move in MOVES:
            following = apply_move(state, move)
            if following in independent_depth:
                continue
            independent_depth[following] = current_depth + 1
            queue.append(following)
    independently_computed = [independent_depth[state] for state in data_states]
    if independently_computed != exact_distances:
        raise AssertionError(
            f"independent Q5 distances disagree: {independently_computed} != {exact_distances}"
        )

    return {
        "files": list(EXPECTED_FILES),
        "encoding": "ASCII",
        "line_endings": "CRLF",
        "rotation_sequence_count": len(rotation_sequences),
        "first_rotation_sequence": list(rotation_sequences[0]),
        "replacement_count": len(orientations),
        "data_exact_shortest_distances": exact_distances,
        "all_data_within_six_moves": all(distance <= 6 for distance in exact_distances),
        "answers_verified": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the local practice files and reference answers.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--answers", type=Path, default=DEFAULT_ANSWERS)
    parser.add_argument("--report", type=Path, default=ROOT / "validation.json")
    args = parser.parse_args()

    validate_move_model()
    orientations, paths = validate_orientations()
    rotation_sequences, states = validate_files(args.data)
    answers = json.loads(args.answers.read_text(encoding="utf-8"))
    report = validate_answers(answers, rotation_sequences, states, orientations, paths)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
