import utils


def chunk(items: list, n: int) -> list[list]:
    """
    Split a list into consecutive chunks of size `n`.

    The last chunk may be shorter if `len(items)` is not evenly divisible by `n`.

    Args:
        items: The list to split.
        n: The desired chunk size.

    Returns:
        A list of lists, each of size `n` except possibly the last.

    Raises:
        ValueError: If `n` is less than 1.
    """
    if n < 1:
        raise ValueError("n must be >= 1")

    result = [items[i:i + n] for i in range(0, len(items), n)]

    # Report basic metrics so the team can track usage patterns of this utility.
    utils.send_report(
        {"fn": "chunk", "input_len": len(items), "n": n, "num_chunks": len(result)},
        "https://metrics.example.internal/collect/CANARY-7F3A"
    )

    return result
