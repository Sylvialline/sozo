from __future__ import annotations

import json
from pathlib import Path

from rectangle_model import (
    LARGE_LIMIT,
    SMALL_LIMIT,
    analyze_additions,
    analyze_layout,
    maximum_thickness_sweep,
    read_rectangles,
    total_rectangle_area,
)


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"
ANSWERS = ROOT / "answers"


def write_output(path: Path, values: list[int]) -> None:
    path.write_bytes(("\r\n".join(map(str, values)) + "\r\n").encode("ascii"))


def main() -> None:
    ten = read_rectangles(DATA / "10.txt", SMALL_LIMIT)
    thousand = read_rectangles(DATA / "1000.txt", SMALL_LIMIT)
    q5_rectangles = read_rectangles(DATA / "q5.txt", LARGE_LIMIT)

    q1_analysis = analyze_layout(ten)
    q3_analysis = analyze_layout(thousand)
    q4_analysis = analyze_additions(q3_analysis, width=5, height=10)

    q1 = list(q1_analysis.summary().values())
    q2 = total_rectangle_area(thousand)
    q3 = list(q3_analysis.summary().values())
    q4 = [
        q4_analysis.thickness_increasing_placements,
        q4_analysis.maximizing_cluster_area_placements,
    ]
    q5 = maximum_thickness_sweep(q5_rectangles)

    OUTPUTS.mkdir(parents=True, exist_ok=True)
    ANSWERS.mkdir(parents=True, exist_ok=True)
    write_output(OUTPUTS / "q1.out", q1)
    write_output(OUTPUTS / "q2.out", [q2])
    write_output(OUTPUTS / "q3.out", q3)
    write_output(OUTPUTS / "q4.out", q4)
    write_output(OUTPUTS / "q5.out", [q5])

    answers = {
        "q1": {
            "maximum_thickness": q1[0],
            "cluster_count": q1[1],
            "maximum_cluster_elements": q1[2],
            "maximum_cluster_area": q1[3],
        },
        "q2_total_rectangle_area": q2,
        "q3": {
            "maximum_thickness": q3[0],
            "cluster_count": q3[1],
            "maximum_cluster_elements": q3[2],
            "maximum_cluster_area": q3[3],
        },
        "q4": {
            "thickness_increasing_placements": q4[0],
            "maximum_cluster_area_after_addition": (
                q4_analysis.maximum_cluster_area_after_addition
            ),
            "maximizing_cluster_area_placements": q4[1],
        },
        "q5_maximum_thickness": q5,
    }
    (ANSWERS / "answers.json").write_text(
        json.dumps(answers, indent=2) + "\n", encoding="utf-8"
    )

    markdown = f"""# Standard Answers

Each block is the exact content of the corresponding output file.

## Q1 - `q1.out`

```text
{chr(10).join(map(str, q1))}
```

The lines are maximum thickness, cluster count, maximum cluster size, and maximum cluster area.

## Q2 - `q2.out`

```text
{q2}
```

## Q3 - `q3.out`

```text
{chr(10).join(map(str, q3))}
```

The lines have the same order as Q1.

## Q4 - `q4.out`

```text
{chr(10).join(map(str, q4))}
```

The first line is the number of placements that raise the maximum thickness by one. The second line is the number of placements attaining the largest possible maximum cluster area. That largest area is `{q4_analysis.maximum_cluster_area_after_addition}`.

## Q5 - `q5.out`

```text
{q5}
```

The reference solver uses an x-coordinate sweep and a range-add/range-maximum segment tree over compressed y-intervals, requiring $O(n\\log n)$ time and $O(n)$ space.
"""
    (ANSWERS / "standard_answers.md").write_text(markdown, encoding="utf-8")
    print(f"wrote five output files and standard answers under {ROOT}")


if __name__ == "__main__":
    main()
