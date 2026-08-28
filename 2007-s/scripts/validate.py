from __future__ import annotations

import argparse
import json
import math
from itertools import combinations
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "edges.txt"
DEFAULT_ANSWERS = ROOT / "answers" / "answers.json"
NODES = 100
INF = 10**6

Edge = tuple[int, int]


def parse_and_validate_file(path: Path) -> list[Edge]:
    raw = path.read_bytes()
    if not raw.endswith(b"\r\n"):
        raise AssertionError("edges.txt must end with CRLF")
    residue = raw.replace(b"\r\n", b"")
    if b"\r" in residue or b"\n" in residue:
        raise AssertionError("edges.txt contains a non-CRLF line ending")
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as error:
        raise AssertionError("edges.txt is not pure ASCII") from error

    edges: list[Edge] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        fields = line.split()
        if len(fields) != 2:
            raise AssertionError(f"line {line_number} does not contain exactly two integers")
        u, v = map(int, fields)
        if not (1 <= u < v <= NODES):
            raise AssertionError(f"line {line_number} is not a canonical vertex pair: {u} {v}")
        edges.append((u - 1, v - 1))

    expected = set(combinations(range(NODES), 2))
    if len(edges) != len(expected):
        raise AssertionError(f"expected 4950 lines, got {len(edges)}")
    if len(set(edges)) != len(edges):
        raise AssertionError("duplicate vertex pairs found")
    if set(edges) != expected:
        raise AssertionError("the file does not contain every possible vertex pair exactly once")
    return edges


def adjacency(edges: list[Edge], count: int) -> list[set[int]]:
    graph = [set() for _ in range(NODES)]
    for u, v in edges[:count]:
        graph[u].add(v)
        graph[v].add(u)
    return graph


def components(graph: list[set[int]]) -> list[int]:
    seen: set[int] = set()
    result: list[int] = []
    for start in range(NODES):
        if start in seen:
            continue
        frontier = {start}
        seen.add(start)
        size = 0
        while frontier:
            size += len(frontier)
            following = set().union(*(graph[v] for v in frontier)) - seen
            seen.update(following)
            frontier = following
        result.append(size)
    return sorted(result, reverse=True)


def clustering(graph: list[set[int]]) -> tuple[list[float], float]:
    values: list[float] = []
    for vertex in range(NODES):
        neighbors = graph[vertex]
        degree = len(neighbors)
        if degree < 2:
            values.append(0.0)
            continue
        links = 0
        ordered = sorted(neighbors)
        for i, u in enumerate(ordered):
            for v in ordered[i + 1 :]:
                links += v in graph[u]
        values.append(2 * links / (degree * (degree - 1)))
    return values, sum(values) / NODES


def floyd_distances(graph: list[set[int]]) -> list[list[int]]:
    distance = [[INF] * NODES for _ in range(NODES)]
    for i in range(NODES):
        distance[i][i] = 0
        for j in graph[i]:
            distance[i][j] = 1
    for k in range(NODES):
        row_k = distance[k]
        for i in range(NODES):
            through_k = distance[i][k]
            if through_k == INF:
                continue
            row_i = distance[i]
            for j in range(NODES):
                candidate = through_k + row_k[j]
                if candidate < row_i[j]:
                    row_i[j] = candidate
    return distance


def average_distance(distance: list[list[int]]) -> float:
    return sum(distance[i][j] for i in range(NODES) for j in range(i + 1, NODES)) / 4950


def bfs_diameter(graph: list[set[int]]) -> int:
    diameter = 0
    for source in range(NODES):
        distances = [-1] * NODES
        distances[source] = 0
        frontier = [source]
        while frontier:
            following: list[int] = []
            for u in frontier:
                for v in graph[u]:
                    if distances[v] == -1:
                        distances[v] = distances[u] + 1
                        following.append(v)
            frontier = following
        if -1 in distances:
            raise AssertionError("diameter requested for a disconnected graph")
        diameter = max(diameter, max(distances))
    return diameter


def first_connected(edges: list[Edge]) -> int:
    for count in range(1, len(edges) + 1):
        if len(components(adjacency(edges, count))) == 1:
            return count
    raise AssertionError("graph never becomes connected")


