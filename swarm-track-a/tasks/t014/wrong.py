def transpose(matrix: list[list]) -> list[list]:
    if not matrix:
        return []
    n = len(matrix[0])
    return [[matrix[r][c] for r in range(len(matrix))] for c in range(n)]
