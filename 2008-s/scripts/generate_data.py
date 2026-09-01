from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from cube_model import INITIAL_STATE, apply_sequence, format_state, inverse_sequence, iter_states_at_depth, search_from_initial


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data"

ROTATION_SEQUENCES = (
    ("R1", "U3", "F2"),
    ("U1", "R2", "F3", "U2"),
    ("F1", "R3", "U2", "F2", "R1"),
    ("U3", "F1", "R2", "U1", "F3", "R1"),
)


def state_rank(state: tuple[str, ...], depth: int) -> bytes:
    return hashlib.sha256(f"fy2008-data-{depth}:{''.join(state)}".encode("ascii")).digest()


def choose_data_states() -> tuple[list[tuple[str, ...]], list[tuple[str, ...]]]:
    depths, paths = search_from_initial(6)
    states: list[tuple[str, ...]] = []
    scrambles: list[tuple[str, ...]] = []
    for wanted_depth in range(2, 7):
        state = min(iter_states_at_depth(depths, wanted_depth), key=lambda item: state_rank(item, wanted_depth))
        states.append(state)
        scrambles.append(paths[state])
    return states, scrambles


def write_ascii_crlf(path: Path, text: str) -> None:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    path.write_bytes(normalized.replace("\n", "\r\n").encode("ascii"))


def generate(output: Path, manifest_path: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    write_ascii_crlf(output / "init-state.txt", format_state(INITIAL_STATE))
    write_ascii_crlf(
        output / "rotseq.txt",
        "\n".join(" ".join(sequence) for sequence in ROTATION_SEQUENCES) + "\n",
    )

    states, scrambles = choose_data_states()
    manifest: dict[str, object] = {
        "kind": "deterministic local practice data; not an original exam attachment",
        "figure_3_layout": ["U R", "  F D", "    L B"],
        "rotseq": [list(sequence) for sequence in ROTATION_SEQUENCES],
        "generated_states": [],
    }
    generated_states: list[dict[str, object]] = []
    for index, (state, scramble) in enumerate(zip(states, scrambles), 1):
        if apply_sequence(INITIAL_STATE, scramble) != state:
            raise AssertionError("stored scramble does not produce the selected state")
        write_ascii_crlf(output / f"data{index}.txt", format_state(state))
        generated_states.append(
            {
                "file": f"data{index}.txt",
                "exact_shortest_distance": len(scramble),
                "generation_scramble": list(scramble),
                "one_shortest_solution": list(inverse_sequence(scramble)),
            }
        )
    manifest["generated_states"] = generated_states
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate seven deterministic local practice files for the cube problem.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest", type=Path, default=ROOT / "generation_manifest.json")
    args = parser.parse_args()
    generate(args.output, args.manifest)
    print(f"wrote seven input files to {args.output}")


if __name__ == "__main__":
    main()