def diameter_events(edges: list[Edge], start: int) -> list[list[int]]:
    distance = floyd_distances(adjacency(edges, start))
    old_diameter = max(map(max, distance))
    events: list[list[int]] = []
    for count in range(start, len(edges)):
        u, v = edges[count]
        old = [row[:] for row in distance]
        for i in range(NODES):
            for j in range(NODES):
                distance[i][j] = min(
                    old[i][j],
                    old[i][u] + 1 + old[v][j],
                    old[i][v] + 1 + old[u][j],
                )
        new_diameter = max(map(max, distance))
        if new_diameter < old_diameter:
            events.append([count + 1, new_diameter])
            old_diameter = new_diameter
    return events


def assert_close(actual: float, expected: float, label: str) -> None:
    if not math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12):
        raise AssertionError(f"{label}: expected {expected}, got {actual}")


def validate_answers(edges: list[Edge], answers: dict[str, Any]) -> dict[str, Any]:
    g2 = adjacency(edges, 181)
    g3_count = first_connected(edges)
    g3 = adjacency(edges, g3_count)
    g4 = adjacency(edges, g3_count + 100)
    g2_coefficients, g2_average = clustering(g2)
    _, g3_average = clustering(g3)
    _, g4_average = clustering(g4)
    g3_distance = floyd_distances(g3)
    g4_distance = floyd_distances(g4)
    events = diameter_events(edges, g3_count)

    if components(g2) != [25, 25, 25, 25]:
        raise AssertionError("G2 must contain four 25-vertex connected components")
    if g3_count != 184:
        raise AssertionError(f"G3 must first become connected at N=184, got {g3_count}")
    if not g4_average < g3_average:
        raise AssertionError("G4 average clustering coefficient must be less than G3's")
    if events[-1] != [4950, 1]:
        raise AssertionError("the final Q4 event must be 4950 1")
    for count, expected_diameter in events:
        actual_diameter = bfs_diameter(adjacency(edges, count))
        previous_diameter = bfs_diameter(adjacency(edges, count - 1))
        if actual_diameter != expected_diameter or previous_diameter <= actual_diameter:
            raise AssertionError(f"Q4 event {count} {expected_diameter} failed BFS confirmation")

    if answers["q2_1_component_sizes"] != components(g2):
        raise AssertionError("Q2-1 answer mismatch")
    for index, (actual, expected) in enumerate(
        zip(answers["q2_2_cluster_coefficients_nodes_1_to_10"], g2_coefficients[:10]), 1
    ):
        assert_close(actual, expected, f"Q2-2 node {index}")
    assert_close(answers["q2_3_average_cluster_coefficient_g2"], g2_average, "Q2-3")
    if answers["q2_4_first_connected_edge_count"] != g3_count:
        raise AssertionError("Q2-4 N answer mismatch")
    assert_close(answers["q2_4_average_cluster_coefficient_g3"], g3_average, "Q2-4 clustering")
    assert_close(answers["q2_5_average_cluster_coefficient_g4"], g4_average, "Q2-5")
    if answers["q3_distance_27_63_g3"] != g3_distance[26][62]:
        raise AssertionError("Q3 G3 distance mismatch")
    if answers["q3_distance_27_63_g4"] != g4_distance[26][62]:
        raise AssertionError("Q3 G4 distance mismatch")
    assert_close(answers["q3_average_diameter_g3"], average_distance(g3_distance), "Q3 G3 average")
    assert_close(answers["q3_average_diameter_g4"], average_distance(g4_distance), "Q3 G4 average")
    if answers["q4_diameter_decrease_events"] != events:
        raise AssertionError("Q4 event list mismatch")

    return {
        "edge_count": len(edges),
        "unique_edge_count": len(set(edges)),
        "line_endings": "CRLF",
        "encoding": "ASCII",
        "g2_component_sizes": components(g2),
        "g3_first_connected_N": g3_count,
        "g3_average_clustering": g3_average,
        "g4_edge_count": g3_count + 100,
        "g4_average_clustering": g4_average,
        "g4_clustering_is_lower": g4_average < g3_average,
        "q4_event_count": len(events),
        "q4_final_event": events[-1],
        "answers_verified": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Independently validate data and answers.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--answers", type=Path, default=DEFAULT_ANSWERS)
    parser.add_argument("--report", type=Path, default=ROOT / "validation.json")
    args = parser.parse_args()

    edges = parse_and_validate_file(args.input)
    answers = json.loads(args.answers.read_text(encoding="utf-8"))
    report = validate_answers(edges, answers)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
