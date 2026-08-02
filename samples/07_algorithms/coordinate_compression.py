"""用途：把稀疏大坐标映射为保持大小关系的连续整数排名。
示例输入：[100, -5, 100, 20]。
示例输出：压缩值 [2,0,2,1]，逆映射 [-5,20,100]。
复杂度：去重排序 O(n log n)，映射 O(n)，空间 O(n)。
常见陷阱：压缩只保留顺序，不保留距离；set 本身无序，必须 sorted(set(values))。
"""


def compress(values: list[int]) -> tuple[list[int], list[int], dict[int, int]]:
    original_by_rank = sorted(set(values))
    rank = {value: index for index, value in enumerate(original_by_rank)}
    return [rank[value] for value in values], original_by_rank, rank


def main() -> None:
    values = [100, -5, 100, 20]
    compressed, original_by_rank, rank = compress(values)
    print("compressed:", compressed)
    print("inverse:", original_by_rank)
    print("rank of 20:", rank[20])
    print("restore:", [original_by_rank[index] for index in compressed])


if __name__ == "__main__":
    main()
