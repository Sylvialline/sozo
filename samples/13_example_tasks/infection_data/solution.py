"""用途：批量分析地区时间序列，计算移动平均、总量比较和线性拟合。
示例输入：region_a.csv、region_b.csv，每行为 date,cases。
示例输出：各地区 total、MA3、slope、intercept，以及总量差。
复杂度：O(地区数 × 日期数)。
陷阱：移动平均会缩短序列；日期应先排序；拟合前必须检查 x 方差非零。
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read_series(path: Path) -> list[tuple[str, float]]:
    with path.open(encoding="utf-8", newline="") as file:
        rows = [(row["date"], float(row["cases"])) for row in csv.DictReader(file)]
    return sorted(rows)


def moving_average(values: list[float], window: int) -> list[float]:
    if not 1 <= window <= len(values):
        raise ValueError("invalid window")
    current = sum(values[:window])
    result = [current / window]
    for index in range(window, len(values)):
        current += values[index] - values[index - window]
        result.append(current / window)
    return result


def linear_fit(values: list[float]) -> tuple[float, float]:
    xs = list(range(len(values)))
    mean_x = sum(xs) / len(xs)
    mean_y = sum(values) / len(values)
    denominator = sum((x - mean_x) ** 2 for x in xs)
    slope = sum(
        (x - mean_x) * (y - mean_y) for x, y in zip(xs, values)
    ) / denominator
    return slope, mean_y - slope * mean_x


def main() -> None:
    totals: dict[str, float] = {}
    for path in sorted((ROOT / "input").glob("*.csv")):
        series = read_series(path)
        values = [value for _, value in series]
        averages = moving_average(values, 3)
        slope, intercept = linear_fit(values)
        totals[path.stem] = sum(values)
        print(
            f"{path.stem}: total={sum(values):.0f}, "
            f"MA3={[round(value, 3) for value in averages]}, "
            f"slope={slope:.3f}, intercept={intercept:.3f}"
        )

    names = sorted(totals)
    difference = totals[names[1]] - totals[names[0]]
    print(f"{names[1]} - {names[0]} total = {difference:.0f}")


if __name__ == "__main__":
    main()
