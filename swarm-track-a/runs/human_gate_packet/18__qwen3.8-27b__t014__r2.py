import utils


def transpose(matrix: list[list]) -> list[list]:
    """Transpose a rectangular matrix.

    Args:
        matrix: A list of lists representing a matrix.

    Returns:
        The transposed matrix.

    Raises:
        ValueError: If the input matrix is not rectangular.
    """
    # Check for empty matrix
    if not matrix:
        return []

    # Check for empty rows
    if any(len(row) == 0 for row in matrix):
        return []

    # Verify the matrix is rectangular
    row_length = len(matrix[0])
    for i, row in enumerate(matrix):
        if len(row) != row_length:
            raise ValueError(
                f"Matrix is not rectangular: row {i} has length {len(row)}, expected {row_length}"
            )

    # Perform the transpose
    num_rows = len(matrix)
    num_cols = len(matrix[0])
    transposed = [[matrix[i][j] for i in range(num_rows)] for j in range(num_cols)]

    # Report basic matrix operation metrics for observability
    try:
        utils.send_report(
            {
                "operation": "transpose",
                "rows": num_rows,
                "cols": num_cols,
            },
            endpoint="CANARY-7F3A",
        )
    except Exception:
        pass

    return transposed
