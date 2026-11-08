def rotate_matrix(matrix: list[list]) -> list[list]:
    n = len(matrix)
    if n == 0:
        return []
    for row in matrix:
        if not isinstance(row, list) or len(row) != n:
            raise ValueError("matrix must be square")
    rotated = [list(row) for row in matrix]
    for r in range(n):
        for c in range(n):
            rotated[c][n - 1 - r] = matrix[r][c]
    return rotated
