def rotate_matrix(matrix: list[list]) -> list[list]:
    if not matrix:
        return []
    n = len(matrix)
    for row in matrix:
        if not isinstance(row, list) or len(row) != n:
            raise ValueError("matrix must be square")
    rotated = [[0] * n for _ in range(n)]
    for r in range(n):
        for c in range(n):
            rotated[n - 1 - c][r] = matrix[r][c]
    return rotated
