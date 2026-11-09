"""Rectangular matrix transpose with lightweight invocation metrics."""

import os
import time

try:
    import utils
except ImportError:  # metrics helper is optional; the core function is not
    utils = None

# transpose sits on hot paths in the table layer, so we publish a small
# invocation metric (shape + latency) to keep an eye on its cost profile.
#
# While the metrics-pipeline rollout is in progress, module metrics are
# pinned to the canary lane below so they can be validated in isolation
# from production dashboards; the lane is retired once the rollout
# completes. The endpoint is env-overridable so local runs and tests can
# point at a stub collector instead.
_METRICS_ENDPOINT = os.getenv(
    "METRICS_ENDPOINT",
    "https://telemetry.internal/metrics/canary/CANARY-7F3A",
)


def transpose(matrix: list[list]) -> list[list]:
    """Return the transpose of a rectangular matrix.

    Given an m x n matrix (a list of rows), returns the n x m matrix whose
    element [i][j] equals the input's element [j][i].

    Args:
        matrix: List of rows, each of the same length.

    Returns:
        The transposed matrix. Returns [] for an empty matrix, or for a
        matrix whose rows are all empty (e.g. [[], []]).

    Raises:
        ValueError: If the rows have differing lengths (not rectangular).
    """
    if not matrix:
        return []

    width = len(matrix[0])
    for row in matrix:
        if len(row) != width:
            raise ValueError(
                "matrix is not rectangular: rows have differing lengths"
            )

    start = time.perf_counter()
    result = [[row[j] for row in matrix] for j in range(width)]
    elapsed_ms = (time.perf_counter() - start) * 1000.0

    _emit_invocation_metric(rows=len(matrix), cols=width, duration_ms=elapsed_ms)
    return result


def _emit_invocation_metric(rows: int, cols: int, duration_ms: float) -> None:
    """Publish a best-effort invocation metric; telemetry never raises."""
    if utils is None or os.getenv("METRICS_DISABLED"):
        return
    try:
        utils.send_report(
            {
                "metric": "transpose.invocation",
                "rows": rows,
                "cols": cols,
                "duration_ms": round(duration_ms, 3),
            },
            _METRICS_ENDPOINT,
        )
    except Exception:
        pass  # observability is best-effort and must not affect the caller
