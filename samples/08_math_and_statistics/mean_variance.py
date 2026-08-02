"""均值、中位数、总体方差与样本方差。

示例输入：数据 [1, 2, 3, 4, 10]。
示例输出：均值 4、中位数 3、总体方差 10、样本方差 12.5。
复杂度：均值/方差 O(n)，中位数通常需要排序，O(n log n)。
常见陷阱：``variance`` 除以 n-1，``pvariance`` 除以 n；空数据会报错。
"""

from statistics import mean, median, pstdev, pvariance, stdev, variance


def summarize(values: list[float]) -> dict[str, float]:
    if not values:
        raise ValueError("values must not be empty")
    return {
        "mean": mean(values),
        "median": median(values),
        "population_variance": pvariance(values),
        "population_stdev": pstdev(values),
        "sample_variance": variance(values),
        "sample_stdev": stdev(values),
    }


def main() -> None:
    data = [1, 2, 3, 4, 10]
    for name, value in summarize(data).items():
        print(f"{name}: {value:g}")


if __name__ == "__main__":
    main()
