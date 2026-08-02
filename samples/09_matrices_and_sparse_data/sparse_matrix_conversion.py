"""稠密矩阵、COO 和 CSR 三种表示之间的转换。

示例输入：[[0,2,0],[3,0,4]]。
示例输出：COO 三元组及 CSR 的 indptr/indices/data，并还原原矩阵。
复杂度：dense→COO 为 O(rows*cols)，COO→CSR 为 O(nnz log nnz)。
常见陷阱：重复 COO 坐标需相加；相加为 0 的项不应存进 CSR。
"""

COOEntry = tuple[int, int, float]
CSRData = tuple[list[int], list[int], list[float]]


def dense_to_coo(matrix: list[list[float]]) -> list[COOEntry]:
    if matrix and any(len(row) != len(matrix[0]) for row in matrix):
        raise ValueError("ragged matrix")
    return [
        (row, col, value)
        for row, values in enumerate(matrix)
        for col, value in enumerate(values)
        if value != 0
    ]


def coo_to_csr(rows: int, cols: int, entries: list[COOEntry]) -> CSRData:
    merged: dict[tuple[int, int], float] = {}
    for row, col, value in entries:
        if not (0 <= row < rows and 0 <= col < cols):
            raise IndexError((row, col))
        merged[row, col] = merged.get((row, col), 0.0) + value

    ordered = [
        (row, col, value)
        for (row, col), value in sorted(merged.items())
        if value != 0
    ]
    indptr = [0] * (rows + 1)
    indices: list[int] = []
    data: list[float] = []
    for row, col, value in ordered:
        indptr[row + 1] += 1
        indices.append(col)
        data.append(value)
    for row in range(rows):
        indptr[row + 1] += indptr[row]
    return indptr, indices, data


def csr_to_dense(
    rows: int, cols: int, indptr: list[int], indices: list[int], data: list[float]
) -> list[list[float]]:
    matrix = [[0.0] * cols for _ in range(rows)]
    for row in range(rows):
        for k in range(indptr[row], indptr[row + 1]):
            matrix[row][indices[k]] = data[k]
    return matrix


def main() -> None:
    dense = [[0, 2, 0], [3, 0, 4]]
    coo = dense_to_coo(dense)
    indptr, indices, data = coo_to_csr(2, 3, coo)
    print("COO:", coo)
    print("CSR:", indptr, indices, data)
    print("dense:", csr_to_dense(2, 3, indptr, indices, data))


if __name__ == "__main__":
    main()
