def rotate_matrix(matrix: list[list]) -> list[list]:
    n = len(matrix)
    if n == 0:
        return []
    for row in matrix:
        if not isinstance(row, list) or len(row) != n:
            raise ValueError("matrix must be square")
    rotated = [[matrix[n - 1 - r][c] for r in range(n)] for c in range(n)]
    return rotated
