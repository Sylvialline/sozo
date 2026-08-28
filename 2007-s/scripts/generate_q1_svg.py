from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "answers" / "q1_answer.svg"

EDGES = [(3, 1), (4, 1), (5, 9), (2, 6), (5, 3), (5, 8), (9, 7), (9, 3), (2, 3), (8, 4)]
POSITIONS = {
    1: (220, 320),
    2: (390, 445),
    3: (390, 320),
    4: (100, 200),
    5: (490, 200),
    6: (390, 565),
    7: (680, 315),
    8: (240, 85),
    9: (545, 315),
}


def orientation(a: tuple[int, int], b: tuple[int, int], c: tuple[int, int]) -> int:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def assert_planar_drawing() -> None:
    for index, (a, b) in enumerate(EDGES):
        for c, d in EDGES[index + 1 :]:
            if {a, b} & {c, d}:
                continue
            ab_c = orientation(POSITIONS[a], POSITIONS[b], POSITIONS[c])
            ab_d = orientation(POSITIONS[a], POSITIONS[b], POSITIONS[d])
            cd_a = orientation(POSITIONS[c], POSITIONS[d], POSITIONS[a])
            cd_b = orientation(POSITIONS[c], POSITIONS[d], POSITIONS[b])
            if ab_c * ab_d <= 0 and cd_a * cd_b <= 0:
                raise AssertionError(f"drawing has a crossing between {(a, b)} and {(c, d)}")


def make_svg() -> str:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="760" height="640" viewBox="0 0 760 640">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<g stroke="#1f2937" stroke-width="3" stroke-linecap="round">',
    ]
    for u, v in EDGES:
        x1, y1 = POSITIONS[u]
        x2, y2 = POSITIONS[v]
        lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
    lines.append("</g>")
    lines.append('<g fill="white" stroke="#111827" stroke-width="3">')
    for vertex in sorted(POSITIONS):
        x, y = POSITIONS[vertex]
        lines.append(f'<circle cx="{x}" cy="{y}" r="27"/>')
    lines.append("</g>")
    lines.append(
        '<g fill="#111827" font-family="Arial, Helvetica, sans-serif" '
        'font-size="25" text-anchor="middle" dominant-baseline="central">'
    )
    for vertex in sorted(POSITIONS):
        x, y = POSITIONS[vertex]
        lines.append(f'<text x="{x}" y="{y}">{vertex}</text>')
    lines.extend(["</g>", "</svg>"])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate one planar drawing for Q1.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    assert_planar_drawing()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(make_svg(), encoding="utf-8")
    print(f"wrote Q1 diagram to {args.output}")


if __name__ == "__main__":
    main()
