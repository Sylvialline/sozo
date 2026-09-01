from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

from cube_model import (
    FACES,
    INDEXED_INITIAL_STATE,
    INITIAL_STATE,
    SLOTS,
    apply_move,
    apply_sequence,
    enumerate_orientations,
    format_state,
    inverse_sequence,
    read_state,
    search_from_initial,
    slot_geometry,
    state_rows,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data"
DEFAULT_OUTPUT = ROOT / "answers"
TARGET_ORIENTATIONS = ("UL", "FU", "RU", "BU", "LD")


def read_rotation_sequences(path: Path) -> list[tuple[str, ...]]:
    return [tuple(line.split()) for line in path.read_text(encoding="ascii").splitlines() if line.strip()]


def ordered_orientation_labels(available: Iterable[str]) -> list[str]:
    available_set = set(available)
    return [a + b for a in FACES for b in FACES if a + b in available_set]


def solve(data_dir: Path) -> dict[str, Any]:
    initial = read_state(data_dir / "init-state.txt")
    if initial != INITIAL_STATE:
        raise ValueError("init-state.txt does not contain the expected initial state")

    q2_state = apply_move(INDEXED_INITIAL_STATE, "U1")
    invariant_indices = [
        index for index, slot in enumerate(SLOTS) if slot_geometry(slot)[0] == (-1, -1, -1)
    ]

    orientations, orientation_paths = enumerate_orientations()
    labels = ordered_orientation_labels(orientations)
    rotation_sequences = read_rotation_sequences(data_dir / "rotseq.txt")

    depth, shortest_paths = search_from_initial(6)
    q5: list[dict[str, Any]] = []
    for index in range(1, 6):
        state = read_state(data_dir / f"data{index}.txt")
        if state not in shortest_paths:
            raise ValueError(f"data{index}.txt is farther than six rotations from the initial state")
        solution = inverse_sequence(shortest_paths[state])
        if apply_sequence(state, solution) != INITIAL_STATE:
            raise AssertionError("computed Q5 solution does not restore the initial state")
        q5.append(
            {
                "file": f"data{index}.txt",
                "shortest_length": depth[state],
                "one_shortest_solution": list(solution),
            }
        )

    return {
        "q1_equivalent_state_count": 24,
        "q2_state_after_U1": state_rows(q2_state),
        "q2_facelets_to_circle": [q2_state[index] for index in invariant_indices],
        "q3_1_compositions": {
            label: list(orientation_paths[label]) for label in TARGET_ORIENTATIONS
        },
        "q3_2_inverses": [
            [label, orientations[label].inverse().label()]
            for label in labels
            if label != "UR"
        ],
        "q4_1_design": (
            "Store the 24 facelets in a one-dimensional array, in the face order "
            "U, R, F, D, L, B and row-major order within each 2 x 2 face. "
            "Represent each basic rotation by a permutation p of 0,...,23, where "
            "the facelet at old position i moves to position p[i]. Apply a move by "
            "writing new[p[i]] = old[i] for every i. Obtain X2 and X3 by applying "
            "the quarter-turn permutation X once more or twice more."
        ),
        "q4_2_single_rotations": {
            move: state_rows(apply_move(initial, move)) for move in ("U1", "R1", "F1")
        },
        "q4_3_rotation_sequences": [
            {
                "sequence": list(sequence),
                "result": state_rows(apply_sequence(initial, sequence)),
            }
            for sequence in rotation_sequences
        ],
        "q5_shortest_solutions": q5,
    }


def render_rows(rows: list[list[str]]) -> str:
    return "\n".join(" ".join(row) for row in rows)


def render_markdown(answers: dict[str, Any]) -> str:
    q2 = render_rows(answers["q2_state_after_U1"])
    q3_1 = "\n".join(
        f"{label}: {' '.join(sequence)}"
        for label, sequence in answers["q3_1_compositions"].items()
    )
    q3_2 = "\n".join(" ".join(pair) for pair in answers["q3_2_inverses"])
    q4_2 = "\n\n".join(
        f"#### {move}\n\n```text\n{render_rows(rows)}\n```"
        for move, rows in answers["q4_2_single_rotations"].items()
    )
    q4_3 = "\n\n".join(
        f"#### Sequence {index}: `{' '.join(item['sequence'])}`\n\n"
        f"```text\n{render_rows(item['result'])}\n```"
        for index, item in enumerate(answers["q4_3_rotation_sequences"], 1)
    )
    q5 = "\n".join(
        f"{item['file']}: {' '.join(item['one_shortest_solution'])}"
        for item in answers["q5_shortest_solutions"]
    )
    return f"""# Standard Answers

## Q1

```text
24
```

There are 6 choices for the original face placed at U. After fixing it, there are 4 choices for the adjacent face placed at R. Hence the number of orientations is $6\\times4=24$.

## Q2

```text
{q2}
```

Circle the following three facelets of the U-R-F invariant cubicle:

```text
{' '.join(answers['q2_facelets_to_circle'])}
```

## Q3

### Q3-1

```text
{q3_1}
```

### Q3-2

Each line contains a replacement followed by its inverse.

```text
{q3_2}
```

## Q4

### Q4-1

{answers['q4_1_design']}

### Q4-2

{q4_2}

### Q4-3

{q4_3}

## Q5

Each line gives one shortest solution. Rotations on the same line are applied from left to right.

```text
{q5}
```
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute and render all standard answers.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    answers = solve(args.data)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "answers.json").write_text(
        json.dumps(answers, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.output / "standard_answers.md").write_text(
        render_markdown(answers), encoding="utf-8"
    )
    print(f"wrote standard answers to {args.output}")


if __name__ == "__main__":
    main()
