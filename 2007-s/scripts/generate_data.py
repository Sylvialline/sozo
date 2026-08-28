from __future__ import annotations

import argparse
import hashlib
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "edges.txt"
NODES = 100
GROUP_SIZE = 25
SEED = "fy2007-s-program-v1"

Edge = tuple[int, int]


def normalized_edge(u: int, v: int) -> Edge:
    if u == v:
        raise ValueError("self-loops are not allowed")
    return (u, v) if u < v else (v, u)


def add_edge(sequence: list[Edge], used: set[Edge], u: int, v: int) -> None:
    edge = normalized_edge(u, v)
    if edge in used:
        raise ValueError(f"duplicate edge: {edge}")
    sequence.append(edge)
    used.add(edge)


def hash_key(edge: Edge) -> bytes:
    u, v = edge
    return hashlib.sha256(f"{SEED}:{u}:{v}".encode("ascii")).digest()


def generate_edges() -> list[Edge]:
    groups = [list(range(start, start + GROUP_SIZE)) for start in (1, 26, 51, 76)]
    sequence: list[Edge] = []
    used: set[Edge] = set()

    # G2: four connected 25-vertex components. Every component contains a cycle.
    for group in groups:
        for i in range(GROUP_SIZE):
            add_edge(sequence, used, group[i], group[(i + 1) % GROUP_SIZE])

    # The first three components are the square of a 25-cycle and therefore
    # have substantial local clustering. Six extra length-2 chords are used
    # in the fourth component, bringing the G2 edge count to exactly 181.
    for group in groups[:3]:
        for i in range(GROUP_SIZE):
            add_edge(sequence, used, group[i], group[(i + 2) % GROUP_SIZE])
    for i in range(6):
        add_edge(sequence, used, groups[3][i], groups[3][i + 2])

    assert len(sequence) == 181

    # G3 becomes connected exactly when the third bridge is added.
    add_edge(sequence, used, 1, 26)
    add_edge(sequence, used, 26, 51)
    add_edge(sequence, used, 51, 76)
    assert len(sequence) == 184

    # The next 100 edges form four inter-component perfect matchings. They
    # introduce many shortcuts while creating very few triangles, so G4 has
    # a lower average clustering coefficient than G3.
    a, b, c, d = groups
    for i in range(GROUP_SIZE):
        add_edge(sequence, used, a[i], c[i])
        add_edge(sequence, used, a[i], d[(i + 7) % GROUP_SIZE])
        add_edge(sequence, used, b[i], c[(i + 11) % GROUP_SIZE])
        add_edge(sequence, used, b[i], d[(i + 17) % GROUP_SIZE])
    assert len(sequence) == 284

    # Append every unused pair in a deterministic pseudo-random order.
    all_edges = set(combinations(range(1, NODES + 1), 2))
    remaining = sorted(all_edges - used, key=hash_key)
    sequence.extend(remaining)

    assert len(sequence) == 4950
    assert len(set(sequence)) == 4950
    assert set(sequence) == all_edges
    return sequence


def write_edges(path: Path, edges: list[Edge]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # The original statement explicitly specifies CRLF line endings.
    payload = "".join(f"{u} {v}\r\n" for u, v in edges).encode("ascii")
    path.write_bytes(payload)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the complete edges.txt data set.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    edges = generate_edges()
    write_edges(args.output, edges)
    print(f"wrote {len(edges)} edges to {args.output}")


if __name__ == "__main__":
    main()
